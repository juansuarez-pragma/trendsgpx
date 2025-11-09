# Feature Specification: Sistema de Análisis de Tendencias en Redes Sociales

**Feature Branch**: `001-social-trends-analysis`
**Created**: 2025-11-08
**Status**: Draft
**Input**: User description: "Sistema de análisis de tendencias en redes sociales que identifica, analiza y reporta temas trending en YouTube, TikTok, Instagram y Facebook, con segmentación demográfica detallada por plataforma, ubicación geográfica, rango de edad y género"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Configurar Lineamientos de Análisis (Priority: P1)

Un analista de marketing necesita configurar áreas temáticas específicas (lineamientos) para monitorear conversaciones en redes sociales. Por ejemplo, crear un lineamiento "Finanzas Personales" con palabras clave como "inversión", "ahorro", "crédito", y hashtags como #finanzaspersonales, #ahorro.

**Why this priority**: Sin lineamientos configurados, el sistema no puede recolectar datos relevantes. Es la base fundamental del sistema.

**Independent Test**: Puede ser completamente testado creando, editando y eliminando lineamientos, y verificando que se almacenan correctamente sin necesitar que el resto del sistema esté implementado.

**Acceptance Scenarios**:

1. **Given** un usuario autenticado en el sistema, **When** el usuario crea un nuevo lineamiento "Finanzas" con keywords ["inversión", "ahorro"] y hashtags ["#finanzas"], **Then** el sistema guarda el lineamiento y lo muestra en la lista de lineamientos activos
2. **Given** un lineamiento existente "Finanzas", **When** el usuario edita el lineamiento agregando keyword "bolsa", **Then** el sistema actualiza el lineamiento y futuros análisis incluyen la nueva keyword
3. **Given** múltiples lineamientos en el sistema, **When** el usuario elimina un lineamiento, **Then** el sistema elimina solo ese lineamiento sin afectar los datos históricos ya recolectados
4. **Given** un lineamiento configurado, **When** el usuario especifica las plataformas a monitorear (YouTube, TikTok), **Then** el sistema solo recolecta datos de esas plataformas para ese lineamiento

---

### User Story 2 - Recolectar Contenido Público de Redes Sociales (Priority: P1)

El sistema debe automáticamente recolectar contenido público relacionado a los lineamientos configurados desde plataformas de redes sociales. Por ejemplo, recolectar videos de YouTube que mencionen "inversión en bolsa" o posts de Instagram con hashtag #finanzaspersonales.

**Why this priority**: Es el motor de datos del sistema. Sin recolección, no hay datos para analizar. Junto con configurar lineamientos, forma el MVP mínimo.

**Independent Test**: Puede ser testado configurando un lineamiento simple, esperando que el sistema recolecte datos, y verificando que el contenido recolectado está almacenado con su metadata (título, autor, fecha, métricas de engagement).

**Acceptance Scenarios**:

1. **Given** un lineamiento "Finanzas" con keyword "inversión", **When** el sistema ejecuta recolección en YouTube, **Then** el sistema obtiene al menos 100 videos públicos que contienen "inversión" en título o descripción
2. **Given** contenido recolectado de YouTube, **When** el usuario consulta los datos, **Then** cada item incluye: título, descripción, autor, fecha de publicación, vistas, likes, comentarios, shares
3. **Given** un lineamiento con hashtag "#finanzas", **When** el sistema recolecta de Instagram, **Then** el sistema obtiene posts públicos que usan ese hashtag
4. **Given** múltiples plataformas configuradas para un lineamiento, **When** la recolección se ejecuta, **Then** el sistema recolecta datos de todas las plataformas en paralelo
5. **Given** límites de API (rate limits), **When** el sistema alcanza el límite, **Then** el sistema pausa la recolección y la reanuda automáticamente cuando el límite se reinicia

---

### User Story 3 - Consultar Tendencias Sin Segmentación (Priority: P1)

