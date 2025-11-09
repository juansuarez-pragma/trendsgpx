# Tasks: Sistema de Análisis de Tendencias en Redes Sociales

**Feature**: 001-social-trends-analysis
**Created**: 2025-11-08
**Status**: Ready for Implementation
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md) | **Data Model**: [data-model.md](./data-model.md)

---

## Phase 1: Setup del Proyecto

**Objetivo**: Configurar estructura básica del proyecto y dependencias

- [ ] T001 Crear estructura de directorios backend/src con subdirectorios: models/, collectors/, nlp/, services/, api/, tasks/, utils/
- [ ] T002 Crear estructura de directorios backend/tests con subdirectorios: contract/, integration/, unit/
- [ ] T003 Crear archivo backend/pyproject.toml con dependencias: FastAPI, Celery, Redis, PostgreSQL, SQLAlchemy, Alembic, spaCy, Transformers, BERTopic, pysentimiento, google-api-python-client, PRAW, Mastodon.py, pytrends, pytest
- [ ] T004 Crear archivo backend/docker-compose.yml con servicios: PostgreSQL 15 + TimescaleDB, Redis, Celery worker, Celery beat
- [ ] T005 Crear archivo backend/.env.example con variables de entorno: DATABASE_URL, REDIS_URL, API keys (YOUTUBE_API_KEY, REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, MASTODON_ACCESS_TOKEN)
- [ ] T006 Crear archivo backend/README.md con instrucciones de setup inicial
- [ ] T007 Crear archivo backend/alembic.ini para configuración de migraciones
- [ ] T008 Crear archivo backend/src/__init__.py (vacío)

---

## Phase 2: Foundational - Database & Infrastructure

**Objetivo**: Configurar base de datos, migraciones, logging y autenticación básica

- [ ] T009 Crear archivo backend/src/models/__init__.py exportando todos los modelos
- [ ] T010 Crear archivo backend/src/models/base.py con configuración base de SQLAlchemy (Base, engine, SessionLocal)
- [ ] T011 Crear migración backend/alembic/versions/001_initial_schema.py: habilitar extensiones TimescaleDB y pg_trgm
- [ ] T012 Crear migración backend/alembic/versions/002_create_lineamientos.py: tabla lineamientos con campos (id, nombre, descripcion, keywords JSONB, plataformas JSONB, activo, created_at, updated_at, created_by), constraints (nombre UNIQUE, keywords_not_empty, plataformas_not_empty), índices (activo, keywords GIN)
- [ ] T013 Crear migración backend/alembic/versions/003_create_contenido.py: tabla contenido_recolectado con campos (id, lineamiento_id FK, plataforma, plataforma_id, contenido_texto, titulo, autor, url, metadata JSONB, fecha_publicacion, fecha_recoleccion, idioma, nlp_procesado, nlp_procesado_at), constraints (plataforma_id_unique, plataforma_valid, texto_not_empty), índices (lineamiento_id, plataforma, fecha_publicacion DESC, fecha_recoleccion DESC, nlp_pending, texto_search GIN)
- [ ] T014 Crear migración backend/alembic/versions/004_create_temas.py: tabla temas_identificados con campos (id, contenido_id FK, tema_nombre, relevancia_score, keywords TEXT[], sentimiento, sentimiento_score, entidades_mencionadas JSONB, modelo_version, identificado_at), constraints (relevancia_score BETWEEN 0 AND 1, sentimiento_score BETWEEN -1 AND 1, sentimiento_valid), índices (contenido_id, tema_nombre, relevancia_score DESC, identificado_at DESC, keywords GIN)
- [ ] T015 Crear migración backend/alembic/versions/005_create_demografia.py: tabla demografia con campos (id, tema_id FK, plataforma, ubicacion_pais, ubicacion_ciudad, edad_rango, genero, conteo_menciones, confianza_score, metodo_inferencia, calculado_at), constraints (plataforma_valid, edad_valid, genero_valid, unique_segment), índices (tema_id, plataforma, ubicacion compuesto, edad_rango, genero, confianza_score DESC, hierarchy compuesto)
- [ ] T016 Crear migración backend/alembic/versions/006_create_tendencias.py: tabla tendencias con campos (id, tema_id FK, fecha_hora, volumen_menciones, tasa_crecimiento, plataforma, ubicacion, edad_rango, genero, es_tendencia, alerta_enviada), constraint (volumen_positive), PRIMARY KEY compuesta (fecha_hora, tema_id, plataforma, ubicacion, edad_rango, genero)
- [ ] T017 Crear migración backend/alembic/versions/007_create_hypertable.py: convertir tabla tendencias a hypertable TimescaleDB con chunks de 7 días, crear política de retención de 7 días
- [ ] T018 Crear migración backend/alembic/versions/008_create_aggregates.py: crear vistas materializadas tendencias_por_hora (agregación 1 hora) y tendencias_por_dia (agregación 1 día) con políticas de actualización continua
- [ ] T019 Crear migración backend/alembic/versions/009_create_validacion.py: tabla validacion_tendencias con campos (id, tendencia_id FK, tema_nombre, fuente_validacion, google_trends_data JSONB, indice_coincidencia, validada, en_google_trends, solo_en_plataforma, validado_at), constraints (indice_coincidencia BETWEEN 0 AND 1, fuente_valid), índices (tendencia_id, validada, validado_at DESC, gap)
- [ ] T020 Crear migración backend/alembic/versions/010_create_cleanup_function.py: función PL/pgSQL cleanup_old_data() para eliminar datos con más de 7 días de contenido_recolectado, temas_identificados huérfanos, demografia huérfana, validacion_tendencias huérfanas
- [ ] T021 [P] Crear archivo backend/src/models/lineamiento.py con modelo SQLAlchemy Lineamiento mapeando tabla lineamientos
- [ ] T022 [P] Crear archivo backend/src/models/contenido.py con modelo SQLAlchemy ContenidoRecolectado mapeando tabla contenido_recolectado
- [ ] T023 [P] Crear archivo backend/src/models/tema.py con modelo SQLAlchemy TemaIdentificado mapeando tabla temas_identificados
- [ ] T024 [P] Crear archivo backend/src/models/demografia.py con modelo SQLAlchemy Demografia mapeando tabla demografia
- [ ] T025 [P] Crear archivo backend/src/models/tendencia.py con modelo SQLAlchemy Tendencia mapeando tabla tendencias
- [ ] T026 [P] Crear archivo backend/src/models/validacion.py con modelo SQLAlchemy ValidacionTendencia mapeando tabla validacion_tendencias
- [ ] T027 Crear archivo backend/src/utils/logging.py con configuración de logging estructurado (formato JSON, niveles por módulo, rotación de archivos)
- [ ] T028 Crear archivo backend/src/utils/config.py para cargar variables de entorno (.env) usando pydantic BaseSettings
- [ ] T029 Crear archivo backend/src/api/auth.py con middleware de autenticación por API key estática (leer de variables de entorno, validar header X-API-Key)
- [ ] T030 Crear archivo backend/src/api/main.py con app FastAPI básica, configurar CORS, incluir middleware de autenticación, agregar endpoint GET /health para healthcheck

