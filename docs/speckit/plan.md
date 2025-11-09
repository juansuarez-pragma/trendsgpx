# Plan de Implementación: Sistema de Análisis de Tendencias en Redes Sociales

**Branch**: `001-social-trends-analysis` | **Fecha**: 2025-11-08 | **Spec**: [spec.md](./spec.md)
**Entrada**: Especificación de funcionalidad de `/specs/001-social-trends-analysis/spec.md`

**Nota**: Este plan es completado por el comando `/speckit.plan`. Ver `.specify/templates/commands/plan.md` para el flujo de trabajo de ejecución.

## Resumen

Construir un sistema de análisis de tendencias en redes sociales que identifica, analiza y reporta automáticamente temas en tendencia a través de YouTube, TikTok, Instagram y Facebook. El sistema recolecta contenido público basado en lineamientos configurados (palabras clave/hashtags), usa NLP para identificar temas, infiere demografía (ubicación, edad, género), y presenta insights a través de una API jerárquica (Plataforma → Ubicación → Edad → Género). Diferenciador clave: segmentación demográfica con jerarquía de 4 niveles. Restricción: Usar SOLO herramientas y APIs gratuitas (FR-029).

**Enfoque Técnico**: Arquitectura de microservicios con colectores por plataforma, procesamiento asíncrono con colas de tareas, pipeline NLP para modelado de temas y análisis de sentimientos, PostgreSQL para almacenamiento con TimescaleDB para series temporales, API REST con estructura de respuesta JSON jerárquica.

## Contexto Técnico

**Lenguaje/Versión**: Python 3.11+
**Dependencias Principales**: FastAPI, Celery, spaCy (NLP español), Transformers (BERT), BERTopic, pytrends, PRAW, Mastodon.py, facebook-sdk, google-api-python-client
**Almacenamiento**: PostgreSQL 15+ con extensión TimescaleDB (datos de series temporales)
**Testing**: pytest, pytest-asyncio, pytest-mock
**Plataforma Objetivo**: Servidor Linux (microservicios containerizados con Docker)
**Tipo de Proyecto**: Aplicación web (backend API REST + frontend opcional para dashboards)
**Objetivos de Rendimiento**:
- Respuesta API <3 segundos para 100k items de contenido (SC-003)
- Procesar 4,000 items de contenido/día por lineamiento (SC-001)
- Identificar 5-15 temas por 1,000 items (SC-002)
- Soportar recolección concurrente de 4 plataformas

**Restricciones**:
- **CRÍTICO**: Solo herramientas/APIs GRATUITAS (FR-029) - SIN servicios pagos
- Retención de datos de 1 semana (FR-025)
- Optimización para idioma español (FR-026)
- Límites de tasa por plataforma API
- Precisión de inferencia demográfica: 65% mínimo (SC-004), 95% para datos directos (SC-005)

**Escala/Alcance**:
- 4 plataformas primarias (YouTube, TikTok, Instagram, Facebook)
- Soporte para múltiples lineamientos simultáneamente
- ~28,000 items de contenido/semana por lineamiento (4,000/día × 7 días retención)
- 6 entidades clave (Lineamiento, Contenido, Tema, Demografia, Tendencia, Validacion)

## Verificación de Constitución

*GATE: Debe pasar antes de investigación Phase 0. Re-verificar después de diseño Phase 1.*

**Estado de Constitución del Proyecto**: No hay constitución personalizada definida para este proyecto.

**Mejores Prácticas por Defecto Aplicadas**:
- ✅ **Separación de Responsabilidades**: Arquitectura de microservicios con colectores, servicio NLP, servicio analytics
- ✅ **Testabilidad**: pytest para pruebas unitarias, de integración y de contrato
- ✅ **Diseño API-First**: API REST con especificación OpenAPI (Phase 1)
- ✅ **Claridad del Modelo de Datos**: Relaciones de entidades definidas en spec (Phase 1 formalizará)
- ✅ **Observabilidad**: Logging estructurado, endpoints de monitoreo
- ✅ **Solo Herramientas Gratuitas**: FR-029 impone restricción de cero costo