Un usuario necesita ver qué temas están siendo discutidos en redes sociales para un lineamiento específico, sin necesidad de segmentación demográfica avanzada.

**Why this priority**: Proporciona valor inmediato mostrando "de qué se habla" en redes sociales. Es la funcionalidad core que justifica el sistema, incluso sin demografía completa.

**Independent Test**: Puede ser testado ejecutando una consulta simple y verificando que retorna los temas identificados con métricas básicas (menciones, engagement) sin depender de segmentación demográfica.

**Acceptance Scenarios**:

1. **Given** datos recolectados para lineamiento "Finanzas", **When** el usuario consulta tendencias, **Then** el sistema retorna lista de temas identificados (ej: "Inversión en bolsa", "Ahorro para vivienda") con número de menciones
2. **Given** temas identificados, **When** el usuario selecciona un tema, **Then** el sistema muestra ejemplos de contenido real que pertenece a ese tema
3. **Given** contenido con métricas de engagement, **When** el sistema calcula tendencias, **Then** los temas se ordenan por engagement total (suma de likes, comentarios, shares)
4. **Given** datos de las últimas 24 horas, **When** el usuario consulta, **Then** el sistema identifica qué temas están creciendo (trending) basado en velocidad de menciones

---

### User Story 4 - Recolectar de Múltiples Plataformas (Priority: P2)

El sistema debe recolectar datos simultáneamente de las cuatro plataformas principales: YouTube, TikTok, Instagram y Facebook, para proporcionar una vista holística de tendencias.

**Why this priority**: Amplía la cobertura de datos. Una vez que el MVP funciona con una plataforma (P1), agregar más plataformas multiplica el valor sin cambiar la arquitectura fundamental.

**Independent Test**: Puede ser testado configurando un lineamiento, ejecutando recolección multi-plataforma, y verificando que los datos de las 4 plataformas están presentes y correctamente etiquetados por plataforma de origen.

**Acceptance Scenarios**:

1. **Given** un lineamiento configurado para 4 plataformas, **When** la recolección se ejecuta, **Then** el sistema recolecta datos de YouTube, TikTok, Instagram y Facebook
2. **Given** datos recolectados de múltiples plataformas, **When** el usuario consulta, **Then** cada item de contenido está claramente identificado con su plataforma de origen
3. **Given** diferentes límites de API por plataforma, **When** una plataforma alcanza su límite, **Then** las otras plataformas continúan recolectando sin interrupción
4. **Given** contenido de diferentes plataformas, **When** se identifican temas, **Then** el sistema muestra en qué plataformas cada tema es popular

---

### User Story 5 - Ver Tendencias con Segmentación Demográfica (Priority: P2)

Un analista necesita ver cómo las tendencias varían por demografía: por ejemplo, descubrir que jóvenes de 18-24 en Bogotá hablan de "inversión en criptomonedas" en TikTok, mientras que adultos de 35-44 en Medellín buscan "crédito hipotecario" en YouTube.

**Why this priority**: Esta es la diferenciación clave del sistema. Transforma datos generales en insights accionables por segmento demográfico específico.

**Independent Test**: Puede ser testado consultando tendencias con filtros demográficos y verificando que los resultados están correctamente segmentados en la jerarquía de 4 niveles: Plataforma → Ubicación → Edad → Género.

**Acceptance Scenarios**:

1. **Given** datos con información de ubicación, **When** el usuario consulta tendencias para Colombia, **Then** el sistema muestra tendencias segmentadas por región (Bogotá, Medellín, Cali) y ciudad
2. **Given** contenido categorizado por rango de edad, **When** el usuario filtra por edad 18-24, **Then** el sistema muestra solo tendencias de ese grupo demográfico
3. **Given** datos segmentados por género, **When** el usuario compara tendencias, **Then** el sistema muestra diferencias entre género masculino y femenino para el mismo tema
4. **Given** la jerarquía Plataforma → Ubicación → Edad → Género, **When** el usuario consulta vía API, **Then** la respuesta JSON sigue exactamente esa estructura de 4 niveles
5. **Given** datos donde demografía no está disponible directamente, **When** el sistema procesa el contenido, **Then** el sistema infiere demografía usando análisis de texto y metadata