---

## Phase 3: US1 - Configurar Lineamientos (P1 - MVP)

**User Story**: Un analista de marketing necesita configurar áreas temáticas específicas (lineamientos) para monitorear conversaciones en redes sociales

**Acceptance Criteria**: FR-001, FR-002

- [ ] T031 Crear archivo backend/src/services/lineamientos.py con clase LineamientosService implementando métodos: crear_lineamiento(), obtener_lineamiento(id), listar_lineamientos(), actualizar_lineamiento(id), eliminar_lineamiento(id)
- [ ] T032 Crear archivo backend/src/api/lineamientos.py con rutas FastAPI: POST /lineamientos (crear), GET /lineamientos (listar), GET /lineamientos/{id} (obtener), PUT /lineamientos/{id} (actualizar), DELETE /lineamientos/{id} (eliminar)
- [ ] T033 Agregar validaciones en backend/src/api/lineamientos.py usando Pydantic schemas: LineamientoCreate (nombre required, keywords list required mínimo 1, plataformas list required valores válidos ["youtube", "reddit", "mastodon"]), LineamientoUpdate, LineamientoResponse
- [ ] T034 Agregar manejo de errores en backend/src/api/lineamientos.py: 400 para validación fallida, 404 para lineamiento no encontrado, 409 para nombre duplicado
- [ ] T035 Registrar router de lineamientos en backend/src/api/main.py con prefix /api/v1

---

## Phase 4: US2 - Recolectar Contenido (P1 - MVP)

**User Story**: El sistema debe automáticamente recolectar contenido público relacionado a los lineamientos configurados desde plataformas de redes sociales

**Acceptance Criteria**: FR-003, FR-004, FR-005, FR-006

- [ ] T036 Crear archivo backend/src/utils/rate_limit.py con clase RateLimiter usando PyrateLimiter + Redis, implementar algoritmo Sliding Window, métodos: check_limit(api_name, max_requests, window_seconds), wait_if_needed(api_name)
- [ ] T037 Crear archivo backend/src/collectors/base.py con clase abstracta BaseCollector definiendo interfaz: collect(lineamiento, limit), parse_response(raw_data), save_content(parsed_data), métodos comunes de retry con backoff exponencial
- [ ] T038 Crear archivo backend/src/collectors/youtube.py con clase YouTubeCollector heredando BaseCollector, implementar collect() usando google-api-python-client para buscar videos por keywords/hashtags, parse_response() extrayendo (video_id, titulo, descripcion, autor, fecha_publicacion, views, likes, comments), manejar rate limit YouTube (10,000 units/día)
- [ ] T039 Crear archivo backend/src/collectors/reddit.py con clase RedditCollector heredando BaseCollector, implementar collect() usando PRAW para buscar posts/comments por keywords, parse_response() extrayendo (post_id, titulo, texto, autor, subreddit, fecha_publicacion, upvotes, comments), manejar rate limit Reddit (60 requests/min)
- [ ] T040 Crear archivo backend/src/collectors/mastodon.py con clase MastodonCollector heredando BaseCollector, implementar collect() usando Mastodon.py para buscar toots por keywords/hashtags, parse_response() extrayendo (toot_id, contenido, autor, fecha_publicacion, favourites, reblogs), manejar rate limit Mastodon (300 requests/5min)
- [ ] T041 Crear archivo backend/src/tasks/__init__.py con configuración de Celery app (broker Redis, result_backend Redis, task_serializer JSON, timezone UTC)
- [ ] T042 Crear archivo backend/src/tasks/collection.py con tarea Celery @task recolectar_contenido_lineamiento(lineamiento_id, plataforma): cargar lineamiento, instanciar collector apropiado, ejecutar collect(), guardar contenido en DB, retornar estadísticas (contenido_nuevo, contenido_duplicado, errores)
- [ ] T043 Agregar en backend/src/tasks/collection.py tarea Celery @task recolectar_todos_lineamientos(): obtener todos lineamientos activos, crear group() de tareas recolectar_contenido_lineamiento para cada combinación (lineamiento, plataforma), ejecutar en paralelo
- [ ] T044 Configurar en backend/src/tasks/collection.py Celery Beat schedule para ejecutar recolectar_todos_lineamientos() cada 6 horas (FR-005)
- [ ] T045 Crear archivo backend/src/utils/cache.py con wrapper de Redis para cachear respuestas de APIs externas (TTL 1 hora), métodos: get(key), set(key, value, ttl), invalidate(pattern)

