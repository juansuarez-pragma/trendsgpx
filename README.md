# TrendsGPX Backend 🚀

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)
![TimescaleDB](https://img.shields.io/badge/TimescaleDB-enabled-orange.svg)
![Speckit](https://img.shields.io/badge/docs-Speckit-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

**Sistema de Análisis de Tendencias en Redes Sociales con Segmentación Demográfica y NLP**

[Características](#características) •
[Instalación](#instalación) •
[API](#documentación-de-api) •
[Arquitectura](#arquitectura) •
[Contribuir](#contribuir)

</div>

---

## 📋 Tabla de Contenidos

- [Características](#características)
- [Documentación](#documentación)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
  - [Instalación con Docker](#instalación-con-docker-recomendado)
  - [Instalación Manual](#instalación-manual)
- [Configuración](#configuración)
- [Uso](#uso)
- [Documentación de API](#documentación-de-api)
- [Arquitectura](#arquitectura)
- [Stack Tecnológico](#stack-tecnológico)
- [Tareas Programadas](#tareas-programadas)
- [Testing](#testing)
- [Despliegue](#despliegue)
- [Contribuir](#contribuir)
- [Licencia](#licencia)

## ✨ Características

### 🔄 Recolección Automática de Contenido
- **YouTube**: Videos, comentarios, estadísticas (views, likes, comments)
- **Reddit**: Posts, comentarios, scoring, subreddits en español
- **Mastodon**: Toots, contexto, hashtags trending
- Rate limiting automático por plataforma
- Deduplicación de contenido

### 🤖 Análisis NLP Avanzado para Español
- **spaCy** (es_core_news_md): Named Entity Recognition (NER), extracción de keywords
- **RoBERTuito/BERTopic**: Topic modeling con embeddings en español
- **pysentimiento**: Análisis de sentimiento (positivo/neutro/negativo)
- Procesamiento batch optimizado

### 📊 Segmentación Demográfica (4 Niveles)
```
Plataforma → Ubicación (País/Ciudad) → Edad → Género
```
- Detección automática de ubicación desde texto y metadata
- Clustering demográfico inteligente
- Queries jerárquicas optimizadas

### ✅ Validación de Tendencias
- Integración con **Google Trends** (pytrends)
- Validación cruzada de popularidad
- Métricas de confianza

### 📁 Exportación Multi-Formato
- JSON (estructurado)
- CSV (análisis)
- Excel (reportes)

### ⚡ Procesamiento Asíncrono
- **Celery** con 5 colas especializadas:
  - `collectors`: Recolección de contenido
  - `nlp`: Procesamiento NLP
  - `analytics`: Análisis de tendencias
  - `validation`: Validación con Google Trends
  - `default`: Tareas generales
- Workers escalables horizontalmente
- Retry automático con exponential backoff

### 💾 Base de Datos Optimizada
- **PostgreSQL 15** + **TimescaleDB** para series temporales
- Hypertables con chunks de 7 días
- Continuous aggregates (hora/día)
- Retention policy automática
- Full-text search en español

## 📚 Documentación

Este proyecto incluye documentación completa desarrollada con la metodología **Speckit**.

### 📖 Documentación Principal

| Documento | Descripción | Tamaño |
|-----------|-------------|--------|
| [📋 Índice de Documentación](docs/README.md) | Guía completa de toda la documentación | - |
| [📝 Especificación Funcional](docs/speckit/spec.md) | User stories, requisitos y criterios de aceptación | 28 KB |
| [🏗️ Plan de Implementación](docs/speckit/plan.md) | Arquitectura técnica y stack tecnológico | 14 KB |
| [✅ Lista de Tareas](docs/speckit/tasks.md) | 148 tareas organizadas en 5 fases (100% completadas) | 39 KB |
| [🗄️ Modelo de Datos](docs/speckit/data-model.md) | Esquema de base de datos completo | 23 KB |
| [🔬 Investigación Técnica](docs/speckit/research.md) | Análisis de APIs, bibliotecas y arquitectura | 77 KB |
| [🤖 Investigación NLP](docs/speckit/nlp-research.md) | Deep dive en NLP para español | 40 KB |
| [🚀 Guía de Inicio Rápido](docs/speckit/quickstart.md) | Setup para desarrolladores | 16 KB |

### 📄 Contratos de API

| Documento | Descripción |
|-----------|-------------|
| [OpenAPI Specification](docs/speckit/contracts/openapi.yaml) | 14 endpoints REST documentados |
| [Celery Events](docs/speckit/contracts/events.yaml) | 11 tareas asíncronas especificadas |

### 🔧 Metodología Speckit

Este proyecto fue construido usando **Speckit**, una metodología estructurada que garantiza:

- ✅ **Trazabilidad completa**: Desde requisitos hasta código
- ✅ **Documentación actualizada**: Sincronizada con la implementación
- ✅ **Reproducibilidad**: El proyecto puede reconstruirse desde los docs
- ✅ **Onboarding rápido**: Nuevos desarrolladores pueden entender el sistema completo

**Comandos Speckit disponibles** (ver [docs/.claude/commands/](docs/.claude/commands/)):
- `/speckit.specify` - Crear/actualizar especificación
- `/speckit.plan` - Diseñar arquitectura
- `/speckit.tasks` - Generar lista de tareas
- `/speckit.implement` - Ejecutar implementación
- `/speckit.analyze` - Verificar consistencia

### 📊 Estadísticas de Documentación

```
📦 31 archivos de documentación
📝 ~240,000 caracteres
✅ 148 tareas (100% completadas)
🎯 5 fases implementadas
📖 2 contratos de API (OpenAPI + Events)
```

## 📦 Requisitos

### Requisitos de Sistema
- Python 3.11 o superior
- PostgreSQL 15+ con extensión TimescaleDB
- Redis 6.0+
- 2GB RAM mínimo (4GB recomendado)
- Docker & Docker Compose (para instalación rápida)

### API Keys Requeridas
- **YouTube Data API v3**: [Obtener aquí](https://console.cloud.google.com/)
- **Reddit API**: [Obtener aquí](https://www.reddit.com/prefs/apps)
- **Mastodon API**: Obtener en tu instancia → Preferencias → Development

## 🚀 Instalación

### Instalación con Docker (Recomendado)

#### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/trendsgpx-backend.git
cd trendsgpx-backend
```

#### 2. Configurar variables de entorno
```bash
cp .env.example .env
nano .env  # o tu editor preferido
```

Edita `.env` con tus API keys:
```env
# Database
DATABASE_URL=postgresql://trendsgpx:password@postgres:5432/trendsgpx

# Redis
REDIS_URL=redis://redis:6379/0

# API Keys - Plataformas
YOUTUBE_API_KEY=tu_youtube_api_key_aqui
REDDIT_CLIENT_ID=tu_reddit_client_id
REDDIT_CLIENT_SECRET=tu_reddit_client_secret
MASTODON_ACCESS_TOKEN=tu_mastodon_access_token

# Security
API_KEY=cambia-esto-en-produccion

# Configuración
LOG_LEVEL=INFO
```

#### 3. Iniciar servicios con Docker Compose
```bash
docker-compose up -d
```

Esto inicia automáticamente:
- ✅ PostgreSQL 15 + TimescaleDB (puerto 5432)
- ✅ Redis (puerto 6379)
- ✅ FastAPI Backend (puerto 8000)
- ✅ Celery Workers (collectors, NLP, analytics)
- ✅ Celery Beat (scheduler)
- ✅ Flower (monitoring - puerto 5555)

#### 4. Ejecutar migraciones
```bash
docker-compose exec api alembic upgrade head
```

#### 5. Verificar instalación
```bash
curl http://localhost:8000/health
```

Respuesta esperada:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "service": "TrendsGPX API"
}
```

### Instalación Manual

#### 1. Instalar dependencias del sistema
```bash
# macOS
brew install postgresql@15 redis

# Ubuntu/Debian
sudo apt-get update
sudo apt-get install postgresql-15 postgresql-15-timescaledb redis-server

# Habilitar TimescaleDB
sudo -u postgres psql -c "CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;"
```

#### 2. Instalar Poetry
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

#### 3. Instalar dependencias de Python
```bash
poetry install
```

#### 4. Descargar modelo de spaCy
```bash
poetry run python -m spacy download es_core_news_md
```

#### 5. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

#### 6. Ejecutar migraciones
```bash
poetry run alembic upgrade head
```

#### 7. Iniciar servicios

**Terminal 1 - FastAPI:**
```bash
poetry run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Celery Worker (Collectors):**
```bash
poetry run celery -A src.celery_app worker -Q collectors -l info
```

**Terminal 3 - Celery Worker (NLP):**
```bash
poetry run celery -A src.celery_app worker -Q nlp -l info
```

**Terminal 4 - Celery Worker (Analytics):**
```bash
poetry run celery -A src.celery_app worker -Q analytics -l info
```

**Terminal 5 - Celery Beat:**
```bash
poetry run celery -A src.celery_app beat -l info
```

## ⚙️ Configuración

### Variables de Entorno Principales

| Variable | Descripción | Default |
|----------|-------------|---------|
| `DATABASE_URL` | URL de PostgreSQL | `postgresql://trendsgpx:password@localhost:5432/trendsgpx` |
| `REDIS_URL` | URL de Redis | `redis://localhost:6379/0` |
| `API_KEY` | API key para autenticación | `dev-api-key-change-in-production` |
| `YOUTUBE_API_KEY` | API key de YouTube | - |
| `REDDIT_CLIENT_ID` | Client ID de Reddit | - |
| `REDDIT_CLIENT_SECRET` | Client Secret de Reddit | - |
| `MASTODON_ACCESS_TOKEN` | Access token de Mastodon | - |
| `LOG_LEVEL` | Nivel de logging | `INFO` |
| `TRENDING_GROWTH_THRESHOLD` | Umbral de crecimiento (0.5 = 50%) | `0.5` |
| `TRENDING_MIN_MENTIONS` | Mínimo de menciones para tendencia | `10` |
| `DATA_RETENTION_DAYS` | Días de retención de datos | `7` |

Ver `.env.example` para la lista completa.

### Rate Limiting por Plataforma

| Plataforma | Límite | Período |
|------------|--------|---------|
| YouTube | 10,000 unidades | 1 día |
| Reddit | 60 requests | 1 minuto |
| Mastodon | 300 requests | 5 minutos |

Configurables via variables de entorno.

## 📚 Uso

### Flujo de Trabajo Básico

#### 1. Crear un lineamiento
```bash
curl -X POST "http://localhost:8000/lineamientos/" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: tu-api-key" \
  -d '{
    "nombre": "Tecnología IA 2025",
    "keywords": ["IA", "inteligencia artificial", "GPT", "machine learning"],
    "plataformas": ["youtube", "reddit", "mastodon"]
  }'
```

#### 2. Recolectar contenido (manual)
```bash
curl -X POST "http://localhost:8000/collect/lineamiento/{lineamiento_id}?hours_back=24" \
  -H "X-API-Key: tu-api-key"
```

O esperar la recolección automática (cada 30 minutos).

#### 3. Consultar tendencias
```bash
curl "http://localhost:8000/tendencias/?hours_back=24&solo_activas=true" \
  -H "X-API-Key: tu-api-key"
```

#### 4. Obtener tendencias agregadas
```bash
curl "http://localhost:8000/tendencias/agregadas?top_n=10" \
  -H "X-API-Key: tu-api-key"
```

#### 5. Ver estructura jerárquica
```bash
curl "http://localhost:8000/tendencias/jerarquicas?hours_back=24" \
  -H "X-API-Key: tu-api-key"
```

## 📖 Documentación de API

### Documentación Interactiva

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpoints Principales

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| **Lineamientos** |||
| POST | `/lineamientos/` | Crear lineamiento |
| GET | `/lineamientos/` | Listar lineamientos |
| GET | `/lineamientos/{id}` | Obtener lineamiento |
| PUT | `/lineamientos/{id}` | Actualizar lineamiento |
| DELETE | `/lineamientos/{id}` | Eliminar lineamiento (soft delete) |
| POST | `/lineamientos/{id}/activate` | Reactivar lineamiento |
| **Recolección** |||
| POST | `/collect/lineamiento/{id}` | Recolectar todas las plataformas |
| POST | `/collect/lineamiento/{id}/platform/{platform}` | Recolectar plataforma específica |
| POST | `/collect/all` | Recolectar todos los lineamientos |
| GET | `/collect/task/{task_id}` | Estado de tarea |
| **Tendencias** |||
| GET | `/tendencias/` | Listar tendencias con filtros |
| GET | `/tendencias/agregadas` | Tendencias agregadas por tema |
| GET | `/tendencias/jerarquicas` | Estructura jerárquica completa |

Ver [API_DOCUMENTATION.md](API_DOCUMENTATION.md) para la documentación completa con ejemplos.

## 🏗️ Arquitectura

### Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────────┐
│                         FastAPI REST API                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Lineamientos │  │  Recolección │  │  Tendencias  │          │
│  │   (CRUD)     │  │   (Trigger)  │  │   (Query)    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Celery Workers                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Collectors  │  │     NLP      │  │  Analytics   │          │
│  │  (YouTube,   │  │  (spaCy,     │  │ (Tendencias, │          │
│  │   Reddit,    │  │  sentiment,  │  │  Validación) │          │
│  │  Mastodon)   │  │  BERTopic)   │  │              │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              PostgreSQL 15 + TimescaleDB + Redis                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Tables     │  │ Hypertables  │  │  Task Queue  │          │
│  │ Lineamientos │  │  Tendencias  │  │   (Redis)    │          │
│  │  Contenido   │  │  Aggregates  │  │              │          │
│  │    Temas     │  │              │  │              │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

### Flujo de Datos

1. **Recolección** (cada 30 min)
   - Celery Beat dispara `collect_all_lineamientos`
   - Workers de `collectors` queue recolectan en paralelo
   - Contenido guardado en `contenido_recolectado`

2. **Procesamiento NLP** (cada hora)
   - Celery Beat dispara `process_pending_content`
   - Workers de `nlp` queue procesan con spaCy/sentiment
   - Temas guardados en `temas_identificados`
   - Demographics en `demografia`

3. **Análisis de Tendencias** (cada hora)
   - Celery Beat dispara `analyze_trends`
   - Workers de `analytics` queue calculan métricas
   - Tendencias en tabla `tendencias` (hypertable)

4. **Validación** (cada 6 horas)
   - Celery Beat dispara `validate_trends`
   - Workers consultan Google Trends
   - Validaciones en `validacion_tendencias`

## 🛠️ Stack Tecnológico

### Backend
- **FastAPI** 0.104+ - Framework web asíncrono
- **Pydantic** 2.0+ - Validación de datos
- **SQLAlchemy** 2.0+ - ORM
- **Alembic** 1.13+ - Migraciones de base de datos

### Procesamiento Asíncrono
- **Celery** 5.3+ - Task queue
- **Redis** 6.0+ - Message broker

### Base de Datos
- **PostgreSQL** 15+
- **TimescaleDB** - Extensión para series temporales

### NLP
- **spaCy** 3.7+ con modelo `es_core_news_md`
- **BERTopic** 0.16+ - Topic modeling
- **sentence-transformers** - Embeddings (RoBERTuito)
- **pysentimiento** 0.7+ - Análisis de sentimiento en español

### APIs Externas
- **google-api-python-client** - YouTube Data API v3
- **praw** 7.7+ - Reddit API
- **Mastodon.py** 1.8+ - Mastodon API
- **pytrends** 4.9+ - Google Trends (unofficial)

### Herramientas
- **Poetry** - Gestión de dependencias
- **Docker** & **Docker Compose** - Containerización
- **pytest** - Testing
- **Flower** - Monitoring de Celery

## ⏰ Tareas Programadas

| Tarea | Frecuencia | Descripción |
|-------|------------|-------------|
| `collect_all_lineamientos` | Cada 30 min | Recolecta contenido de todas las plataformas |
| `process_pending_content` | Cada hora (en punto) | Procesa contenido con NLP |
| `analyze_trends` | Cada hora (min 15) | Analiza tendencias y calcula métricas |
| `validate_trends` | Cada 6 horas (min 30) | Valida tendencias con Google Trends |
| `cleanup_old_data` | Diariamente (3:00 AM) | Limpia datos antiguos según retention policy |

## 🧪 Testing

### Ejecutar tests
```bash
# Con Poetry
poetry run pytest

# Con coverage
poetry run pytest --cov=src --cov-report=html

# Tests específicos
poetry run pytest tests/test_lineamientos.py -v
```

### Test Coverage Actual
- **Lineamientos**: 18 tests (CRUD completo)
- **Collectors**: Tests pendientes
- **NLP**: Tests pendientes
- **Analytics**: Tests pendientes

## 🚢 Despliegue

### Docker Production

1. **Build imagen**
```bash
docker build -t trendsgpx-backend:latest .
```

2. **Configurar variables de entorno producción**
```bash
cp .env.example .env.production
# Editar con valores de producción
```

3. **Deploy con docker-compose**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Consideraciones de Producción

- ✅ Cambiar `API_KEY` en `.env`
- ✅ Usar PostgreSQL gestionado (AWS RDS, Google Cloud SQL)
- ✅ Configurar Redis con persistencia
- ✅ Configurar logs centralizados (ELK, Datadog)
- ✅ Configurar monitoring (Prometheus + Grafana)
- ✅ Configurar backups automáticos de PostgreSQL
- ✅ Usar HTTPS con certificado SSL
- ✅ Configurar rate limiting en API Gateway
- ✅ Escalar workers de Celery horizontalmente según carga

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### Guías de Contribución

- Seguir PEP 8 para código Python
- Agregar tests para nuevas funcionalidades
- Actualizar documentación según sea necesario
- Usar commits descriptivos

## 📝 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 👥 Autores

- **Juan Suarez** - *Desarrollo Inicial* - [@juansuarez-pragma](https://github.com/juansuarez-pragma)

## 🙏 Agradecimientos

- FastAPI por el excelente framework
- spaCy por las herramientas de NLP
- TimescaleDB por la optimización de series temporales
- Comunidad de Python/FastAPI

## 📞 Contacto

- GitHub Issues: [https://github.com/tu-usuario/trendsgpx-backend/issues](https://github.com/tu-usuario/trendsgpx-backend/issues)
- Email: tu-email@example.com

---

<div align="center">
Hecho con ❤️ usando FastAPI, spaCy y TimescaleDB
</div>