---

### User Story 6 - Identificar Temas con Procesamiento de Lenguaje Natural (Priority: P2)

El sistema debe automáticamente identificar de qué temas se está hablando en el contenido recolectado, sin que el usuario tenga que definir temas manualmente. Por ejemplo, agrupar automáticamente contenido sobre "invertir en acciones", "cómo comprar acciones", "tutorial de trading" bajo el tema "Inversión en Bolsa de Valores".

**Why this priority**: Automatiza el análisis y descubre temas emergentes que el usuario no anticipó. Sin NLP, el análisis sería manual y no escalable.

**Independent Test**: Puede ser testado alimentando contenido al sistema y verificando que identifica temas coherentes, extrae keywords relevantes, y calcula sentiment sin intervención manual.

**Acceptance Scenarios**:

1. **Given** 1,000 posts recolectados sobre finanzas, **When** el sistema ejecuta análisis NLP, **Then** el sistema identifica entre 5-15 temas distintos con nombres descriptivos
2. **Given** un tema identificado "Inversión en Bolsa", **When** el usuario consulta detalles, **Then** el sistema muestra las keywords que definen ese tema (ej: "bolsa", "acciones", "trading", "invertir")
3. **Given** contenido procesado con NLP, **When** el sistema analiza sentiment, **Then** cada tema tiene un sentiment promedio entre -1 (negativo) y +1 (positivo)
4. **Given** múltiples menciones de lugares en el texto, **When** el sistema extrae entidades nombradas, **Then** el sistema identifica ubicaciones mencionadas (ej: "Bogotá", "Colombia") para enriquecer segmentación geográfica
5. **Given** contenido en español con variaciones regionales, **When** el sistema procesa texto, **Then** el sistema maneja correctamente español de diferentes países (Colombia, México, Argentina)

---

### User Story 7 - Validar Tendencias con Datos de Búsqueda (Priority: P3)

El sistema debe validar si una tendencia detectada en redes sociales es real o solo una burbuja algorítmica, correlacionando con datos de búsqueda (ej: Google Trends). Por ejemplo, si "plan de ahorro 50/30/20" es trending en TikTok (+200% engagement) Y las búsquedas en Google crecen +180%, entonces es una tendencia real.

**Why this priority**: Aumenta la confianza en las tendencias identificadas. Es un feature avanzado que diferencia tendencias reales de virales artificiales, pero no es esencial para el valor core.

**Independent Test**: Puede ser testado comparando una tendencia detectada en redes sociales con datos de Google Trends y verificando que el sistema marca tendencias como "validadas" cuando hay correlación.

**Acceptance Scenarios**:

1. **Given** un tema trending en TikTok, **When** el sistema consulta Google Trends, **Then** el sistema compara volumen de búsquedas con menciones en redes sociales
2. **Given** alta correlación entre búsquedas y menciones sociales (>70%), **When** el usuario consulta tendencias, **Then** el sistema marca el tema como "Tendencia Validada"
3. **Given** alto volumen de búsquedas pero bajo contenido social, **When** el sistema analiza, **Then** el sistema identifica un "Gap de Contenido" (oportunidad para creadores)
4. **Given** datos de búsquedas por región en Google Trends, **When** el sistema compara con datos sociales, **Then** el sistema identifica regiones con alto interés pero bajo contenido local

---

### User Story 8 - Recibir Alertas de Tendencias Emergentes (Priority: P3)

Un usuario necesita ser notificado inmediatamente cuando un tema comienza a crecer rápidamente (ej: +100% menciones en 24 horas), para poder reaccionar antes que la competencia.