---

## Phase 5: US3 - Consultar Tendencias (P1 - MVP)

**User Story**: Un usuario necesita ver qué temas están siendo discutidos en redes sociales para un lineamiento específico, sin necesidad de segmentación demográfica avanzada

**Acceptance Criteria**: FR-016, FR-017, FR-018, FR-019, FR-020

- [ ] T046 Crear archivo backend/src/nlp/topic_modeling.py con clase TopicModeler usando BERTopic, métodos: entrenar_modelo(documentos), identificar_temas(documentos), extraer_keywords(tema_id), calcular_relevancia(documento, tema)
- [ ] T047 Crear archivo backend/src/nlp/sentiment.py con clase SentimentAnalyzer usando pysentimiento, métodos: analizar_sentimiento(texto) retornando (sentimiento: "positive"/"negative"/"neutral", score: float -1 a 1)
- [ ] T048 Crear archivo backend/src/tasks/processing.py con tarea Celery @task procesar_nlp_contenido(contenido_id): cargar contenido, ejecutar TopicModeler.identificar_temas(), ejecutar SentimentAnalyzer.analizar_sentimiento(), guardar en temas_identificados, marcar contenido.nlp_procesado=True
- [ ] T049 Agregar en backend/src/tasks/processing.py tarea Celery @task procesar_nlp_batch(): obtener contenido con nlp_procesado=False (límite 100), crear chord(group(procesar_nlp_contenido por cada item), callback=actualizar_estadisticas), ejecutar
- [ ] T050 Configurar en backend/src/tasks/processing.py Celery Beat schedule para ejecutar procesar_nlp_batch() cada 30 minutos
- [ ] T051 Crear archivo backend/src/services/analytics.py con clase AnalyticsService, método calcular_metricas_agregadas(tema_id) calculando: total_menciones, engagement_total (suma metadata.likes + comments + shares), sentiment_promedio
- [ ] T052 Agregar en backend/src/services/analytics.py método detectar_trending(umbral_crecimiento=0.15): consultar tendencias tabla con ventana de 24 horas, calcular tasa_crecimiento comparando periodo actual vs anterior, filtrar temas con tasa_crecimiento > umbral, marcar es_tendencia=True
- [ ] T053 Crear archivo backend/src/services/trends.py con clase TrendsService, método consultar_tendencias(lineamiento_id, fecha_inicio, fecha_fin, plataforma, solo_trending) retornando estructura jerárquica de 4 niveles según FR-017
- [ ] T054 Agregar en backend/src/services/trends.py método obtener_ejemplos_contenido(tema_id, limite=5) retornando lista de contenido real para el tema con metadata completa
- [ ] T055 Crear archivo backend/src/api/tendencias.py con ruta GET /tendencias: query params (lineamiento_id, fecha_inicio, fecha_fin, plataforma, pais, ciudad, edad_rango, genero, min_menciones, solo_trending), llamar TrendsService.consultar_tendencias(), retornar JSON jerárquico Plataforma → Ubicacion → Edad → Genero
- [ ] T056 Agregar en backend/src/api/tendencias.py ruta GET /tendencias/{tema_id}/ejemplos llamando TrendsService.obtener_ejemplos_contenido()
- [ ] T057 Registrar router de tendencias en backend/src/api/main.py con prefix /api/v1
- [ ] T058 Crear archivo backend/src/tasks/analytics.py con tarea Celery @task actualizar_tendencias(): ejecutar AnalyticsService.detectar_trending() para todos los temas activos, actualizar tabla tendencias
- [ ] T059 Configurar en backend/src/tasks/analytics.py Celery Beat schedule para ejecutar actualizar_tendencias() cada 30 minutos

---

## Phase 6: US4 - Múltiples Plataformas (P2)

**User Story**: El sistema debe recolectar datos simultáneamente de las tres plataformas principales: YouTube, Reddit y Mastodon, para proporcionar una vista holística de tendencias

**Acceptance Criteria**: FR-003 (todas las plataformas)

- [ ] T060 Actualizar backend/src/tasks/collection.py para configurar colas Celery separadas: youtube_queue, reddit_queue, mastodon_queue con configuración de workers (youtube: gevent/100 workers/prefetch 4, reddit: gevent/50 workers/prefetch 4, mastodon: gevent/30 workers/prefetch 4)
- [ ] T061 Actualizar backend/src/collectors/youtube.py para implementar recolección por lotes de 50 videos, manejar paginación usando pageToken, guardar en DB en transacción única por lote
- [ ] T062 Actualizar backend/src/collectors/reddit.py para implementar recolección por lotes de 50 posts, manejar paginación usando after parameter, guardar en DB en transacción única por lote
- [ ] T063 Actualizar backend/src/collectors/mastodon.py para implementar recolección por lotes de 50 toots, manejar paginación usando max_id parameter, guardar en DB en transacción única por lote
- [ ] T064 Agregar en backend/src/services/trends.py método obtener_tendencias_por_plataforma(lineamiento_id) retornando métricas comparativas entre plataformas (volumen, engagement, temas únicos por plataforma)
- [ ] T065 Agregar en backend/src/api/tendencias.py ruta GET /tendencias/comparativa-plataformas llamando TrendsService.obtener_tendencias_por_plataforma()