**Gates**:
- ✅ **Gate 1**: Spec tiene requisitos funcionales claros (29 FRs)
- ✅ **Gate 2**: Criterios de éxito son medibles (15 SCs)
- ✅ **Gate 3**: Restricción de herramientas gratuitas documentada (FR-029)
- ⚠️ **Gate 4**: Elecciones tecnológicas necesitan investigación (Phase 0)

**Estado**: PROCEDER a Phase 0 (Se necesita investigación para bibliotecas/patrones específicos)

## Estructura del Proyecto

### Documentación (esta funcionalidad)

```text
specs/001-social-trends-analysis/
├── plan.md              # Este archivo (salida comando /speckit.plan)
├── research.md          # Salida Phase 0 (comando /speckit.plan)
├── data-model.md        # Salida Phase 1 (comando /speckit.plan)
├── quickstart.md        # Salida Phase 1 (comando /speckit.plan)
├── contracts/           # Salida Phase 1 (comando /speckit.plan)
│   ├── openapi.yaml     # Especificación API REST
│   └── events.yaml      # Esquema de eventos async (tareas Celery)
└── tasks.md             # Salida Phase 2 (comando /speckit.tasks - AÚN NO creado)
```

### Código Fuente (raíz del repositorio)

```text
# Opción 2: Aplicación web (backend + frontend opcional)

backend/
├── src/
│   ├── models/              # Modelos SQLAlchemy (Lineamiento, Contenido, Tema, etc.)
│   ├── collectors/          # Colectores específicos por plataforma
│   │   ├── youtube.py
│   │   ├── reddit.py
│   │   ├── mastodon.py
│   │   ├── trends.py       # Google Trends
│   │   └── base.py         # Interfaz abstracta de colector
│   ├── nlp/                 # Pipeline de procesamiento NLP
│   │   ├── topic_modeling.py  # BERTopic
│   │   ├── sentiment.py       # Análisis de sentimientos
│   │   ├── ner.py             # Reconocimiento de Entidades Nombradas
│   │   └── demographics.py    # Inferencia demográfica
│   ├── services/            # Lógica de negocio
│   │   ├── lineamientos.py
│   │   ├── analytics.py
│   │   ├── trends.py
│   │   └── validation.py   # Validación Google Trends
│   ├── api/                 # Rutas FastAPI
│   │   ├── lineamientos.py
│   │   ├── tendencias.py
│   │   ├── auth.py         # Autenticación API key
│   │   └── main.py         # App FastAPI
│   ├── tasks/               # Tareas Celery
│   │   ├── collection.py   # Tareas de recolección periódica
│   │   ├── processing.py   # Tareas de procesamiento NLP
│   │   └── alerts.py       # Alertas de tendencias
│   └── utils/
│       ├── cache.py        # Wrapper de caché Redis
│       └── rate_limit.py   # Limitación de tasa por plataforma

├── tests/
│   ├── contract/           # Pruebas de contrato API
│   ├── integration/        # Pruebas de integración (DB, APIs externas)
│   └── unit/               # Pruebas unitarias por módulo

├── alembic/                # Migraciones de base de datos
├── docker-compose.yml      # Entorno de desarrollo local
└── pyproject.toml          # Dependencias Python

frontend/ (opcional - fase futura)
├── src/
│   ├── components/         # Componentes React/Vue
│   ├── pages/              # Páginas de dashboard
│   └── services/           # Clientes API
└── tests/

scripts/
├── setup_apis.sh           # Configurar API keys
└── seed_data.sh            # Poblar lineamientos de prueba
```

**Decisión de Estructura**: Aplicación web con backend FastAPI. Frontend es opcional/fase futura - MVP se enfoca en API REST. Patrón de microservicios con colectores como módulos independientes, orquestados por Celery para procesamiento asíncrono.