**Why this priority**: Proporciona ventaja competitiva al detectar tendencias temprano. Es valioso pero no esencial para el funcionamiento core del sistema.

**Independent Test**: Puede ser testado configurando umbrales de alerta, simulando un crecimiento rápido de un tema, y verificando que el sistema envía la alerta correctamente.

**Acceptance Scenarios**:

1. **Given** un tema con crecimiento >50% en menciones en 24 horas, **When** el sistema detecta el crecimiento, **Then** el sistema envía alerta al usuario con detalles del tema
2. **Given** alertas configuradas para un lineamiento, **When** un tema cruza el umbral de trending, **Then** el usuario recibe notificación en tiempo real
3. **Given** múltiples temas creciendo simultáneamente, **When** el sistema genera alertas, **Then** las alertas están priorizadas por velocidad de crecimiento
4. **Given** alertas enviadas, **When** el usuario hace clic en la alerta, **Then** el sistema muestra análisis detallado del tema trending incluyendo ejemplos de contenido

---

### User Story 9 - Exportar Reportes de Tendencias (Priority: P3)

Un usuario necesita exportar análisis de tendencias en formatos compartibles (JSON, CSV, PDF) para presentar a stakeholders o integrar con otras herramientas.

**Why this priority**: Facilita compartir insights con equipos. Es conveniente pero el sistema entrega valor sin esta funcionalidad.

**Independent Test**: Puede ser testado ejecutando una consulta de tendencias y exportándola en diferentes formatos, verificando que los datos exportados son completos y correctos.

**Acceptance Scenarios**:

1. **Given** resultados de análisis de tendencias, **When** el usuario solicita exportar en JSON, **Then** el sistema genera un archivo JSON con la estructura jerárquica completa de 4 niveles
2. **Given** datos de tendencias, **When** el usuario exporta a CSV, **Then** el sistema genera CSV con una fila por combinación de Plataforma-Ubicación-Edad-Género-Tema
3. **Given** análisis completado, **When** el usuario solicita reporte PDF, **Then** el sistema genera PDF con visualizaciones de tendencias, gráficos de engagement, y tablas de datos demográficos

---

### Edge Cases

- **¿Qué pasa cuando una API de red social está temporalmente caída?**
  - El sistema debe reintentar la conexión automáticamente con backoff exponencial y marcar los datos como "pendientes de recolección"

- **¿Cómo maneja el sistema contenido en múltiples idiomas?**
  - El sistema debe detectar idioma y procesar solo contenido en español o lenguas configuradas, marcando otros idiomas como "no procesado"

- **¿Qué sucede cuando demografía no puede ser inferida con confianza?**
  - El sistema debe marcar demografía como "desconocida" e incluir el dato en categoría "Desconocido" en lugar de adivinar incorrectamente

- **¿Cómo maneja el sistema picos masivos de contenido (evento viral)?**
  - El sistema debe priorizar recolección de contenido más reciente y con más engagement, estableciendo límites de contenido procesado por hora

- **¿Qué pasa cuando dos temas se solapan significativamente?**
  - El sistema debe permitir que un contenido pertenezca a múltiples temas con scores de relevancia diferentes para cada tema

- **¿Cómo maneja el sistema cambios en estructura de APIs de terceros?**
  - El sistema debe validar estructura de respuestas de APIs y generar alertas cuando detecta cambios, continuando con datos disponibles