---

## Phase 7: US5 - Segmentación Demográfica (P2)

**User Story**: Un analista necesita ver cómo las tendencias varían por demografía: por ejemplo, descubrir que jóvenes de 18-24 en Bogotá hablan de "inversión en criptomonedas" en Reddit, mientras que adultos de 35-44 en Medellín buscan "crédito hipotecario" en YouTube

**Acceptance Criteria**: FR-011, FR-012, FR-013, FR-014, FR-015, FR-017

- [ ] T066 Crear archivo backend/src/nlp/ner.py con clase NERExtractor usando spaCy modelo es_core_news_lg, métodos: extraer_entidades(texto) retornando diccionario {persons: [], organizations: [], locations: []}, extraer_ubicaciones(texto) retornando lista de lugares mencionados con confianza
- [ ] T067 Crear archivo backend/src/nlp/demographics.py con clase DemographicsInferencer implementando métodos: inferir_ubicacion(contenido) usando NER + metadata de plataforma (si disponible), inferir_edad(contenido) usando análisis de keywords/lenguaje, inferir_genero(contenido) usando análisis de lenguaje/nombre autor, calcular_confianza(metodo_inferencia)
- [ ] T068 Agregar en backend/src/nlp/demographics.py método categorizar_ubicacion(ubicacion_raw) normalizando a estructura {pais: str, region: str, ciudad: str} usando diccionario de lugares conocidos
- [ ] T069 Agregar en backend/src/nlp/demographics.py método categorizar_edad(edad_inferida) mapeando a rangos ["18-24", "25-34", "35-44", "45-54", "55+", "unknown"]
- [ ] T070 Agregar en backend/src/nlp/demographics.py método categorizar_genero(genero_inferido) mapeando a valores ["male", "female", "other", "unknown"]
- [ ] T071 Actualizar backend/src/tasks/processing.py en tarea procesar_nlp_contenido para agregar: ejecutar NERExtractor.extraer_entidades(), guardar en temas_identificados.entidades_mencionadas
- [ ] T072 Crear en backend/src/tasks/processing.py tarea Celery @task inferir_demografia_tema(tema_id): cargar tema y contenido relacionado, ejecutar DemographicsInferencer para inferir ubicacion/edad/genero, calcular confianza por método usado, guardar en tabla demografia con confianza_score y metodo_inferencia
- [ ] T073 Agregar en backend/src/tasks/processing.py al callback de procesar_nlp_batch crear group() de tareas inferir_demografia_tema para todos los temas recién procesados
- [ ] T074 Actualizar backend/src/services/analytics.py método calcular_metricas_agregadas para agrupar por jerarquía (plataforma, ubicacion_pais, ubicacion_ciudad, edad_rango, genero), almacenar agregados en tabla demografia
- [ ] T075 Actualizar backend/src/services/trends.py método consultar_tendencias para construir estructura JSON jerárquica exacta de 4 niveles: Plataforma → Ubicación (país/ciudad) → Edad → Género según FR-017
- [ ] T076 Agregar en backend/src/api/tendencias.py validación de query params: plataforma IN ["youtube", "reddit", "mastodon"], edad_rango IN ["18-24", "25-34", "35-44", "45-54", "55+"], genero IN ["male", "female", "other", "unknown"]
- [ ] T077 Agregar en backend/src/api/tendencias.py ruta GET /tendencias/segmentacion con filtros demográficos completos retornando breakdown detallado por segmento

---

## Phase 8: US6 - NLP Avanzado (P2)

**User Story**: El sistema debe automáticamente identificar de qué temas se está hablando en el contenido recolectado, sin que el usuario tenga que definir temas manualmente

**Acceptance Criteria**: FR-007, FR-008, FR-009, FR-010, FR-026

- [ ] T078 Descargar modelos NLP en backend/src/nlp/__init__.py: spaCy es_core_news_lg, descargar modelo RoBERTuito (PlanTL-GOB-ES/roberta-base-bne), configurar BERTopic con embeddings multilingües
- [ ] T079 Actualizar backend/src/nlp/topic_modeling.py para usar RoBERTuito embeddings, configurar BERTopic con parámetros: min_topic_size=10, nr_topics="auto", language="spanish"
- [ ] T080 Agregar en backend/src/nlp/topic_modeling.py método asignar_nombres_temas(temas_brutos) para generar nombres descriptivos en español usando keywords principales (evitar "Topic_0", usar "Inversión en Bolsa")
- [ ] T081 Actualizar backend/src/nlp/sentiment.py para usar pysentimiento modelo específico de español, manejar variaciones regionales (Colombia, México, Argentina, España)
- [ ] T082 Agregar en backend/src/nlp/sentiment.py método detectar_idioma(texto) usando langdetect, filtrar solo español ("es"), marcar otros idiomas como "no procesado"
- [ ] T083 Crear archivo backend/src/nlp/preprocessing.py con funciones: limpiar_texto(texto) removiendo URLs/mentions/emojis, normalizar_texto(texto) para español (tildes, ñ, caracteres especiales)
- [ ] T084 Actualizar backend/src/tasks/processing.py en procesar_nlp_contenido para agregar preprocesamiento: detectar_idioma(), si no es español marcar y saltar, aplicar limpiar_texto() antes de NLP
- [ ] T085 Configurar en backend/src/tasks/processing.py cola nlp_queue con workers prefork/8 workers/prefetch 1 (para procesos CPU-intensive de NLP)
- [ ] T086 Agregar en backend/src/nlp/topic_modeling.py método reentrenar_modelo_periodico(documentos_nuevos) para actualizar modelo BERTopic con nuevos datos cada semana, mantener temas coherentes
- [ ] T087 Crear en backend/src/tasks/processing.py tarea Celery @task reentrenar_modelo_nlp(): cargar todo contenido de última semana, ejecutar TopicModeler.reentrenar_modelo_periodico(), persistir modelo actualizado
- [ ] T088 Configurar en backend/src/tasks/processing.py Celery Beat schedule para ejecutar reentrenar_modelo_nlp() semanalmente (domingos 2 AM)