## Seguimiento de Complejidad

> **Completar SOLO si la Verificación de Constitución tiene violaciones que deben justificarse**

Sin violaciones de constitución. Mejores prácticas por defecto aplicadas.

---

## Phase 0: Investigación y Decisiones Tecnológicas

**Estado**: ✅ COMPLETO

### Tareas de Investigación - Todas Completas

Todas las incógnitas técnicas han sido investigadas y documentadas en [research.md](./research.md):

1. ✅ **Verificación de Acceso a APIs Gratuitas**
   - **Hallazgo**: YouTube + Reddit + Mastodon son viables (ELIMINAR TikTok, Instagram, Facebook)
   - **Capacidad**: 149,000+ peticiones/día combinadas (supera ampliamente el objetivo de 4,000)
   - **Estado**: COMPLETO - Ver research.md Sección 1-5

2. ✅ **Bibliotecas NLP para Español**
   - **Hallazgo**: RoBERTuito (Spanish BERT), BERTopic, pysentimiento
   - **Rendimiento**: <10% degradación entre regiones de español
   - **Estado**: COMPLETO - Cubierto en research.md

3. ✅ **Enfoques de Inferencia Demográfica**
   - **Hallazgo**: Enfoque multi-método (NER + ML + heurísticas)
   - **Precisión**: 65-75% alcanzable (cumple SC-004)
   - **Estado**: COMPLETO - Ver research.md "Estrategia de Datos Demográficos"

4. ✅ **Patrón de Almacenamiento de Series Temporales**
   - **Hallazgo**: TimescaleDB con chunks de 7 días, agregados continuos
   - **Rendimiento**: Consultas <3s vía exclusión de chunks e índices
   - **Estado**: COMPLETO - Investigación realizada

5. ✅ **Estrategia de Limitación de Tasa de API**
   - **Hallazgo**: PyrateLimiter + Redis + algoritmo Sliding Window
   - **Patrón**: Colas Celery separadas por API con backoff exponencial
   - **Estado**: COMPLETO - Ver research.md Apéndice

6. ✅ **Arquitectura de Tareas Celery**
   - **Hallazgo**: Granularidad híbrida - Colectores por lotes (50), NLP individual, analytics por lotes
   - **Patrón**: chain(group(collectors), chord(nlp_tasks, aggregation_callback))
   - **Estado**: COMPLETO - Ver research.md Tarea de Investigación #6

### Decisiones Tecnológicas Clave

Basado en hallazgos de investigación:

**Cambios de Plataforma** (Crítico):
- ❌ ELIMINAR: TikTok, Instagram, Facebook (APIs no viables/accesibles)
- ✅ USAR: YouTube Data API v3, Reddit API (PRAW), Mastodon API, Google Trends

**Stack NLP para Español**:
- RoBERTuito: BERT para español (entrenado con 600M tweets en español)
- BERTopic: Modelado de temas con embeddings multilingües
- pysentimiento: Análisis de sentimientos para español
- spaCy: NER español y características lingüísticas

**Limitación de Tasa**:
- PyrateLimiter con backend Redis
- Algoritmo Sliding Window para seguimiento de cuotas
- Colas Celery separadas: youtube_queue, reddit_queue, mastodon_queue, nlp_queue, analytics_queue

**Arquitectura Celery**:
- Colectores: Lotes de 50 items, gevent/100 workers, prefetch=4
- NLP: Item individual, prefork/8 workers, prefetch=1
- Analytics: Procesamiento por lotes, prefork/4 workers, prefetch=2

**TimescaleDB**:
- Chunks de 7 días (alineado con retención FR-025)
- Agregados continuos para cálculos de tendencias horarias/diarias
- Hypertables para tabla tendencias

---

## Phase 1: Artefactos de Diseño

**Estado**: ✅ COMPLETO

### Entregables - Todos Completos