- **¿Qué sucede cuando un usuario consulta datos de un período sin recolección?**
  - El sistema debe retornar respuesta vacía con mensaje claro indicando que no hay datos disponibles para ese período

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST permitir crear, leer, actualizar y eliminar lineamientos (áreas temáticas a analizar)
- **FR-002**: System MUST permitir configurar para cada lineamiento: nombre, descripción, keywords, hashtags, y plataformas a monitorear
- **FR-003**: System MUST recolectar contenido público de YouTube, TikTok, Instagram y Facebook basado en keywords y hashtags de lineamientos
- **FR-004**: System MUST almacenar para cada contenido recolectado: plataforma de origen, título, descripción/texto, autor, fecha de publicación, URL, y métricas de engagement (vistas, likes, comentarios, shares)
- **FR-005**: System MUST ejecutar recolección de datos de manera programada (periódica) según frecuencia configurada por lineamiento
- **FR-006**: System MUST manejar límites de APIs de plataformas (rate limits) pausando y reanudando recolección automáticamente
- **FR-007**: System MUST identificar automáticamente temas (topics) en contenido recolectado sin intervención manual
- **FR-008**: System MUST extraer keywords relevantes para cada tema identificado
- **FR-009**: System MUST calcular sentiment (positivo/negativo/neutral) para cada tema en escala de -1 a +1
- **FR-010**: System MUST extraer menciones de lugares, organizaciones y personas del texto (Named Entity Recognition)
- **FR-011**: System MUST inferir demografía (ubicación, edad, género) cuando no está disponible directamente de APIs usando análisis de texto, metadata y modelos de ML
- **FR-012**: System MUST categorizar ubicación en tres niveles: país, región/estado, y ciudad
- **FR-013**: System MUST categorizar edad en rangos: 13-17, 18-24, 25-34, 35-44, 45-54, 55-64, 65+
- **FR-014**: System MUST categorizar género en: masculino, femenino, no binario, desconocido
- **FR-015**: System MUST calcular métricas agregadas por cada combinación de Plataforma → Ubicación → Edad → Género
- **FR-016**: System MUST identificar temas "trending" basado en velocidad de crecimiento de menciones (ej: >15% en 24 horas)
- **FR-017**: System MUST proporcionar API REST para consultar tendencias con jerarquía de 4 niveles: Plataforma → Ubicación → Edad → Género
- **FR-018**: System MUST permitir filtrar consultas por: plataforma, país, región, ciudad, rango de edad, género, fecha inicio, fecha fin, mínimo de menciones, solo trending
- **FR-019**: System MUST incluir en cada tema retornado: nombre, número de menciones, engagement total, sentiment promedio, keywords, hashtags, velocidad de crecimiento, y flag de trending
- **FR-020**: System MUST incluir ejemplos de contenido real para cada tema con toda su metadata
- **FR-021**: System MUST validar tendencias detectadas correlacionando con datos de Google Trends
- **FR-022**: System MUST identificar "gaps de contenido" (alto volumen de búsquedas, bajo contenido social)
- **FR-023**: System MUST autenticar usuarios vía API keys estáticas (cada cliente/organización recibe una API key única)
- **FR-024**: System MUST aplicar rate limiting por usuario/cliente para prevenir abuso
- **FR-025**: System MUST retener datos históricos por 1 semana (7 días - datos más antiguos se archivan o eliminan)
- **FR-026**: System MUST procesar contenido en español incluyendo variantes regionales (Colombia, México, Argentina, España)
- **FR-027**: System MUST generar alertas cuando un tema crece más de 50% en menciones en 24 horas
- **FR-028**: System MUST exportar resultados en formatos JSON y CSV
- **FR-029**: System MUST utilizar EXCLUSIVAMENTE herramientas, APIs y bibliotecas que sean gratuitas o que tengan free tiers suficientes (sin costos operacionales recurrentes de APIs de pago)

### Key Entities

- **Lineamiento**: Representa un área temática a analizar. Atributos: nombre, descripción, keywords (lista), hashtags (lista), plataformas activas (lista), frecuencia de recolección. Relación: tiene muchos contenidos recolectados y temas identificados.

- **Contenido Recolectado**: Representa una pieza de contenido de redes sociales. Atributos: plataforma de origen, ID externo, título, descripción/texto completo, autor, fecha de publicación, URL, métricas (vistas, likes, comentarios, shares), ubicación geográfica (país, región, ciudad), metadata adicional. Relación: pertenece a un lineamiento, puede estar asociado a múltiples temas.

