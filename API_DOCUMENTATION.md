# TrendsGPX - Documentación de API

## Tabla de Contenidos

1. [Autenticación](#autenticación)
2. [Endpoints de Lineamientos](#endpoints-de-lineamientos)
3. [Endpoints de Recolección](#endpoints-de-recolección)
4. [Endpoints de Tendencias](#endpoints-de-tendencias)
5. [Ejemplos de Uso](#ejemplos-de-uso)

## Autenticación

Todos los endpoints (excepto `/health` y `/`) requieren autenticación mediante API key en el header.

```http
X-API-Key: tu-api-key-aqui
```

Por defecto en desarrollo: `dev-api-key-change-in-production`

## Endpoints de Lineamientos

### POST /lineamientos/
Crea un nuevo lineamiento de búsqueda.

**Request Body:**
```json
{
  "nombre": "Tecnología IA 2025",
  "keywords": ["IA", "inteligencia artificial", "machine learning"],
  "plataformas": ["youtube", "reddit"]
}
```

**Response (201):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "nombre": "Tecnología IA 2025",
  "keywords": ["IA", "inteligencia artificial", "machine learning"],
  "plataformas": ["youtube", "reddit"],
  "activo": true,
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

### GET /lineamientos/
Lista lineamientos con paginación.

**Query Parameters:**
- `skip` (int): Offset para paginación (default: 0)
- `limit` (int): Máximo de resultados (default: 100, max: 100)
- `activo_only` (bool): Solo lineamientos activos (default: false)

**Response (200):**
```json
{
  "total": 10,
  "items": [...]
}
```

### GET /lineamientos/{id}
Obtiene un lineamiento por ID.

**Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "nombre": "Tecnología IA 2025",
  ...
}
```

### PUT /lineamientos/{id}
Actualiza un lineamiento (parcial o completo).

**Request Body (todos los campos opcionales):**
```json
{
  "nombre": "Tecnología IA 2025 Actualizado",
  "keywords": ["IA", "GPT", "transformers"],
  "activo": false
}
```

### DELETE /lineamientos/{id}
Elimina un lineamiento (soft delete - marca como inactivo).

**Response (204):** No Content

### POST /lineamientos/{id}/activate
Reactiva un lineamiento inactivo.

**Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "activo": true,
  ...
}
```

## Endpoints de Recolección

### POST /collect/lineamiento/{id}
Dispara recolección de contenido para todas las plataformas de un lineamiento.

**Query Parameters:**
- `hours_back` (int): Horas hacia atrás a buscar (default: 24)

**Response (202):**
```json
{
  "task_id": "abc123-def456",
  "lineamiento_id": "550e8400-e29b-41d4-a716-446655440000",
  "lineamiento_nombre": "Tecnología IA 2025",
  "plataformas": ["youtube", "reddit"],
  "hours_back": 24,
  "status": "accepted",
  "message": "Tarea de recolección iniciada en segundo plano"
}
```

### POST /collect/lineamiento/{id}/platform/{platform}
Recolecta contenido de una plataforma específica.

**Path Parameters:**
- `platform`: youtube, reddit, o mastodon

**Query Parameters:**
- `hours_back` (int): Horas hacia atrás (default: 24)

**Response (202):**
```json
{
  "task_id": "abc123-def456",
  "lineamiento_id": "550e8400-e29b-41d4-a716-446655440000",
  "platform": "youtube",
  "status": "accepted",
  ...
}
```

### POST /collect/all
Recolecta contenido para TODOS los lineamientos activos (⚠️ operación costosa).

**Response (202):**
```json
{
  "task_id": "abc123-def456",
  "total_lineamientos": 5,
  "status": "accepted",
  "message": "Tarea de recolección masiva iniciada para 5 lineamientos"
}
```

### GET /collect/task/{task_id}
Consulta el estado de una tarea de recolección.

**Response (200):**
```json
{
  "task_id": "abc123-def456",
  "status": "SUCCESS",
  "ready": true,
  "result": {
    "lineamiento_id": "550e8400-...",
    "platforms": ["youtube", "reddit"],
    "status": "success"
  }
}
```

Estados posibles: `PENDING`, `STARTED`, `SUCCESS`, `FAILURE`, `RETRY`

## Endpoints de Tendencias

### GET /tendencias/
Lista tendencias activas con filtros.

**Query Parameters:**
- `plataforma` (str): youtube, reddit, mastodon (opcional)
- `ubicacion` (str): País o ciudad (opcional)
- `solo_activas` (bool): Solo tendencias activas (default: true)
- `hours_back` (int): Horas hacia atrás, max 168 (default: 24)
- `skip` (int): Offset (default: 0)
- `limit` (int): Máximo 100 (default: 50)

**Response (200):**
```json
{
  "total": 25,
  "items": [
    {
      "id": "uuid-here",
      "tema_id": "uuid-here",
      "tema_nombre": "youtube_content_123",
      "plataforma": "youtube",
      "ubicacion": "México",
      "edad_rango": "18-24",
      "genero": "M",
      "volumen_menciones": 150,
      "tasa_crecimiento": 0.75,
      "sentimiento_promedio": 0.65,
      "es_tendencia": true,
      "fecha_hora": "2025-01-15T14:00:00Z",
      "keywords": ["IA", "tecnología", "futuro"],
      "validada": true
    },
    ...
  ]
}
```

### GET /tendencias/agregadas
Tendencias agregadas por tema across plataformas.

**Query Parameters:**
- `hours_back` (int): Horas hacia atrás, max 168 (default: 24)
- `top_n` (int): Top N tendencias, max 50 (default: 10)

**Response (200):**
```json
[
  {
    "tema_nombre": "youtube_content_123",
    "plataformas": ["youtube", "reddit"],
    "volumen_total": 300,
    "tasa_crecimiento_promedio": 0.68,
    "sentimiento_promedio": 0.72,
    "keywords": ["IA", "tecnología", "GPT"],
    "ubicaciones": ["México", "España", "Argentina"]
  },
  ...
]
```

### GET /tendencias/jerarquicas
Tendencias en estructura jerárquica (Plataforma → Ubicación → Edad → Género).

**Query Parameters:**
- `hours_back` (int): Horas hacia atrás, max 168 (default: 24)

**Response (200):**
```json
{
  "total_tendencias": 50,
  "plataformas": [
    {
      "plataforma": "youtube",
      "ubicaciones": [
        {
          "ubicacion": "México",
          "edades": [
            {
              "edad_rango": "18-24",
              "generos": [
                {
                  "genero": "M",
                  "temas": [
                    {
                      "tema_nombre": "youtube_content_123",
                      "volumen": 150,
                      "crecimiento": 0.75,
                      "sentimiento": 0.65,
                      "keywords": ["IA", "tech"]
                    }
                  ]
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

## Ejemplos de Uso

### Flujo Completo: Crear Lineamiento y Recolectar Tendencias

#### 1. Crear lineamiento
```bash
curl -X POST "http://localhost:8000/lineamientos/" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-api-key-change-in-production" \
  -d '{
    "nombre": "Tecnología IA 2025",
    "keywords": ["IA", "inteligencia artificial", "GPT"],
    "plataformas": ["youtube", "reddit"]
  }'
```

#### 2. Disparar recolección
```bash
curl -X POST "http://localhost:8000/collect/lineamiento/550e8400-e29b-41d4-a716-446655440000?hours_back=24" \
  -H "X-API-Key: dev-api-key-change-in-production"
```

#### 3. Consultar estado de la tarea
```bash
curl "http://localhost:8000/collect/task/abc123-def456" \
  -H "X-API-Key: dev-api-key-change-in-production"
```

#### 4. Esperar procesamiento NLP (automático cada hora)

El procesamiento NLP se ejecuta automáticamente cada hora vía Celery Beat.

#### 5. Consultar tendencias
```bash
curl "http://localhost:8000/tendencias/?hours_back=24&solo_activas=true" \
  -H "X-API-Key: dev-api-key-change-in-production"
```

#### 6. Consultar tendencias agregadas
```bash
curl "http://localhost:8000/tendencias/agregadas?top_n=10" \
  -H "X-API-Key: dev-api-key-change-in-production"
```

### Filtrar Tendencias por Plataforma

```bash
curl "http://localhost:8000/tendencias/?plataforma=youtube&hours_back=48" \
  -H "X-API-Key: dev-api-key-change-in-production"
```

### Obtener Estructura Jerárquica

```bash
curl "http://localhost:8000/tendencias/jerarquicas?hours_back=24" \
  -H "X-API-Key: dev-api-key-change-in-production"
```

## Tareas Programadas (Celery Beat)

Las siguientes tareas se ejecutan automáticamente:

- **Recolección de contenido**: Cada 30 minutos
- **Procesamiento NLP**: Cada hora (en punto)
- **Análisis de tendencias**: Cada hora (minuto 15)
- **Validación con Google Trends**: Cada 6 horas (minuto 30)
- **Limpieza de datos antiguos**: Diariamente a las 3:00 AM

## Errores Comunes

### 401 Unauthorized
```json
{
  "detail": "API key requerida. Incluir header X-API-Key"
}
```
**Solución**: Incluir header `X-API-Key` en la petición.

### 403 Forbidden
```json
{
  "detail": "API key inválida"
}
```
**Solución**: Verificar que la API key sea correcta.

### 404 Not Found
```json
{
  "detail": "Lineamiento {id} no encontrado"
}
```
**Solución**: Verificar que el ID del lineamiento exista.

### 400 Bad Request
```json
{
  "detail": "Ya existe un lineamiento con el nombre 'X'"
}
```
**Solución**: Usar un nombre diferente para el lineamiento.

## Rate Limiting

Las plataformas tienen los siguientes límites (configurables en .env):

- **YouTube**: 10,000 unidades/día
- **Reddit**: 60 requests/minuto
- **Mastodon**: 300 requests/5 minutos

El sistema maneja automáticamente el rate limiting con token bucket algorithm.

## Documentación Interactiva

Accede a la documentación interactiva de Swagger UI:

```
http://localhost:8000/docs
```

O ReDoc:

```
http://localhost:8000/redoc
```
