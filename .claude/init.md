# TrendsGPX Backend - Configuración de Claude Code

## 🎯 Resumen del Proyecto

**TrendsGPX Backend** es un sistema de análisis de tendencias en redes sociales que identifica, analiza y reporta temas trending con segmentación demográfica detallada (Plataforma → Ubicación → Edad → Género).

### Stack Tecnológico
- **Framework**: FastAPI 0.104+
- **Base de Datos**: PostgreSQL 15+ con TimescaleDB
- **Queue**: Celery 5.3+ con Redis
- **NLP**: spaCy, BERTopic, pysentimiento, RoBERTuito
- **APIs**: YouTube Data API v3, Reddit API (PRAW), Mastodon API, Google Trends

### Características Clave
- ✅ Recolección multi-plataforma (YouTube, Reddit, Mastodon)
- ✅ Procesamiento NLP en español (Colombia, México, Argentina)
- ✅ Segmentación demográfica 4 niveles
- ✅ Análisis de tendencias con TimescaleDB
- ✅ API REST completa con 14 endpoints
- ✅ Tareas asíncronas con Celery (4 colas especializadas)

## 📁 Estructura del Proyecto

```
backend/
├── src/
│   ├── api/              # FastAPI application
│   │   ├── main.py       # App principal
│   │   ├── auth.py       # Autenticación API key
│   │   └── routes/       # Endpoints (lineamientos, collector, tendencias)
│   ├── models/           # SQLAlchemy ORM models (6 entidades)
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Lógica de negocio
│   ├── collectors/       # Recolectores (YouTube, Reddit, Mastodon)
│   ├── nlp/              # Servicios NLP (spaCy, sentiment, topics)
│   ├── tasks/            # Tareas Celery (collector, nlp, analytics)
│   ├── utils/            # Utilidades (config, logging, rate_limiter)
│   └── celery_app.py     # Configuración Celery
├── alembic/              # Migraciones de base de datos (10 migraciones)
├── tests/                # Tests con pytest
├── docs/                 # Documentación Speckit
│   ├── speckit/          # Artefactos de diseño
│   │   ├── spec.md       # Especificación funcional (28 KB)
│   │   ├── plan.md       # Plan de implementación (14 KB)
│   │   ├── tasks.md      # 148 tareas (100% completadas)
│   │   ├── data-model.md # Modelo de datos (23 KB)
│   │   ├── research.md   # Investigación de APIs (77 KB)
│   │   ├── nlp-research.md # Investigación NLP (40 KB)
│   │   ├── quickstart.md # Guía de inicio rápido
│   │   └── contracts/    # OpenAPI y eventos Celery
│   └── README.md         # Índice de documentación
├── docker-compose.yml    # Stack completo (postgres, redis, api, celery)
├── pyproject.toml        # Dependencias con Poetry
└── README.md             # README principal del proyecto
```

## 🧠 Metodología Speckit

Este proyecto fue construido usando **Speckit**, una metodología estructurada de desarrollo:

### Comandos Disponibles
- `/speckit.specify` - Crear/actualizar especificación funcional
- `/speckit.plan` - Diseñar arquitectura técnica
- `/speckit.tasks` - Generar lista de tareas implementables
- `/speckit.implement` - Ejecutar implementación
- `/speckit.analyze` - Verificar consistencia entre artefactos
- `/speckit.clarify` - Identificar áreas poco especificadas
- `/speckit.checklist` - Generar checklists de validación

### Documentación Clave
1. **docs/speckit/spec.md** - Especificación funcional con 9 user stories
2. **docs/speckit/plan.md** - Plan técnico y decisiones de arquitectura
3. **docs/speckit/tasks.md** - 148 tareas organizadas en 5 fases
4. **docs/speckit/data-model.md** - Esquema de base de datos completo
5. **docs/speckit/research.md** - Investigación de APIs de plataformas
6. **docs/speckit/nlp-research.md** - Investigación de modelos NLP para español

## 🔧 Configuración del Entorno

### Variables de Entorno Requeridas (.env)
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/trendsgpx
POSTGRES_USER=trendsgpx_user
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=trendsgpx

# Redis
REDIS_URL=redis://localhost:6379/0

# API Keys
YOUTUBE_API_KEY=your_youtube_api_key
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
MASTODON_ACCESS_TOKEN=your_mastodon_token
MASTODON_API_BASE_URL=https://mastodon.social

# App Config
API_KEY=dev-api-key-change-in-production
LOG_LEVEL=INFO
CORS_ORIGINS=["http://localhost:3000"]

# Rate Limiting
YOUTUBE_QUOTA_LIMIT=10000
REDDIT_RATE_LIMIT=60
MASTODON_RATE_LIMIT=300

# Trending Thresholds
MIN_MENTIONS_FOR_TREND=10
GROWTH_RATE_THRESHOLD=0.5
DATA_RETENTION_DAYS=7
```

## 🚀 Comandos Útiles

### Desarrollo Local
```bash
# Instalar dependencias
poetry install

