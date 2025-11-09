# Guía de Inicio Rápido: Sistema de Análisis de Tendencias en Redes Sociales

**Funcionalidad**: 001-social-trends-analysis
**Última Actualización**: 2025-11-08
**Tiempo Estimado de Configuración**: 45-60 minutos

---

## Tabla de Contenidos

1. [Prerrequisitos](#prerrequisitos)
2. [Configuración de Claves API](#configuración-de-claves-api)
3. [Configuración de Desarrollo Local](#configuración-de-desarrollo-local)
4. [Inicialización de la Base de Datos](#inicialización-de-la-base-de-datos)
5. [Ejecutar la Aplicación](#ejecutar-la-aplicación)
6. [Pruebas](#pruebas)
7. [Problemas Comunes](#problemas-comunes)
8. [Próximos Pasos](#próximos-pasos)

---

## Prerrequisitos

### Requisitos del Sistema

- **SO**: Linux, macOS, o WSL2 (Windows)
- **Python**: 3.11 o superior
- **PostgreSQL**: 15 o superior
- **Redis**: 6.0 o superior
- **Git**: Última versión
- **Docker** (opcional pero recomendado): Última versión

### Instalar Dependencias del Sistema

**macOS** (usando Homebrew):
```bash
brew install python@3.11 postgresql@15 redis git
brew services start postgresql
brew services start redis
```

**Ubuntu/Debian**:
```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip \
    postgresql-15 postgresql-contrib redis-server git
sudo systemctl start postgresql
sudo systemctl start redis-server
```

**Verificar Instalaciones**:
```bash
python3.11 --version  # Debe ser 3.11+
psql --version        # Debe ser 15+
redis-cli --version   # Debe ser 6.0+
```

---

## Configuración de Claves API

Necesitarás obtener claves API/credenciales de las siguientes plataformas:

### 1. YouTube Data API v3

**Pasos**:
1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto (por ejemplo, "TrendsGPX")
3. Habilita **YouTube Data API v3**:
   - Menú de Navegación → APIs & Services → Library
   - Busca "YouTube Data API v3" → Enable
4. Crea una Clave API:
   - APIs & Services → Credentials → Create Credentials → API Key
   - Copia tu clave API

**Cuota**: 10,000 unidades/día (nivel gratuito)

**Valor Esperado**:
```bash
YOUTUBE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

**Documentación**: https://developers.google.com/youtube/v3/getting-started

---

### 2. Reddit API (PRAW)

**Pasos**:
1. Crea una cuenta en Reddit en https://reddit.com (si no tienes una)
2. Ve a https://www.reddit.com/prefs/apps
3. Haz clic en "Create App" o "Create Another App"
4. Completa:
   - **Name**: TrendsGPX Collector
   - **Type**: script
   - **Description**: Social media trends analysis
   - **About URL**: (dejar en blanco)
   - **Redirect URI**: http://localhost:8000
5. Haz clic en "Create app"
6. Copia `client_id` (debajo del nombre de la app) y `client_secret`

**Cuota**: 100 consultas por minuto (nivel gratuito)

**Valores Esperados**:
```bash
REDDIT_CLIENT_ID=xxxxxxxxxxxx
REDDIT_CLIENT_SECRET=yyyyyyyyyyyyyyyyyyyyyyyy
REDDIT_USER_AGENT=TrendsGPX/1.0 by YourRedditUsername
```

**Documentación**: https://www.reddit.com/dev/api

---

### 3. Mastodon API

**Pasos**:
1. Crea una cuenta en una instancia de Mastodon (por ejemplo, https://mastodon.social)
2. Ve a Preferencias → Development → New Application
3. Completa:
   - **Application Name**: TrendsGPX
   - **Scopes**: read (solo lectura)
4. Enviar
5. Copia `access_token`

**Cuota**: Generosa (varía según la instancia)

**Valores Esperados**:
```bash
MASTODON_ACCESS_TOKEN=zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz
MASTODON_INSTANCE_URL=https://mastodon.social
```

**Documentación**: https://docs.joinmastodon.org/api/

---

### 4. Google Trends (pytrends)

**¡No Se Requiere Clave API!** pytrends usa acceso no oficial a Google Trends.

**Limitación de Tasa**: ~1 solicitud cada 5 segundos recomendada.

**Nota**: pytrends está sin mantenimiento (archivado en abril 2025). Puede fallar si Google cambia el sitio web de Trends.

---

## Configuración de Desarrollo Local

### 1. Clonar Repositorio

```bash
git clone <repository-url>
cd trendsgpx
```

### 2. Crear Entorno Virtual de Python

```bash
python3.11 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar Dependencias

```bash
pip install --upgrade pip
pip install -r backend/requirements.txt
```

**requirements.txt** incluye:
- FastAPI + Uvicorn
- Celery + Redis
- SQLAlchemy + Alembic
- psycopg2-binary (controlador PostgreSQL)
- TimescaleDB (cliente Python)
- PRAW (Reddit)
- Mastodon.py
- google-api-python-client (YouTube)
- pytrends
- transformers, spaCy, BERTopic (NLP)
- pysentimiento (análisis de sentimiento en español)
- PyrateLimiter

### 4. Descargar Modelos NLP

```bash
# Modelo de spaCy en español
python -m spacy download es_core_news_md

# Opcional: Descargar RoBERTuito (BERT en español)
# Esto sucede automáticamente en el primer uso mediante transformers
```

### 5. Configurar Variables de Entorno

Crea el archivo `.env` en el directorio `backend/`:

```bash
# Base de datos
DATABASE_URL=postgresql://trendsgpx:password@localhost:5432/trendsgpx
TIMESCALEDB_ENABLED=true

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Claves API
YOUTUBE_API_KEY=your_youtube_api_key_here
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=TrendsGPX/1.0 by YourUsername
MASTODON_ACCESS_TOKEN=your_mastodon_access_token
MASTODON_INSTANCE_URL=https://mastodon.social

# Aplicación
SECRET_KEY=your-secret-key-generate-with-openssl-rand-hex-32
DEBUG=true
ALLOWED_HOSTS=localhost,127.0.0.1
API_KEYS=dev_key_12345,another_api_key  # Separadas por comas

# NLP
NLP_MODEL=dccuchile/bert-base-spanish-wwm-cased
BERTOPIC_EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2
SENTIMENT_MODEL=pysentimiento/robertuito-sentiment-analysis

# Registro (Logging)
LOG_LEVEL=INFO
```

**Generar SECRET_KEY**:
```bash
openssl rand -hex 32
```

---

## Inicialización de la Base de Datos

### 1. Crear Base de Datos y Habilitar TimescaleDB

**Opción A: Configuración Manual**

```bash
# Crear base de datos
createdb -U postgres trendsgpx

# Conectar y habilitar extensiones
psql -U postgres -d trendsgpx <<EOF
CREATE USER trendsgpx WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE trendsgpx TO trendsgpx;

-- Habilitar extensiones
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS pg_trgm;  -- Búsqueda de texto completo
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";  -- Generación de UUID
EOF
```

**Opción B: Docker Compose** (Recomendado)

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: timescale/timescaledb:latest-pg15
    environment:
      POSTGRES_DB: trendsgpx
      POSTGRES_USER: trendsgpx
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

```bash
docker-compose up -d
```

### 2. Ejecutar Migraciones de Base de Datos

```bash
cd backend

# Inicializar Alembic (solo la primera vez)
alembic init alembic

# Ejecutar migraciones
alembic upgrade head
```

### 3. Verificar Configuración de Base de Datos

```bash
psql -U trendsgpx -d trendsgpx -c "\dt"
```

**Tablas esperadas**:
- lineamientos
- contenido_recolectado
- temas_identificados
- demografia
- tendencias (hipertabla de TimescaleDB)
- validacion_tendencias
- alembic_version

---

## Ejecutar la Aplicación

### Modo de Desarrollo (Manual)

**Terminal 1: Servidor FastAPI**
```bash
cd backend
source ../venv/bin/activate
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2: Worker de Celery (Recolectores)**
```bash
cd backend
source ../venv/bin/activate
celery -A src.tasks.celery_app worker \
  -Q youtube_collector,reddit_collector,mastodon_collector \
  --concurrency=100 --pool=gevent --prefetch-multiplier=4 \
  --loglevel=info
```

**Terminal 3: Worker de Celery (NLP)**
```bash
cd backend
source ../venv/bin/activate
celery -A src.tasks.celery_app worker \
  -Q nlp_processing \
  --concurrency=8 --pool=prefork --prefetch-multiplier=1 \
  --loglevel=info
```

**Terminal 4: Worker de Celery (Analítica)**
```bash
cd backend
source ../venv/bin/activate
celery -A src.tasks.celery_app worker \
  -Q analytics \
  --concurrency=4 --prefetch-multiplier=2 \
  --loglevel=info
```

**Terminal 5: Celery Beat (Programador)**
```bash
cd backend
source ../venv/bin/activate
celery -A src.tasks.celery_app beat \
  --scheduler django_celery_beat.schedulers:DatabaseScheduler \
  --loglevel=info
```

**Terminal 6: Flower (Panel de Monitoreo)**
```bash
cd backend
source ../venv/bin/activate
celery -A src.tasks.celery_app flower --port=5555
```

**Puntos de Acceso**:
- API: http://localhost:8000
- Documentación API (Swagger): http://localhost:8000/docs
- Panel de Flower: http://localhost:5555

---

### Modo de Producción (Docker Compose)

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  api:
    build: ./backend
    command: uvicorn src.api.main:app --host 0.0.0.0 --port 8000
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://trendsgpx:password@postgres:5432/trendsgpx
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis

  celery_collector:
    build: ./backend
    command: celery -A src.tasks.celery_app worker -Q youtube_collector,reddit_collector,mastodon_collector --concurrency=100 --pool=gevent
    depends_on:
      - postgres
      - redis

  celery_nlp:
    build: ./backend
    command: celery -A src.tasks.celery_app worker -Q nlp_processing --concurrency=8 --pool=prefork
    depends_on:
      - postgres
      - redis

  celery_beat:
    build: ./backend
    command: celery -A src.tasks.celery_app beat --scheduler django_celery_beat.schedulers:DatabaseScheduler
    depends_on:
      - postgres
      - redis

  flower:
    build: ./backend
    command: celery -A src.tasks.celery_app flower --port=5555
    ports:
      - "5555:5555"
    depends_on:
      - redis

  postgres:
    image: timescale/timescaledb:latest-pg15
    environment:
      POSTGRES_DB: trendsgpx
      POSTGRES_USER: trendsgpx
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

volumes:
  postgres_data:
```

```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## Pruebas

### Ejecutar Pruebas de API

```bash
cd backend
pytest tests/ -v
```

### Probar Endpoints de API

**Crear Lineamiento**:
```bash
curl -X POST http://localhost:8000/v1/lineamientos \
  -H "X-API-Key: dev_key_12345" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Test Tech Trends",
    "keywords": ["python", "fastapi"],
    "plataformas": ["youtube", "reddit"]
  }'
```

**Obtener Tendencias**:
```bash
curl -X GET "http://localhost:8000/v1/tendencias?fecha_inicio=2025-11-01T00:00:00Z&fecha_fin=2025-11-08T23:59:59Z" \
  -H "X-API-Key: dev_key_12345"
```

### Probar Tareas de Celery

**Activar Recolección Manual**:
```bash
cd backend
python -c "
from src.tasks.collectors import collect_youtube_batch
result = collect_youtube_batch.delay(
    lineamiento_id='<uuid>',
    keywords=['python', 'fastapi'],
    batch_size=10
)
print(f'Task ID: {result.id}')
"
```

**Verificar Estado de Tarea**:
```bash
# Vía Flower: http://localhost:5555
# O vía Python:
python -c "
from celery.result import AsyncResult
result = AsyncResult('<task-id>')
print(result.status)
print(result.result)
"
```

### Probar Pipeline de NLP

```bash
cd backend
python -c "
from src.nlp.topic_modeling import BERTopicAnalyzer
analyzer = BERTopicAnalyzer()
topics = analyzer.identify_topics(['Este es un texto de prueba sobre inteligencia artificial'])
print(topics)
"
```

---

## Problemas Comunes

### Problema: Error de Conexión a PostgreSQL

**Error**: `psycopg2.OperationalError: could not connect to server`

**Solución**:
```bash
# Verificar si PostgreSQL está ejecutándose
sudo systemctl status postgresql  # Linux
brew services list                # macOS

# Verificar DATABASE_URL en .env
# Asegurar que host, port, user, password sean correctos
```

---

### Problema: Extensión TimescaleDB No Encontrada

**Error**: `CREATE EXTENSION IF NOT EXISTS timescaledb; ERROR: extension "timescaledb" is not available`

**Solución**:
```bash
# Asegurar que TimescaleDB esté instalado
# macOS:
brew install timescaledb

# Ubuntu:
sudo add-apt-repository ppa:timescale/timescaledb-ppa
sudo apt update
sudo apt install timescaledb-postgresql-15

# Luego reiniciar PostgreSQL
sudo systemctl restart postgresql
```

---

### Problema: Worker de Celery No Consume Tareas

**Error**: Las tareas permanecen en la cola, nunca se procesan

**Solución**:
```bash
# Verificar si los workers están ejecutándose
celery -A src.tasks.celery_app inspect active

# Verificar enrutamiento de cola
# Asegurar que la cola de tareas coincida con el parámetro -Q del worker

# Verificar conexión a Redis
redis-cli ping  # Debe retornar PONG

# Limpiar tareas atascadas
celery -A src.tasks.celery_app purge
```

---

### Problema: Cuota de API de YouTube Excedida

**Error**: `googleapiclient.errors.HttpError: 403 quotaExceeded`

**Solución**:
```bash
# Verificar uso de cuota en Google Cloud Console:
# APIs & Services → YouTube Data API v3 → Quotas

# Esperar hasta medianoche PT (reinicio de cuota)
# O solicitar aumento de cuota (gratis, pero requiere aprobación)

# Temporal: Reducir frecuencia de recolección en el cronograma de Celery Beat
```

---

### Problema: Falla la Descarga de Modelo NLP

**Error**: `OSError: Can't load model`

**Solución**:
```bash
# Descargar modelos manualmente
python -m spacy download es_core_news_md

# Para modelos de transformers, establecer directorio de caché
export TRANSFORMERS_CACHE=/path/to/cache
python -c "from transformers import AutoModel; AutoModel.from_pretrained('dccuchile/bert-base-spanish-wwm-cased')"
```

---

### Problema: Memoria de Redis Llena

**Error**: `OOM command not allowed when used memory > 'maxmemory'`

**Solución**:
```bash
# Verificar uso de memoria de Redis
redis-cli info memory

# Establecer política de expulsión
redis-cli CONFIG SET maxmemory-policy allkeys-lru

# O aumentar maxmemory en redis.conf
# maxmemory 2gb
```

---

## Próximos Pasos

### 1. Sembrar Datos de Prueba

```bash
cd backend
python scripts/seed_data.py
```

Esto crea:
- 3 lineamientos de muestra
- ~100 elementos de contenido_recolectado de muestra
- Temas y demografías procesados por NLP

### 2. Configurar Límites de Tasa de API

Edita `backend/src/utils/rate_limit.py` para ajustar:
- YouTube: 80% del umbral de 10,000 unidades/día
- Reddit: 90% del umbral de 100 QPM
- Mastodon: Límites específicos de la instancia

### 3. Configurar Monitoreo

**Prometheus + Grafana**:
```bash
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
```

**Importar Dashboards**:
- Monitoreo de Celery: ID de dashboard de Grafana 14637
- PostgreSQL: ID de dashboard de Grafana 9628

### 4. Configurar Alertas

Edita `backend/src/tasks/alerts.py` para agregar:
- Notificaciones por correo electrónico (vía SMTP)
- Webhooks de Slack/Discord
- Endpoints de webhook personalizados

### 5. Ejecutar Pruebas de Rendimiento

```bash
cd backend
pytest tests/performance/ -v --benchmark-only
```

Resultados esperados:
- Tiempo de respuesta de API <3s para 100k elementos (SC-003)
- Procesamiento NLP <5s por elemento
- Tasa de recolección >4,000 elementos/día (SC-001)

---

## Enlaces de Documentación

- [Especificación de Funcionalidad](./spec.md)
- [Plan de Implementación](./plan.md)
- [Modelo de Datos](./data-model.md)
- [Contrato de API (OpenAPI)](./contracts/openapi.yaml)
- [Contrato de Eventos de Celery](./contracts/events.yaml)
- [Hallazgos de Investigación](./research.md)

---

## Soporte

**Problemas**: https://github.com/<org>/trendsgpx/issues
**Slack**: #trendsgpx-dev
**Correo**: dev@trendsgpx.com

---

**Estado**: ✅ ¡Entorno de desarrollo listo!

**Tiempo Estimado para la Primera Llamada a la API**: ~15 minutos (si todos los prerrequisitos están instalados)

**Siguiente**: ¡Crea tu primer lineamiento vía API y observa a los workers de Celery recolectar datos en tiempo real a través del panel de Flower!
