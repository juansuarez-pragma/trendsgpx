# Modelos SQLAlchemy - Sistema de Análisis de Tendencias

## Modelos Creados

Los siguientes 6 modelos SQLAlchemy han sido creados según las especificaciones del esquema de datos:

### 1. Lineamiento (`lineamiento.py`)
- **Tabla**: `lineamientos`
- **Propósito**: Configuración para lineamientos de recolección de contenido
- **Campos principales**:
  - `id` (UUID, PK)
  - `nombre` (String 255, unique, not null)
  - `descripcion` (Text)
  - `keywords` (JSONB)
  - `plataformas` (JSONB)
  - `activo` (Boolean, default True)
  - `created_at`, `updated_at` (DateTime timezone)
  - `created_by` (String 255)
- **Relaciones**: 
  - `contenido_recolectado` (1:N) → ContenidoRecolectado

### 2. ContenidoRecolectado (`contenido.py`)
- **Tabla**: `contenido_recolectado`
- **Propósito**: Almacena contenido crudo recolectado de plataformas
- **Campos principales**:
  - `id` (UUID, PK)
  - `lineamiento_id` (UUID, FK)
  - `plataforma` (String 50)
  - `plataforma_id` (String 255)
  - `contenido_texto` (Text)
  - `titulo` (String 500)
  - `autor` (String 255)
  - `url` (Text)
  - `metadata` (JSONB)
  - `fecha_publicacion`, `fecha_recoleccion` (DateTime timezone)
  - `idioma` (String 10, default 'es')
  - `nlp_procesado` (Boolean, default False)
  - `nlp_procesado_at` (DateTime timezone)
- **Relaciones**:
  - `lineamiento` (N:1) → Lineamiento
  - `temas` (1:N) → TemaIdentificado

### 3. TemaIdentificado (`tema.py`)
- **Tabla**: `temas_identificados`
- **Propósito**: Temas extraídos mediante procesamiento NLP
- **Campos principales**:
  - `id` (UUID, PK)
  - `contenido_id` (UUID, FK)
  - `tema_nombre` (String 255)
  - `relevancia_score` (Float)
  - `keywords` (ARRAY Text)
  - `sentimiento` (String 20)
  - `sentimiento_score` (Float)
  - `entidades_mencionadas` (JSONB)
  - `modelo_version` (String 50)
  - `identificado_at` (DateTime timezone)
- **Relaciones**:
  - `contenido` (N:1) → ContenidoRecolectado
  - `demografia` (1:N) → Demografia
  - `tendencias` (1:N) → Tendencia

### 4. Demografia (`demografia.py`)
- **Tabla**: `demografia`
- **Propósito**: Segmentación demográfica de temas (jerarquía de 4 niveles)
- **Campos principales**:
  - `id` (UUID, PK)
  - `tema_id` (UUID, FK)
  - `plataforma` (String 50)
  - `ubicacion_pais` (String 100)
  - `ubicacion_ciudad` (String 100)
  - `edad_rango` (String 20)
  - `genero` (String 20)
  - `conteo_menciones` (Integer, default 1)
  - `confianza_score` (Float)
  - `metodo_inferencia` (String 50)
  - `calculado_at` (DateTime timezone)
- **Relaciones**:
  - `tema` (N:1) → TemaIdentificado

### 5. Tendencia (`tendencia.py`)
- **Tabla**: `tendencias`
- **Propósito**: Datos de series temporales para temas en tendencia (TimescaleDB)
- **Campos principales**:
  - `id` (UUID)
  - `tema_id` (UUID, FK)
  - `fecha_hora` (DateTime timezone)
  - `volumen_menciones` (Integer, default 0)
  - `tasa_crecimiento` (Float)
  - `plataforma` (String 50)
  - `ubicacion` (String 100)
  - `edad_rango` (String 20)
  - `genero` (String 20)
  - `es_tendencia` (Boolean, default False)
  - `alerta_enviada` (Boolean, default False)
- **PRIMARY KEY compuesta**: (fecha_hora, tema_id, plataforma, ubicacion, edad_rango, genero)
- **Relaciones**:
  - `tema` (N:1) → TemaIdentificado
  - `validacion` (1:0..1) → ValidacionTendencia

### 6. ValidacionTendencia (`validacion.py`)
- **Tabla**: `validacion_tendencias`
- **Propósito**: Validación de tendencias con fuentes externas (Google Trends)
- **Campos principales**:
  - `id` (UUID, PK)
  - `tendencia_id` (UUID, FK nullable)
  - `tema_nombre` (String 255)
  - `fuente_validacion` (String 50, default 'google_trends')
  - `google_trends_data` (JSONB)
  - `indice_coincidencia` (Float)
  - `validada` (Boolean)
  - `en_google_trends` (Boolean)
  - `solo_en_plataforma` (Boolean)
  - `validado_at` (DateTime timezone)
- **Relaciones**:
  - `tendencia` (1:1) → Tendencia (nullable)

## Diagrama de Relaciones

```
Lineamiento (1) ─────┐
                     │ cascade delete
                     ↓
              ContenidoRecolectado (N) ─────┐
                                            │ cascade delete
                                            ↓
                                    TemaIdentificado (N) ─────┬─────┬─────┐
                                                               │     │     │
                                          cascade delete ──────┘     │     └────── cascade delete
                                                 ↓                   │                    ↓
                                            Demografia (N)           │                Tendencia (N)
                                                                     │                    │
                                                cascade delete ──────┘              SET NULL
                                                      ↓                                   ↓
                                                 Tendencia (N)                  ValidacionTendencia (1)
```

## Características Especiales

### Cascadas de Eliminación
- **Lineamiento → ContenidoRecolectado**: CASCADE
- **ContenidoRecolectado → TemaIdentificado**: CASCADE
- **TemaIdentificado → Demografia**: CASCADE
- **TemaIdentificado → Tendencia**: CASCADE
- **Tendencia → ValidacionTendencia**: SET NULL (para auditoría)

### Claves Compuestas
- **Tendencia**: PRIMARY KEY compuesta en (fecha_hora, tema_id, plataforma, ubicacion, edad_rango, genero)
  - Optimizada para TimescaleDB hipertablas

### Tipos Especiales de PostgreSQL
- **UUID**: Usado para todos los IDs primarios
- **JSONB**: Usado para datos flexibles (metadata, keywords, plataformas, entidades)
- **ARRAY**: Usado para keywords en TemaIdentificado
- **DateTime(timezone=True)**: Usado para todas las marcas de tiempo

### Valores por Defecto
- **UUID**: `uuid.uuid4` para generación automática de IDs
- **DateTime**: `func.now()` para marcas de tiempo automáticas
- **Boolean**: Valores predeterminados apropiados (activo=True, nlp_procesado=False, etc.)

## Próximos Pasos

1. **Instalar dependencias**:
   ```bash
   pip install sqlalchemy psycopg2-binary alembic
   ```

2. **Crear migración inicial**:
   ```bash
   alembic revision --autogenerate -m "Initial schema"
   alembic upgrade head
   ```

3. **Habilitar TimescaleDB**:
   - Convertir tabla `tendencias` a hipertabla
   - Configurar políticas de retención
   - Crear vistas materializadas continuas

4. **Agregar índices adicionales** según queries de producción

5. **Implementar tests unitarios** para validar relaciones

## Documentación de Referencia

- Especificación completa: `/specs/001-social-trends-analysis/data-model.md`
- Base SQLAlchemy: `src/models/base.py`