Todos los artefactos de diseño han sido creados y validados:

1. ✅ **[data-model.md](./data-model.md)**:
   - Diagrama ER completo con 6 entidades
   - Esquema PostgreSQL + TimescaleDB
   - Política de retención de 7 días (FR-025)
   - Optimización de rendimiento para consultas <3s (SC-003)
   - Matriz de validación mapeando requisitos a implementación

2. ✅ **[contracts/openapi.yaml](./contracts/openapi.yaml)**:
   - Especificación API REST (OpenAPI 3.0.3)
   - 10 endpoints cubriendo lineamientos, tendencias, validación, exportación
   - Estructura de respuesta jerárquica (4 niveles: Plataforma → Ubicación → Edad → Género)
   - Autenticación por API key (FR-023)
   - Respuestas de error y reglas de validación

3. ✅ **[contracts/events.yaml](./contracts/events.yaml)**:
   - 15 definiciones de tareas Celery
   - Organización de colas (5 colas)
   - Patrones Canvas (chain, group, chord)
   - Estrategias de reintento y manejo de errores
   - Patrones Circuit breaker y DLQ
   - Ejemplos de flujo de trabajo completos

4. ✅ **[quickstart.md](./quickstart.md)**:
   - Guía completa de configuración para desarrolladores (45-60 min de setup)
   - Configuración de API keys para YouTube, Reddit, Mastodon
   - Entorno de desarrollo local (manual + Docker)
   - Inicialización de base de datos con TimescaleDB
   - Instrucciones de pruebas
   - Guía de resolución de problemas

### Resumen de Arquitectura

**Stack Tecnológico Confirmado**:
- **Backend**: FastAPI + Uvicorn
- **Base de Datos**: PostgreSQL 15 + TimescaleDB (hypertables, agregados continuos)
- **Cola de Tareas**: Celery + Redis
- **NLP**: RoBERTuito, BERTopic, pysentimiento, spaCy
- **APIs**: YouTube Data API v3, Reddit API (PRAW), Mastodon API, pytrends
- **Limitación de Tasa**: PyrateLimiter + Redis sliding window
- **Monitoreo**: Prometheus + Grafana + Flower

**Modelo de Datos**:
- 6 entidades core: Lineamiento, Contenido, Tema, Demografia, Tendencia, Validacion
- Hypertable TimescaleDB para tendencias (chunks de 7 días)
- Agregados continuos para tendencias horarias/diarias
- Política de retención automática de 7 días

**Diseño de API**:
- API RESTful con respuesta jerárquica de 4 niveles
- Autenticación por API key (claves estáticas por cliente)
- Formatos de exportación: JSON, CSV, Excel
- Tiempo de respuesta <3s para 100k items (vía índices + agregados)

**Procesamiento Asíncrono**:
- 5 colas especializadas (youtube, reddit, mastodon, nlp, analytics)
- Granularidad híbrida: Colectores por lotes (50), NLP individual, analytics por lotes
- Patrón Canvas: chain(group(collectors), chord(nlp, analytics))
- Tareas programadas: Recolección (6h), Detección tendencias (30min), Validación (diaria)

---

## Phase 2: Desglose de Tareas

**Estado**: PENDIENTE (creado por comando `/speckit.tasks`, no `/speckit.plan`)

Esta fase generará `tasks.md` con tareas de implementación ordenadas por dependencias.

---

## Notas

- **Restricción de Herramientas Gratuitas**: Todas las elecciones tecnológicas deben tener costo recurrente cero (free tiers o código abierto)
- **Optimización para Español**: Pipeline NLP debe manejar español de múltiples regiones (Colombia, México, Argentina, España)
- **Retención de 1 Semana**: Diseño de base de datos debe soportar archivado/eliminación eficiente después de 7 días
- **API Jerárquica**: Estructura de respuesta Plataforma → Ubicación → Edad → Género es no-negociable (FR-017)