---

## Phase 9: US7 - Validación Google Trends (P3)

**User Story**: El sistema debe validar si una tendencia detectada en redes sociales es real o solo una burbuja algorítmica, correlacionando con datos de búsqueda

**Acceptance Criteria**: FR-021, FR-022

- [ ] T089 Crear archivo backend/src/collectors/trends.py con clase GoogleTrendsCollector usando pytrends, métodos: buscar_tendencia(keyword, timeframe, geo), obtener_interes_tiempo(keyword), obtener_queries_relacionados(keyword)
- [ ] T090 Agregar en backend/src/collectors/trends.py método comparar_regiones(keyword) obteniendo volumen de búsquedas por región (país/ciudad) de Google Trends
- [ ] T091 Crear archivo backend/src/services/validation.py con clase ValidationService, método validar_tendencia(tema_id): obtener tema y keywords principales, consultar GoogleTrendsCollector para últimos 7 días, comparar volumen social vs volumen búsquedas
- [ ] T092 Agregar en backend/src/services/validation.py método calcular_correlacion(datos_social, datos_trends) usando correlación de Pearson, retornar indice_coincidencia entre 0 y 1
- [ ] T093 Agregar en backend/src/services/validation.py método identificar_gaps(datos_social, datos_trends): detectar casos con alto volumen búsquedas pero bajo contenido social (gap de contenido FR-022), retornar oportunidades
- [ ] T094 Agregar en backend/src/services/validation.py lógica para marcar tendencia como validada si indice_coincidencia >= 0.70
- [ ] T095 Crear en backend/src/tasks/validation.py tarea Celery @task validar_tendencia_google(tema_id): ejecutar ValidationService.validar_tendencia(), guardar resultado en validacion_tendencias con google_trends_data JSONB
- [ ] T096 Agregar en backend/src/tasks/validation.py tarea Celery @task validar_todas_tendencias(): obtener todos temas marcados como es_tendencia=True sin validación, crear group() de tareas validar_tendencia_google, ejecutar en paralelo
- [ ] T097 Configurar en backend/src/tasks/validation.py Celery Beat schedule para ejecutar validar_todas_tendencias() diariamente (6 AM)
- [ ] T098 Agregar en backend/src/api/tendencias.py ruta GET /tendencias/{tema_id}/validacion retornando datos de validacion_tendencias incluyendo google_trends_data, indice_coincidencia, validada
- [ ] T099 Agregar en backend/src/api/tendencias.py ruta GET /tendencias/gaps retornando lista de tendencias con solo_en_plataforma=True (oportunidades de contenido)

---

## Phase 10: US8 - Alertas Emergentes (P3)

**User Story**: Un usuario necesita ser notificado inmediatamente cuando un tema comienza a crecer rápidamente, para poder reaccionar antes que la competencia

**Acceptance Criteria**: FR-027

- [ ] T100 Actualizar backend/src/services/analytics.py método detectar_trending para identificar temas con tasa_crecimiento > 0.50 (50% en 24h según FR-027), marcar para alertas
- [ ] T101 Crear archivo backend/src/tasks/alerts.py con tarea Celery @task generar_alerta_trending(tema_id): cargar tema con métricas, construir payload de alerta (tema_nombre, tasa_crecimiento, plataformas, ejemplos_contenido, timestamp)
- [ ] T102 Agregar en backend/src/tasks/alerts.py método enviar_alerta(payload) con múltiples canales: logging (por ahora), preparar estructura para webhooks/email futuros
- [ ] T103 Actualizar backend/src/tasks/analytics.py en actualizar_tendencias para detectar temas no alertados (es_tendencia=True AND alerta_enviada=False), crear group() de tareas generar_alerta_trending
- [ ] T104 Agregar en backend/src/tasks/alerts.py al finalizar generar_alerta_trending marcar tendencias.alerta_enviada=True
- [ ] T105 Crear archivo backend/src/api/alertas.py con ruta GET /alertas retornando historial de alertas enviadas (últimas 24 horas) ordenadas por tasa_crecimiento DESC
- [ ] T106 Agregar en backend/src/api/alertas.py ruta GET /alertas/pendientes retornando temas trending sin alerta enviada (para debugging)
- [ ] T107 Registrar router de alertas en backend/src/api/main.py con prefix /api/v1

---

## Phase 11: US9 - Exportar Reportes (P3)