- **Tema Identificado**: Representa un tema automáticamente descubierto por NLP. Atributos: nombre del tema, descripción, keywords que lo definen, métricas agregadas (menciones totales, engagement total, sentiment promedio), plataformas donde aparece, trending (booleano). Relación: pertenece a un lineamiento, está presente en múltiples contenidos.

- **Demografía por Tema**: Representa agregación de métricas demográficas para un tema. Atributos: plataforma, género (masculino/femenino/no_binario/desconocido), rango de edad, país, región, ciudad, métricas (interacciones totales, engagement promedio, sentiment promedio), porcentaje de participación. Relación: pertenece a un tema.

- **Tendencia (Serie Temporal)**: Representa la evolución temporal de un tema. Atributos: fecha y hora, menciones en ese período, engagement en ese período, usuarios únicos, velocidad de crecimiento (porcentaje). Relación: pertenece a un tema y plataforma.

- **Validación de Tendencia**: Representa correlación con datos de búsqueda. Atributos: fuente de validación (ej: Google Trends), volumen de búsquedas, correlación (porcentaje), regiones con alto interés, queries relacionados. Relación: pertenece a un tema.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El sistema puede recolectar y almacenar al menos 4,000 contenidos por día (1,000 por plataforma) para un lineamiento activo
- **SC-002**: El sistema identifica automáticamente entre 5-15 temas distintos por cada 1,000 contenidos analizados con precisión >70% (validado por revisión manual de muestra)
- **SC-003**: El sistema responde a consultas de tendencias en menos de 3 segundos para datasets de hasta 100,000 contenidos
- **SC-004**: El sistema infiere demografía (ubicación, edad, género) con precisión mínima de 65% para plataformas sin demografía directa (validado contra muestra con demografía conocida)
- **SC-005**: El sistema logra 95%+ de precisión en demografía para plataformas con datos directos (Facebook, Instagram)
- **SC-006**: Los usuarios pueden configurar un nuevo lineamiento y ver primeros datos recolectados en menos de 6 horas
- **SC-007**: El sistema maneja correctamente límites de APIs sin pérdida de datos, retomando recolección automáticamente cuando límites se reinician
- **SC-008**: El sistema identifica temas trending con al menos 2-4 semanas de anticipación comparado con tendencias mainstream (validado correlacionando con Google Trends)
- **SC-009**: El sistema procesa contenido en español de múltiples regiones sin degradación de precisión de NLP >10% entre regiones
- **SC-010**: Las consultas API retornan estructura JSON jerárquica de 4 niveles correctamente formateada en 100% de las respuestas
- **SC-011**: El sistema detecta y alerta sobre tendencias emergentes (>50% crecimiento) dentro de 6 horas de que el crecimiento ocurra
- **SC-012**: Los usuarios pueden completar análisis completo (configurar lineamiento, recolectar datos, consultar tendencias) en menos de 1 día de tiempo calendario
- **SC-013**: El sistema mantiene uptime >99% excluyendo mantenimiento programado
- **SC-014**: El sistema valida al menos 80% de tendencias detectadas contra Google Trends mostrando correlación >60%
- **SC-015**: Los reportes exportados contienen 100% de los datos mostrados en consultas web sin pérdida de información

## Assumptions

- **Data Availability**: Asumimos que las APIs de redes sociales mantienen endpoints públicos estables. Cambios significativos en APIs requerirán actualización de collectors.

- **Language**: El sistema está optimizado para español (incluyendo variantes regionales). Contenido en otros idiomas se marca como "no procesado" y puede soportarse en futuras versiones.

- **Public Content Only**: El sistema solo accede y analiza contenido público. Contenido privado o protegido está fuera del alcance.

- **Demographics Accuracy**: La precisión de demografía inferida (65%+) es aceptable para análisis de tendencias agregadas. Decisiones críticas de negocio deben validarse con fuentes adicionales.