# Descargar modelo spaCy
python -m spacy download es_core_news_md

# Ejecutar migraciones
alembic upgrade head

# Iniciar API
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Iniciar Celery worker
celery -A src.celery_app worker --loglevel=info -Q collectors,nlp,analytics

# Iniciar Celery beat (tareas programadas)
celery -A src.celery_app beat --loglevel=info

# Monitorear Celery (Flower)
celery -A src.celery_app flower --port=5555
```

### Con Docker
```bash
# Iniciar todo el stack
docker-compose up -d

# Ver logs
docker-compose logs -f api
docker-compose logs -f celery_worker

# Ejecutar migraciones
docker-compose exec api alembic upgrade head

# Detener todo
docker-compose down
```

### Testing
```bash
# Ejecutar todos los tests
pytest

# Con cobertura
pytest --cov=src --cov-report=html

# Solo tests de lineamientos
pytest tests/test_lineamientos.py -v
```

## 📊 Modelo de Datos

### 6 Entidades Principales

1. **lineamientos** - Configuración de búsqueda
   - keywords (JSONB), plataformas (JSONB), activo (Boolean)

2. **contenido_recolectado** - Contenido de redes sociales
   - plataforma, plataforma_id, contenido_texto, metadata (JSONB)
   - Índice full-text search en español

3. **temas_identificados** - Temas extraídos con NLP
   - tema_nombre, keywords (JSONB), probabilidad

4. **demografia** - Segmentación demográfica
   - ubicacion, edad_rango, genero, inferido (Boolean)

5. **tendencias** - Serie temporal de tendencias
   - Hypertable de TimescaleDB (particionado por fecha_hora)
   - Composite PRIMARY KEY (fecha_hora, tema_id, plataforma, ubicacion, edad_rango, genero)
   - Continuous aggregates para agregaciones horarias/diarias

6. **validacion_tendencias** - Validación con Google Trends
   - volumen_busquedas, correlacion

## 🔄 Flujo de Trabajo

### 1. Crear Lineamiento
```bash
POST /lineamientos/
{
  "nombre": "Tecnología IA",
  "keywords": ["IA", "inteligencia artificial"],
  "plataformas": ["youtube", "reddit"]
}
```

### 2. Recolectar Contenido (Automático cada 30 min)
```bash
POST /collect/lineamiento/{id}?hours_back=24
```
→ Dispara tareas Celery en cola `collectors`

### 3. Procesamiento NLP (Automático cada hora)
- Tarea `process_pending_content` en cola `nlp`
- Extrae entidades, keywords, sentimiento
- Crea registros en `temas_identificados` y `demografia`

### 4. Análisis de Tendencias (Automático cada hora)
- Tarea `analyze_trends` en cola `analytics`
- Calcula volumen, crecimiento, marca como tendencia
- Inserta en hypertable `tendencias`

### 5. Validación con Google Trends (Cada 6 horas)
- Tarea `validate_trends` en cola `validation`
- Correlaciona con volumen de búsquedas

### 6. Consultar Tendencias
```bash
GET /tendencias/?hours_back=24&solo_activas=true
GET /tendencias/agregadas?top_n=10
GET /tendencias/jerarquicas?hours_back=24
```

## 🎨 Patrones de Diseño

### Services Pattern
Toda la lógica de negocio está en `src/services/`:
- `lineamiento_service.py` - CRUD de lineamientos
- `content_service.py` - Gestión de contenido recolectado
- `trends_service.py` - Queries de tendencias

### Collectors Pattern
Cada plataforma tiene su propio collector en `src/collectors/`:
- `youtube_collector.py` - YouTube Data API v3
- `reddit_collector.py` - Reddit API con PRAW
- `mastodon_collector.py` - Mastodon API

### Rate Limiting
`src/utils/rate_limiter.py` implementa Token Bucket Algorithm:
```python
rate_limiter = RateLimiterManager.get_limiter("youtube", max_requests=100, time_window=60)
rate_limiter.acquire()  # Bloquea hasta que haya tokens disponibles
```

### Celery Canvas
Orquestación de tareas con group, chain, chord:
```python
# Recolección paralela
job = group([
    collect_youtube.s(lineamiento_id, keywords),
    collect_reddit.s(lineamiento_id, keywords),
])
result = job.apply_async()
```

## 🧪 Testing

### Configuración de Tests
- `tests/conftest.py` - Fixtures compartidas
- SQLite in-memory para tests
- Override de dependencias (get_db)

### Cobertura Actual
- 18 tests en `test_lineamientos.py`
- Cubre full CRUD + soft delete + activación
- Tests de validación (401, 403, 404, 422, 400)

## 📚 Documentación de API

### Endpoints Principales

**Lineamientos**
- `POST /lineamientos/` - Crear (201)
- `GET /lineamientos/` - Listar con paginación
- `GET /lineamientos/{id}` - Obtener por ID
- `PUT /lineamientos/{id}` - Actualizar
- `DELETE /lineamientos/{id}` - Soft delete (204)
- `POST /lineamientos/{id}/activate` - Reactivar

**Recolección**
- `POST /collect/lineamiento/{id}` - Recolectar todas las plataformas (202)
- `POST /collect/lineamiento/{id}/platform/{platform}` - Plataforma específica
- `POST /collect/all` - Todos los lineamientos activos
- `GET /collect/task/{task_id}` - Estado de tarea

**Tendencias**
- `GET /tendencias/` - Lista con filtros (plataforma, ubicacion, solo_activas)
- `GET /tendencias/agregadas` - Agregadas por tema cross-platform
- `GET /tendencias/jerarquicas` - Estructura jerárquica 4 niveles

### Documentación Interactiva
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI spec: `http://localhost:8000/openapi.json`