**User Story**: Un usuario necesita exportar análisis de tendencias en formatos compartibles para presentar a stakeholders o integrar con otras herramientas

**Acceptance Criteria**: FR-028

- [ ] T108 Crear archivo backend/src/services/export.py con clase ExportService, método exportar_json(datos_tendencias) retornando estructura JSON completa con jerarquía de 4 niveles preservada
- [ ] T109 Agregar en backend/src/services/export.py método exportar_csv(datos_tendencias): aplanar jerarquía de 4 niveles a filas CSV con columnas (plataforma, ubicacion_pais, ubicacion_ciudad, edad_rango, genero, tema_nombre, menciones, engagement, sentiment, tasa_crecimiento, trending), retornar StringIO con CSV
- [ ] T110 Agregar en backend/src/services/export.py método exportar_excel(datos_tendencias) usando openpyxl: crear workbook con múltiples sheets (Resumen, Por Plataforma, Por Demografía, Temas Detallados), aplicar formato (headers bold, colores alternados)
- [ ] T111 Agregar en backend/src/api/tendencias.py ruta GET /tendencias/export con query params (formato: "json"/"csv"/"excel", + filtros iguales a GET /tendencias), llamar TrendsService.consultar_tendencias() seguido de ExportService según formato
- [ ] T112 Configurar en backend/src/api/tendencias.py headers de respuesta apropiados: Content-Type (application/json, text/csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet), Content-Disposition con filename dinámico (tendencias_{fecha}.{ext})
- [ ] T113 Agregar en backend/pyproject.toml dependencia openpyxl para exportación Excel
- [ ] T114 Agregar validación en backend/src/api/tendencias.py para limitar tamaño de exportación (máximo 10,000 registros por exportación, retornar 413 si excede)

---

## Phase 12: Polish & Production Readiness

**Objetivo**: Preparar sistema para producción con monitoreo, optimización, documentación

- [ ] T115 [P] Agregar en backend/src/utils/logging.py integración con Prometheus para métricas: contador de requests por endpoint, histograma de latencia, gauge de items procesados, contador de errores por tipo
- [ ] T116 [P] Crear archivo backend/src/api/monitoring.py con rutas: GET /metrics (Prometheus metrics), GET /health (healthcheck simple), GET /health/detailed (status DB, Redis, Celery workers)
- [ ] T117 [P] Registrar router de monitoring en backend/src/api/main.py con prefix /internal (sin autenticación para load balancers)
- [ ] T118 Agregar en backend/docker-compose.yml servicios de monitoreo: Prometheus, Grafana, Flower (Celery monitoring)
- [ ] T119 Crear archivo backend/prometheus.yml con configuración de scraping: targets FastAPI /metrics, Celery exporter, PostgreSQL exporter
- [ ] T120 [P] Crear archivo backend/grafana/dashboards/api_performance.json con dashboard: request rate, latency p50/p95/p99, error rate, top endpoints
- [ ] T121 [P] Crear archivo backend/grafana/dashboards/data_pipeline.json con dashboard: contenido recolectado/hora, temas procesados/hora, cola Celery depth, worker utilization
- [ ] T122 [P] Crear archivo backend/grafana/dashboards/business_metrics.json con dashboard: lineamientos activos, tendencias detectadas/día, alertas enviadas, cobertura demográfica
- [ ] T123 Optimizar queries en backend/src/services/trends.py: agregar índices compuestos faltantes, usar EXPLAIN ANALYZE para verificar performance <3s según SC-003
- [ ] T124 Agregar en backend/src/utils/cache.py estrategia de cache para consultas frecuentes: cachear resultados de consultar_tendencias() por 5 minutos, invalidar al actualizar tendencias
- [ ] T125 Crear archivo backend/src/tasks/maintenance.py con tarea Celery @task ejecutar_limpieza_datos(): llamar función SQL cleanup_old_data(), loggear estadísticas de registros eliminados
- [ ] T126 Configurar en backend/src/tasks/maintenance.py Celery Beat schedule para ejecutar ejecutar_limpieza_datos() diariamente (3 AM)
- [ ] T127 [P] Actualizar backend/README.md con secciones: Arquitectura (diagrama de componentes), Setup (local + Docker), Configuración API keys, Estructura del proyecto, Guía de desarrollo
- [ ] T128 [P] Crear archivo backend/docs/API.md con documentación de API REST: autenticación, endpoints, ejemplos de requests/responses, códigos de error, rate limits
- [ ] T129 [P] Crear archivo backend/docs/DEPLOYMENT.md con guía de despliegue a producción: requisitos de servidor, variables de entorno, configuración PostgreSQL/Redis, estrategia de migraciones, monitoreo
- [ ] T130 Generar especificación OpenAPI automáticamente en backend/src/api/main.py configurando FastAPI metadata (title, version, description, contact), exportar a backend/openapi.json
- [ ] T131 Configurar en backend/src/api/main.py documentación interactiva: Swagger UI en /docs, ReDoc en /redoc
- [ ] T132 Crear archivo backend/.dockerignore excluyendo: __pycache__, *.pyc, .env, .git, tests/, docs/, *.md
- [ ] T133 Crear archivo backend/Dockerfile multi-stage: stage 1 (builder con dependencias), stage 2 (runtime slim), configurar user no-root, exponer puerto 8000
- [ ] T134 Crear archivo backend/docker-compose.prod.yml para producción: sin volumenes de desarrollo, healthchecks, restart policies, resource limits
- [ ] T135 Agregar en backend/src/api/main.py middleware de compresión (gzip) para responses >1KB
- [ ] T136 Agregar en backend/src/api/main.py middleware de rate limiting usando slowapi: 100 requests/min por IP para endpoints públicos, 1000 requests/min para API keys autenticadas
- [ ] T137 Crear script backend/scripts/seed_demo_data.py para poblar DB con lineamientos demo: "Tecnología Colombia", "Finanzas Personales", "Salud y Bienestar", cada uno con keywords/hashtags relevantes
- [ ] T138 Crear script backend/scripts/test_collectors.sh para verificar conectividad con APIs externas: YouTube, Reddit, Mastodon, Google Trends, reportar límites disponibles
- [ ] T139 [P] Crear archivo backend/tests/contract/test_api_contract.py verificando contrato de API: estructura de respuesta jerárquica 4 niveles, códigos de status, headers requeridos
- [ ] T140 [P] Crear archivo backend/tests/integration/test_collection_pipeline.py testeando flujo completo: crear lineamiento → recolectar contenido → verificar en DB
- [ ] T141 [P] Crear archivo backend/tests/integration/test_nlp_pipeline.py testeando: contenido → procesar NLP → verificar temas_identificados → verificar demografia
- [ ] T142 [P] Crear archivo backend/tests/unit/test_collectors.py con mocks de APIs externas, verificar parsing correcto de respuestas
- [ ] T143 [P] Crear archivo backend/tests/unit/test_nlp.py testeando: topic_modeling, sentiment, ner, demographics con datasets español
- [ ] T144 [P] Crear archivo backend/tests/unit/test_services.py testeando lógica de negocio: LineamientosService, AnalyticsService, TrendsService, ValidationService
- [ ] T145 Configurar en backend/pyproject.toml pytest con coverage: mínimo 70% coverage para aprobar CI, excluir tests/ y migrations/
- [ ] T146 Crear archivo backend/.github/workflows/ci.yml con GitHub Actions: lint (flake8/black), tests (pytest), coverage report, build Docker image
- [ ] T147 Agregar en backend/src/api/main.py manejo global de excepciones: DatabaseError → 503, ValidationError → 400, NotFoundError → 404, RateLimitError → 429, fallback → 500 con logging
- [ ] T148 Crear archivo backend/CHANGELOG.md documentando versión 1.0.0 con features implementadas según user stories