- **Free Tools Only**: El sistema SOLO utilizará herramientas, bibliotecas y APIs que sean 100% gratuitas o que tengan capas gratuitas (free tiers) suficientes para el MVP. Esto incluye: Meta Graph API (Facebook/Instagram), YouTube Data API v3, Google Trends (pytrends), Reddit API (PRAW), TikTok Creative Center, NewsAPI.org (free tier), Talkwalker Alerts, Mastodon API, y bibliotecas open source (spaCy, BERT, BERTopic). NO se usarán servicios de pago como Twitter API oficial, Brandwatch, Sprinklr, etc.

- **Data Retention**: Retención de 1 semana (7 días) como especificado en FR-025. Este período permite análisis de tendencias semanales y detección de crecimiento. Para análisis de estacionalidad a largo plazo, futuras fases pueden extender retención.

- **Performance Baseline**: Métricas de performance (SC-003, SC-006, SC-011) asumen infraestructura estándar de servidor (no especificada intencionalmente para mantener spec agnóstica).

- **Content Volume**: Estimaciones de 4,000 contenidos/día se basan en un lineamiento activo de alcance medio. Lineamientos muy amplios o nichos muy pequeños pueden variar significativamente.

- **NLP Models**: Asumimos disponibilidad de modelos NLP pre-entrenados en español con calidad razonable. Afinar modelos puede mejorar precisión pero no es requisito del MVP.

- **User Authentication**: Se asume sistema de autenticación estándar (método a definir en FR-023). Multi-tenancy para múltiples organizaciones puede agregarse en futuras fases.

## Dependencies

- **External APIs**: El sistema depende de APIs de YouTube, TikTok, Instagram, Facebook, y Google Trends. Interrupción de cualquier API afecta recolección de esa plataforma pero no detiene el sistema completo.

- **NLP Libraries**: Requiere bibliotecas de procesamiento de lenguaje natural en español (tipo y versión no especificados para mantener spec agnóstica).

- **Search Validation Data**: Validación de tendencias depende de disponibilidad continua de Google Trends o servicio equivalente.

## Out of Scope

- **Content Creation**: El sistema analiza contenido existente pero no crea ni publica contenido en redes sociales.

- **Sentiment Analysis Profundo**: Análisis de sentiment es a nivel de tema completo. Análisis de emociones específicas (alegría, tristeza, enojo) está fuera del alcance del MVP.

- **Video/Image Analysis**: El sistema analiza texto (títulos, descripciones, comentarios) pero no procesa contenido visual o de audio dentro de videos o imágenes.

- **Real-time Streaming**: Recolección es periódica (cada N horas). Streaming en tiempo real continuo está fuera del alcance inicial.

- **Private/Protected Content**: Solo contenido público es accesible. Contenido detrás de autenticación (posts privados, stories privados) no se recolecta.

- **Competitive Intelligence Específica**: El sistema identifica tendencias generales, no rastrea competidores específicos o marcas (aunque esto podría agregarse como lineamiento futuro).

- **Automated Actions**: El sistema es puramente analítico. No toma acciones automáticas basadas en tendencias (ej: no publica contenido, no ajusta campañas de marketing automáticamente).

- **Platforms Beyond Core 4**: MVP cubre YouTube, TikTok, Instagram, Facebook como plataformas principales. Plataformas adicionales con APIs gratuitas (Reddit, Mastodon) pueden incluirse si hay capacidad. Twitter/X con API de pago ($100+/mes) está fuera del alcance - solo se considerarían alternativas gratuitas (ej: scraping con snscrape si es viable).

- **Paid APIs and Tools**: Cualquier servicio que requiera pago recurrente está fuera del alcance del MVP: Twitter API oficial ($100+/mes), Brandwatch ($1,000+/mes), Sprinklr ($2,000+/mes), Awario ($29+/mes), TwitterAPI.io ($0.15/1k tweets), Apify ($0.25/1k tweets), etc.