## 🔒 Seguridad

### Autenticación
- API Key en header `X-API-Key`
- Middleware de autenticación en `src/api/auth.py`
- Endpoints públicos: `/health`, `/`, `/docs`, `/redoc`

### Configuración
```python
# src/api/auth.py
async def get_api_key(x_api_key: str = Header(...)):
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=403, detail="API key inválida")
    return x_api_key
```

## 🐛 Troubleshooting

### Error: Celery no conecta a Redis
```bash
# Verificar que Redis está corriendo
docker-compose ps redis
# Verificar REDIS_URL en .env
echo $REDIS_URL
```

### Error: Migraciones fallan
```bash
# Revisar estado de migraciones
alembic current
# Rollback si es necesario
alembic downgrade -1
# Aplicar nuevamente
alembic upgrade head
```

### Error: spaCy modelo no encontrado
```bash
# Descargar modelo
python -m spacy download es_core_news_md
# O usar Docker
docker-compose exec api python -m spacy download es_core_news_md
```

### Error: YouTube API quota exceeded
```bash
# Verificar uso de cuota en Google Cloud Console
# Ajustar YOUTUBE_QUOTA_LIMIT en .env
# La cuota se reinicia diariamente (Pacific Time)
```

## 📝 Convenciones del Código

### Naming
- **Archivos**: snake_case (e.g., `lineamiento_service.py`)
- **Clases**: PascalCase (e.g., `LineamientoCreate`)
- **Funciones**: snake_case (e.g., `create_lineamiento`)
- **Constantes**: UPPER_SNAKE_CASE (e.g., `MAX_KEYWORDS`)

### Docstrings
```python
def analyze_trends(lineamiento_id: UUID) -> List[Tendencia]:
    """
    Analiza tendencias para un lineamiento específico.

    Args:
        lineamiento_id: UUID del lineamiento a analizar

    Returns:
        Lista de tendencias detectadas

    Raises:
        ValueError: Si el lineamiento no existe
    """
```

### Type Hints
- Siempre usar type hints en funciones
- Usar `from typing import List, Dict, Optional, Union`
- Usar Pydantic models para validación

### Logging
```python
import logging
logger = logging.getLogger(__name__)

logger.info(f"Recolectando contenido para lineamiento {lineamiento_id}")
logger.warning(f"Rate limit alcanzado para YouTube")
logger.error(f"Error al procesar contenido: {error}", exc_info=True)
```

## 🎯 Próximos Pasos

### Features Pendientes (según spec.md)
- [ ] Implementar análisis de sentiment profundo
- [ ] Agregar soporte para TikTok Creative Center
- [ ] Implementar predicción de tendencias con ML
- [ ] Dashboard web con visualizaciones
- [ ] Sistema de notificaciones en tiempo real
- [ ] Soporte multi-idioma (además de español)

### Mejoras Técnicas
- [ ] Añadir tests para collectors
- [ ] Implementar cache con Redis
- [ ] Optimizar queries con índices adicionales
- [ ] Añadir monitoring con Prometheus/Grafana
- [ ] Implementar CI/CD con GitHub Actions
- [ ] Añadir documentación de arquitectura (diagramas)

## 📞 Contacto y Recursos

### Repositorio
- **GitHub**: git@github.com:juansuarez-pragma/trendsgpx.git
- **Autor**: Juan Suarez (@juansuarez-pragma)

### Referencias Externas
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [TimescaleDB Docs](https://docs.timescale.com/)
- [Celery Docs](https://docs.celeryq.dev/)
- [spaCy Docs](https://spacy.io/)
- [BERTopic Docs](https://maartengr.github.io/BERTopic/)

### Documentación Interna
- `docs/README.md` - Índice completo de documentación
- `API_DOCUMENTATION.md` - Guía completa de API con ejemplos
- `docs/speckit/quickstart.md` - Guía de inicio rápido

---

**Generado con**: Speckit + Claude Code
**Fecha**: Noviembre 2025
**Versión del Proyecto**: 1.0.0