---

## Dependencies

### Bloqueantes Críticos

- **T001-T008 bloquea TODO**: Sin estructura de proyecto no se puede crear código
- **T009-T020 bloquea US1-US9**: Sin schema de DB no se pueden implementar features
- **T021-T026 bloquea US1-US9**: Sin modelos SQLAlchemy no se puede acceder a DB
- **T027-T030 bloquea Phase 3-12**: Sin logging/config/auth no hay APIs seguras
- **T031-T035 bloquea Phase 4**: Sin API de lineamientos no se puede recolectar (lineamientos son input de recolección)
- **T036-T045 bloquea Phase 5**: Sin contenido recolectado no hay datos para analizar tendencias
- **T046-T059 bloquea Phase 6-11**: NLP y analytics son core del sistema, todos los features avanzados dependen de ellos

### Dependencias por User Story

**US1 (T031-T035)**: Depende de T009-T030 (foundation)
**US2 (T036-T045)**: Depende de US1 + T009-T030 (necesita lineamientos configurados)
**US3 (T046-T059)**: Depende de US2 (necesita contenido recolectado)
**US4 (T060-T065)**: Depende de US2 (mejora recolección existente)
**US5 (T066-T077)**: Depende de US3 (agrega demografía a tendencias existentes)
**US6 (T078-T088)**: Depende de US3 (mejora NLP existente)
**US7 (T089-T099)**: Depende de US3 (valida tendencias existentes)
**US8 (T100-T107)**: Depende de US3 (alerta sobre tendencias existentes)
**US9 (T108-T114)**: Depende de US3 (exporta tendencias existentes)
**Polish (T115-T148)**: Depende de US1-US9 (optimiza sistema completo)

---

## Parallel Execution Examples

### Phase 2 - Modelos pueden crearse en paralelo

```
T021, T022, T023, T024, T025, T026 [P]
```

Todos son archivos independientes mapeando diferentes tablas, sin dependencias entre sí.

### Phase 12 - Documentación y tests en paralelo

```
T127, T128, T129 [P] - Documentación
T139, T140, T141, T142, T143, T144 [P] - Tests
T120, T121, T122 [P] - Dashboards Grafana
```

Archivos independientes que documentan/testean funcionalidad ya implementada.

---

## Implementation Strategy

### Orden de Ejecución Recomendado

1. **Phase 1 (T001-T008)**: Setup secuencial - establece estructura base
2. **Phase 2 (T009-T030)**: Foundation
   - T009-T020: Migraciones secuenciales (orden de dependencias de tablas)
   - T021-T026: Modelos en paralelo [P]
   - T027-T030: Utils/auth secuenciales
3. **Phase 3 (T031-T035)**: US1 - Secuencial (API depende de service)
4. **Phase 4 (T036-T045)**: US2 - Mayormente secuencial (collectors pueden ser paralelos pero tasks dependen de collectors)
5. **Phase 5 (T046-T059)**: US3 - Secuencial (pipeline NLP → analytics → API)
6. **Phase 6-11**: US4-US9 - Pueden ejecutarse en CUALQUIER orden después de US3 (son mejoras independientes)
7. **Phase 12**: Polish - Mayoría paralelos, solo T123-T126 requieren sistema funcionando

### Estrategia de Testing

- NO se requiere TDD (spec no lo solicita explícitamente)
- Tests se implementan en Phase 12 (T139-T145) después de features completas
- Contract tests (T139) validan API según spec
- Integration tests (T140-T141) validan pipelines end-to-end
- Unit tests (T142-T144) validan componentes individuales

### Hitos Críticos

**Hito 1 - MVP Funcional** (End of Phase 5):
- ✅ Configurar lineamientos (US1)
- ✅ Recolectar contenido (US2)
- ✅ Consultar tendencias (US3)
- Sistema básico operacional

**Hito 2 - Feature Complete** (End of Phase 11):
- ✅ Todas las user stories implementadas (US1-US9)
- ✅ Todas las prioridades cubiertas (P1, P2, P3)

**Hito 3 - Production Ready** (End of Phase 12):
- ✅ Tests, documentación, monitoreo
- ✅ CI/CD configurado
- ✅ Sistema listo para deployment

---

## Notes

### Stack Tecnológico Final

**IMPORTANTE - Cambio de Plataformas**: Según research.md, las APIs de TikTok, Instagram y Facebook NO son viables gratuitamente. El sistema usa SOLO:
- ✅ YouTube Data API v3 (10,000 units/día gratis)
- ✅ Reddit API via PRAW (60 req/min gratis)
- ✅ Mastodon API (300 req/5min gratis)
- ✅ Google Trends via pytrends (sin límites)

**Backend**: Python 3.11+, FastAPI, Uvicorn
**Queue**: Celery + Redis (5 colas: youtube_queue, reddit_queue, mastodon_queue, nlp_queue, analytics_queue)
**Database**: PostgreSQL 15 + TimescaleDB (hypertables, agregados continuos, retención 7 días)
**NLP**: RoBERTuito (Spanish BERT), BERTopic, pysentimiento, spaCy es_core_news_lg
**Monitoring**: Prometheus, Grafana, Flower

### Granularidad de Tasks

- **Colectores**: Lotes de 50 items (T061-T063) para eficiencia de DB
- **NLP**: Item individual (T048) porque es CPU-intensive
- **Analytics**: Procesamiento por lotes (T058) para agregaciones

### Rate Limits por Plataforma

- **YouTube**: 10,000 units/día (1 búsqueda = ~100 units = 100 búsquedas/día)
- **Reddit**: 60 requests/min = 3,600/hora = 86,400/día
- **Mastodon**: 300 requests/5min = 3,600/hora = 86,400/día
- **Total capacidad**: ~149,000 requests/día (supera ampliamente objetivo de 4,000 items/día)

### Retención de Datos (FR-025)

- TimescaleDB maneja retención automática de tabla `tendencias` (hypertable)
- Función SQL `cleanup_old_data()` limpia tablas no-TimescaleDB
- Tarea Celery `ejecutar_limpieza_datos()` ejecuta diariamente (T125-T126)
- Retención: 7 días para todo contenido y análisis

### Jerarquía de Respuesta API (FR-017)

Estructura JSON de 4 niveles ESTRICTA:
```json
{
  "plataforma": {
    "youtube": {
      "ubicacion": {
        "Colombia": {
          "Bogotá": {
            "edad": {
              "25-34": {
                "genero": {
                  "female": {
                    "temas": [...],
                    "metricas": {...}
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
```

### Performance Targets

- **SC-003**: Queries <3s para 100k items → Logrado con índices + agregados continuos TimescaleDB
- **SC-001**: 4,000 items/día → Capacidad de 149,000 requests/día disponible
- **SC-004**: Precisión demografía 65%+ → DemographicsInferencer multi-método
- **SC-011**: Alertas dentro de 6h de crecimiento → Celery beat cada 30min (T059)

### Consideraciones de Idioma (FR-026)

- Optimizado para español con variantes regionales: Colombia, México, Argentina, España
- Modelo RoBERTuito entrenado específicamente en español
- spaCy modelo es_core_news_lg para NER en español
- pysentimiento maneja variaciones regionales de español
- Detección de idioma (T082) filtra contenido no-español

### Seguridad

- Autenticación por API key estática (T029)
- Rate limiting 100 req/min anónimos, 1000 req/min autenticados (T136)
- CORS configurado (T030)
- Docker user no-root (T133)
- Secrets en .env (nunca commiteados)

### Total Tasks: 148

- Phase 1: 8 tasks (T001-T008)
- Phase 2: 22 tasks (T009-T030)
- Phase 3: 5 tasks (T031-T035) - US1 P1
- Phase 4: 10 tasks (T036-T045) - US2 P1
- Phase 5: 14 tasks (T046-T059) - US3 P1
- Phase 6: 6 tasks (T060-T065) - US4 P2
- Phase 7: 12 tasks (T066-T077) - US5 P2
- Phase 8: 11 tasks (T078-T088) - US6 P2
- Phase 9: 11 tasks (T089-T099) - US7 P3
- Phase 10: 8 tasks (T100-T107) - US8 P3
- Phase 11: 7 tasks (T108-T114) - US9 P3
- Phase 12: 34 tasks (T115-T148) - Polish

**MVP (P1)**: 59 tasks (Phase 1-5)
**Feature Complete (P1+P2+P3)**: 114 tasks (Phase 1-11)
**Production Ready**: 148 tasks (Phase 1-12)
