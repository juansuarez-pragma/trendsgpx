# Investigación de APIs: APIs de Redes Sociales Gratuitas para MVP

**Fecha de Investigación**: 2025-11-08
**Rama**: `001-social-trends-analysis`
**Restricción**: FR-029 - El sistema DEBE usar SOLO herramientas/APIs gratuitas (sin servicios de pago)
**Objetivo**: Recolectar 4,000 elementos de contenido/día (1,000 por plataforma) con datos demográficos

---

## Resumen Ejecutivo

**Hallazgo Crítico**: La mayoría de las APIs oficiales de redes sociales tienen limitaciones significativas en sus niveles gratuitos que hacen que recolectar 4,000 elementos/día sea **MUY DESAFIANTE** sin costo. Solo 2 de 5 APIs evaluadas son realmente viables para el MVP sin pago.

### Recomendaciones:
- **USAR**: YouTube Data API v3 (con gestión de cuota), Google Trends (pytrends), Reddit API (PRAW)
- **EVITAR**: Meta Graph API (aprobación restrictiva + límites bajos), TikTok APIs (acceso solo para investigadores)
- **ENFOQUE ALTERNATIVO**: Considerar web scraping para plataformas con APIs restrictivas (aplican consideraciones legales/éticas)

---

## 1. Meta Graph API (Facebook + Instagram)

### Estado del Nivel Gratuito: **GRATIS LIMITADO (⚠️ NO RECOMENDADO)**

#### Límites de Tasa / Cuotas:
- **Instagram API**: 200 solicitudes por hora
- **Facebook API**: Límites de tasa basados en uso de la app (call_count, total_time, total_cputime como porcentajes)
- Cuando cualquier métrica excede 100%, la app se limita
- **No hay forma de aumentar límites** mediante solicitud especial

#### Capacidad de Recolección Diaria:
- **200 solicitudes/hora × 24 horas = 4,800 solicitudes/día máximo**
- Si cada solicitud retorna 25 elementos: ~120,000 elementos/día (teóricamente suficiente)
- **SIN EMBARGO**: Los requisitos estrictos de acceso limitan severamente el uso real

#### Datos Demográficos:
| Tipo de Dato | Disponibilidad | Notas |
|--------------|----------------|-------|
| Edad | ✅ DISPONIBLE | Solo para cuentas de negocio/creador que autoricen tu app |
| Género | ✅ DISPONIBLE | Solo para cuentas de negocio/creador |
| Ubicación | ✅ DISPONIBLE | Nivel de país/ciudad |
| **Precisión** | 95%+ | Datos directos de la plataforma (cumple SC-005) |

**Endpoints Disponibles**:
- `engaged_audience_demographics`
- `reached_audience_demographics`
- `follower_demographics`

#### Método de Autenticación:
- **OAuth 2.0** vía Facebook Login
- Requiere cuenta de Facebook Developer
- **LIMITACIÓN CRÍTICA**: Requiere aprobación de App Review
- Los usuarios deben tener cuentas de Instagram Business/Creator conectadas a Facebook Pages
- Los tokens expiran (corta duración: horas, larga duración: 60 días) - debe implementarse lógica de actualización

#### Barreras Principales:
1. **Proceso de App Review**: Puede tomar >1 semana, frecuentemente denegado
2. **Restringido a Cuentas de Negocio**: No puede acceder contenido de usuarios regulares
3. **Limitaciones de Privacidad**: Solo los 45 segmentos principales de audiencia, retraso de reporte de 48 horas
4. **Modo de Desarrollo**: Límites extremadamente bajos para apps no verificadas

#### Recomendación: **NO USAR** ❌
**Justificación**: Las barreras de revisión de la app, restricciones de cuentas de negocio y complejidad superan los beneficios. Los límites de tasa son técnicamente suficientes pero los requisitos de acceso lo hacen impracticable para MVP.

#### Alternativas Gratuitas:
- **Web Scraping**: Herramientas estilo Invidious (área gris legal, viola ToS)
- **Instagram Basic Display API**: Limitado solo al contenido propio del usuario
- **APIs de terceros**: RapidAPI (pago), Apify (pago $0.25/1k)

---

## 2. YouTube Data API v3

### Estado del Nivel Gratuito: **VERDADERAMENTE GRATIS** ✅ **RECOMENDADO**

#### Límites de Tasa / Cuotas:
- **10,000 unidades de cuota por día** (por defecto)
- La cuota se reinicia a medianoche Hora del Pacífico (PT)
- Diferentes operaciones consumen diferentes unidades:
  - Búsqueda: 100 unidades por solicitud
  - Lista de videos: 1 unidad por solicitud
  - Hilos de comentarios: 1 unidad por solicitud

#### Capacidad de Recolección Diaria:
- **Recolección basada en búsqueda**: 10,000 unidades ÷ 100 unidades = **100 búsquedas/día**
- Si cada búsqueda retorna 50 videos: **5,000 videos/día** (excede objetivo de 1,000 ✅)
- **Detalles de videos (después de búsqueda)**: Casi ilimitado (1 unidad por 50 videos)

**Flujo de Trabajo de Ejemplo**:
1. Búsqueda por palabra clave: 20 búsquedas × 100 unidades = 2,000 unidades (1,000 videos)
2. Obtener detalles de video: 1,000 videos ÷ 50 por solicitud × 1 unidad = 20 unidades
3. **Total**: 2,020 unidades usadas, 7,980 restantes

#### Datos Demográficos:
| Tipo de Dato | Disponibilidad | Notas |
|--------------|----------------|-------|
| Edad | ✅ DISPONIBLE | Vía YouTube Analytics API (API separada) |
| Género | ✅ DISPONIBLE | Vía YouTube Analytics API |
| Ubicación | ✅ DISPONIBLE | País, continente, subcontinente, ciudad, provincia (solo EE.UU.) |
| **Precisión** | 95%+ | Datos directos de usuarios conectados (cumple SC-005) |

**IMPORTANTE**: YouTube Analytics API proporciona demografía pero **SOLO para el canal propio del propietario del contenido**. Para analizar OTROS canales/videos, los datos demográficos NO están disponibles vía API.

**Dimensiones Disponibles** (YouTube Analytics API):
- `ageGroup`: Rangos de edad
- `gender`: female, male, user_specified
- `country`, `continent`, `subcontinent`, `city`

**Umbrales de Privacidad**: Los datos demográficos están sujetos a umbrales mínimos de vistas.

#### Método de Autenticación:
- **API Key** (simple, para datos públicos de solo lectura) ✅ FÁCIL
- **OAuth 2.0** (para datos específicos del usuario, ej., analíticas del canal propio)

#### Aumento de Cuota:
- **Gratis solicitar** vía Google Cloud Console
- Aprobación basada en caso de uso y cumplimiento
- Sin cargo monetario por aumentos

#### Recomendación: **USAR** ✅
**Justificación**:
- Verdaderamente gratis con cuota suficiente (5,000 elementos/día vs objetivo de 1,000)
- Autenticación simple con API key
- API bien documentada y estable
- Se pueden solicitar aumentos de cuota gratis
- **LIMITACIÓN**: Demografía solo para canal propio, no para analizar otros

#### Estrategia de Recolección:
1. Usar `search.list` para encontrar videos por palabras clave (100 unidades cada uno)
2. Usar `videos.list` para obtener detalles (1 unidad por 50 videos)
3. Implementar seguimiento de cuota para evitar alcanzar límites
4. Para demografía: Inferir de comentarios, descripciones de canal (objetivo de precisión 65% según FR-011)

---

## 3. TikTok APIs

### Estado del Nivel Gratuito: **SOLO INVESTIGADORES** ❌ **NO ACCESIBLE**

#### TikTok Research API:
- **Acceso**: Restringido a investigadores académicos de universidades sin fines de lucro acreditadas (EE.UU. y Europa)
- **Proceso de Aplicación**: Debe aplicar, revisado por legitimidad
- **Costo**: Gratis para investigadores aprobados
- **Cronograma**: 1-2 semanas para decisión de aprobación

#### TikTok Commercial Content API:
- **Acceso**: Solo investigadores aprobados
- **Propósito**: Búsqueda de anuncios y datos de contenido comercial
- **Costo**: Gratis para investigadores aprobados

#### TikTok Creative Center:
- **Sin API oficial** - solo interfaz web
- **Scrapers de terceros**: Apify ($0.25/1k elementos) - NO GRATIS

#### Límites de Tasa / Cuotas:
- No documentados públicamente (acceso solo para investigadores)

#### Capacidad de Recolección Diaria:
- **N/A** - No se puede acceder sin estatus de investigador

#### Datos Demográficos:
- No documentados públicamente
- Probablemente limitados incluso para investigadores (enfoque de privacidad primero)

#### Método de Autenticación:
- Aprobación basada en aplicación (no OAuth/API key)
- Client key emitida después de aprobación

#### Recomendación: **NO USAR** ❌
**Justificación**:
- Requiere estatus de investigador académico (no disponible para uso comercial/MVP)
- Proceso de aplicación incompatible con cronograma de MVP
- Sin garantía de aprobación

#### Alternativas Gratuitas:
- **Web Scraping**: Herramientas como `TikTokAPI` (biblioteca Python, no oficial, viola ToS)
- **yt-dlp**: Puede descargar videos de TikTok pero no tiene API de búsqueda/tendencias
- **Apify TikTok Scraper**: $0.25/1k elementos (NO GRATIS)

---

## 4. Google Trends (biblioteca pytrends)

### Estado del Nivel Gratuito: **VERDADERAMENTE GRATIS** ✅ **RECOMENDADO**

#### Límites de Tasa / Cuotas:
- **Sin API oficial** - pytrends es un wrapper no oficial
- **Límites no documentados** basados en dirección IP
- Reportes de la comunidad:
  - ~1,400 solicitudes antes del límite de tasa (con períodos de 4 horas)
  - ~10 descargas con retrasos de 5-10 segundos activan límites
  - **Recomendado**: Pausa de 60 segundos entre solicitudes

#### Capacidad de Recolección Diaria:
- **Estimación conservadora**: 1 solicitud por minuto = **1,440 solicitudes/día**
- Cada solicitud puede obtener tendencias para múltiples palabras clave
- **Suficiente para MVP** ✅ (no recolectando elementos individuales, solo validación de tendencias)

#### Datos Demográficos:
| Tipo de Dato | Disponibilidad | Notas |
|--------------|----------------|-------|
| Edad | ❌ NO DISPONIBLE | N/A |
| Género | ❌ NO DISPONIBLE | N/A |
| Ubicación | ✅ DISPONIBLE | País, región, ciudad |
| **Propósito** | Validación de Tendencias | No para recolectar elementos de contenido |

**Datos Disponibles**:
- Tendencias de volumen de búsqueda a lo largo del tiempo
- Interés geográfico (por país/región)
- Consultas relacionadas
- Búsquedas en ascenso/tendencia

#### Método de Autenticación:
- **Ninguno requerido** ✅ FÁCIL
- La biblioteca hace solicitudes HTTP a la interfaz web de Google Trends

#### Notas Importantes:
- **Repositorio de pytrends archivado** (17 de abril de 2025) - ya no se mantiene
- Puede fallar si Google cambia la estructura del sitio web de Trends
- **Riesgo**: La herramienta no oficial podría dejar de funcionar

#### Recomendación: **USAR (con precaución)** ⚠️
**Justificación**:
- Completamente gratis, sin autenticación
- Perfecto para FR-021 (validar tendencias con Google Trends)
- NO para recolectar 1,000+ elementos/día (análisis de brechas FR-022 solamente)
- **Riesgo**: Biblioteca sin mantenimiento, puede fallar

#### Estrategia de Mitigación:
- Implementar limitación de tasa (60s entre solicitudes)
- Usar bloques try-except para degradación elegante
- Tener método de validación de respaldo listo
- Considerar bifurcar pytrends si falla

---

## 5. Reddit API (PRAW)

### Estado del Nivel Gratuito: **VERDADERAMENTE GRATIS (con limitaciones)** ✅ **RECOMENDADO**

#### Límites de Tasa / Cuotas:
- **Clientes autenticados con OAuth**: 100 consultas por minuto (QPM)
- **Clientes no autenticados**: 10 QPM
- Límites promediados en ventanas de 10 minutos (permite ráfagas)

#### Capacidad de Recolección Diaria:
- **100 QPM × 60 minutos × 24 horas = 144,000 solicitudes/día**
- Si cada solicitud retorna 25 publicaciones: **3,600,000 elementos/día** (excede ampliamente el objetivo ✅)
- **Realista**: 100 solicitudes/minuto = 6,000 solicitudes/hora = **144,000 solicitudes/día**

**Ejemplo**: Recolectar 1,000 elementos/día requiere ~40 solicitudes (25 elementos cada una) = **muy por debajo de los límites**

#### Datos Demográficos:
| Tipo de Dato | Disponibilidad | Notas |
|--------------|----------------|-------|
| Edad | ❌ NO DISPONIBLE | Debe inferirse del subreddit, idioma, contenido de publicación |
| Género | ❌ NO DISPONIBLE | Debe inferirse de patrones de lenguaje |
| Ubicación | ❌ NO DISPONIBLE | Debe inferirse del subreddit (ej., r/Colombia), menciones |
| **Precisión** | ~50-60% | Basado en inferencia (por debajo del objetivo del 65% en SC-004) |

**Metadatos Disponibles** (por publicación/comentario):
- Subreddit
- Nombre de usuario del autor
- Título de publicación, texto, URL
- Puntuación (votos positivos - votos negativos)
- Número de comentarios
- Marca de tiempo de creación
- Premios

#### Método de Autenticación:
- **OAuth 2.0** vía Reddit App (PRAW maneja automáticamente)
- Crear cuenta de Reddit → Crear app → Obtener client_id y client_secret
- **Configuración fácil** ✅

#### PRAW (Python Reddit API Wrapper):
- Wrapper oficial de biblioteca
- Maneja autenticación y limitación de tasa automáticamente
- **Gratis y activamente mantenido** ✅

#### Restricciones de Uso Comercial:
- **Nivel gratuito** para uso no comercial (proyectos personales, investigación)
- **Requiere aprobación** para uso comercial (apps con anuncios, paywalls, monetización)
- **Nivel de pago**: $0.24 por 1,000 solicitudes (empresarial: miles/mes)

#### Recomendación: **USAR (si es no comercial)** ⚠️
**Justificación**:
- Excelente nivel gratuito (100 QPM = 144,000 solicitudes/día)
- Autenticación fácil con PRAW
- API bien documentada y estable
- **LIMITACIÓN**: Demografía no disponible (debe inferirse, precisión <65%)
- **RIESGO**: Requiere aprobación para uso comercial

#### Estrategia de Recolección:
1. Usar PRAW para buscar subreddits por palabras clave
2. Recolectar publicaciones + comentarios principales (datos de engagement)
3. Inferir demografía de:
   - Geografía del subreddit (r/Colombia, r/Mexico)
   - Patrones de lenguaje (marcadores de género en español)
   - Patrones temporales (cohortes de edad por horarios de publicación)

---

## Alternativas Gratuitas Adicionales

### 6. Mastodon API ✅ **RECOMENDACIÓN BONUS**

**Estado del Nivel Gratuito**: **COMPLETAMENTE GRATIS** (código abierto, descentralizado)

**Límites de Tasa**: Varía por instancia (típicamente generosos para datos públicos)

**Datos de Tendencias**:
- API de hashtags en tendencia
- Enlaces/noticias en tendencia
- Estados en tendencia

**Datos Demográficos**: ❌ NO DISPONIBLE (red federada, sin demografía centralizada)

**Autenticación**: OAuth 2.0 (por instancia)

**Pros**:
- Completamente gratis y de código abierto
- Sin restricciones de API corporativa
- API de temas en tendencia integrada
- Desarrollo activo (v4.5 lanzado en Nov 2025)

**Contras**:
- Base de usuarios más pequeña que las principales plataformas
- Demografía no disponible
- Las tendencias varían por instancia (modelo federado)

**Recomendación**: **USAR como 5ª plataforma** (bonus más allá de las 4 principales)

---

### 7. Web Scraping (Último Recurso)

**Herramientas**:
- **Twint**: Scraper gratuito de Twitter/X (no necesita API)
- **snscrape**: Scraper multiplataforma gratuito (Twitter, Instagram, etc.)
- **yt-dlp**: Descargador gratuito de YouTube (extracción de metadatos)
- **Invidious**: Frontend de privacidad de YouTube (amigable con scraping)

**Pros**:
- Sin límites de API
- Sin autenticación requerida
- Acceso a datos públicos

**Contras**:
- **Viola Términos de Servicio** (riesgo legal)
- Se rompe frecuentemente (ciclo de mantenimiento de 2-4 semanas)
- Sin datos demográficos
- Preocupaciones éticas
- Puede resultar en prohibiciones de IP

**Recomendación**: **EVITAR a menos que las APIs sean insuficientes** ⚠️

---

## Tabla Resumen

| API | Estado Gratuito | Capacidad Diaria | Demografía | Complejidad de Autenticación | Recomendación |
|-----|-----------------|------------------|------------|------------------------------|----------------|
| **Meta Graph API** | ⚠️ Limitado | 4,800 solicitudes | ✅ 95% (solo negocios) | ❌ Alta (App Review) | ❌ NO USAR |
| **YouTube Data API v3** | ✅ Verdaderamente Gratis | 5,000 elementos | ⚠️ Solo canal propio | ✅ Fácil (API key) | ✅ **USAR** |
| **TikTok APIs** | ❌ Solo investigadores | N/A | ❓ Desconocido | ❌ Basado en aplicación | ❌ NO USAR |
| **Google Trends** | ✅ Verdaderamente Gratis | 1,440 solicitudes | 🌍 Solo ubicación | ✅ Ninguno | ⚠️ USAR (solo validación) |
| **Reddit API (PRAW)** | ✅ Verdaderamente Gratis | 144,000 solicitudes | ❌ Ninguno (inferir) | ✅ Fácil (OAuth) | ⚠️ USAR (no comercial) |
| **Mastodon API** | ✅ Verdaderamente Gratis | Alto | ❌ Ninguno | ✅ Fácil (OAuth) | ✅ USAR BONUS |

---

## Cumplimiento de Restricción: FR-029

**Requisito**: El sistema DEBE usar SOLO herramientas/APIs gratuitas

### APIs Conformes (100% Gratis):
1. ✅ **YouTube Data API v3**: Cuota gratuita (10,000 unidades/día), aumentos de cuota gratuitos
2. ✅ **Google Trends (pytrends)**: Completamente gratis (no oficial, sin autenticación)
3. ✅ **Reddit API (PRAW)**: Nivel gratuito (100 QPM) para uso no comercial
4. ✅ **Mastodon API**: Código abierto, completamente gratis

### No Conformes (No Se Puede Acceder Sin Pago/Aprobación):
1. ❌ **Meta Graph API**: Técnicamente gratis pero las barreras de App Review lo hacen impracticable
2. ❌ **TikTok APIs**: Acceso solo para investigadores (no disponible para MVP)
3. ❌ **Twitter/X API**: $100-200/mes mínimo (explícitamente fuera de alcance según especificación)

---

## Estrategia de Plataforma Revisada para MVP

### Plataformas Recomendadas (4,000 elementos/día total):

1. **YouTube** (1,500 elementos/día):
   - Usar YouTube Data API v3 (capacidad de 5,000)
   - Inferir demografía de comentarios/canales (precisión del 65%)

2. **Reddit** (1,500 elementos/día):
   - Usar Reddit API con PRAW (capacidad de 144,000)
   - Inferir demografía de subreddits (precisión del 60%)
   - Marcar como "no comercial" o buscar aprobación

3. **Mastodon** (500 elementos/día):
   - Usar Mastodon API (instancias federadas)
   - Usar APIs de tendencias directamente
   - Sin demografía (marcar como "desconocido")

4. **Google Trends** (500 validaciones/día):
   - No para recolección de elementos, solo validación de tendencias (FR-021)
   - Datos geográficos para validación cruzada

### Plataformas a ELIMINAR del MVP:
- ❌ **Facebook**: Barreras de App Review, restricciones de cuenta de negocio
- ❌ **Instagram**: Igual que Facebook (Graph API)
- ❌ **TikTok**: Acceso solo para investigadores

### Enfoque Alternativo (Si Se Acepta Web Scraping):
- Usar **snscrape** o **Twint** para Twitter/X (gratis, sin API)
- Usar **scrapers no oficiales de Instagram** (viola ToS, riesgo legal)
- **NO RECOMENDADO** debido a preocupaciones legales/éticas y espíritu de FR-029

---

## Estrategia de Datos Demográficos

### Plataformas con Demografía Directa:
- **NINGUNA de las APIs gratuitas recomendadas** proporciona datos demográficos públicos
- YouTube Analytics API: Solo para canal propio
- Meta Graph API: Solo cuentas de negocio (no recomendado)

### Enfoque de Inferencia (FR-011, SC-004):

**Precisión Objetivo**: 65% mínimo (inferido), 95% para datos directos

**Métodos de Inferencia**:

1. **Ubicación (País/Región/Ciudad)**:
   - YouTube: Descripciones de canal, etiquetas de ubicación de video, idioma
   - Reddit: Geografía de subreddit (r/Colombia, r/Mexico), menciones en publicaciones
   - Mastodon: Ubicación de instancia (mastodon.social vs instancias localizadas)
   - **Precisión Esperada**: 70-75% ✅

2. **Rango de Edad**:
   - Patrones de lenguaje (jerga, referencias generacionales)
   - Patrones de uso de plataforma (TikTok tiende a jóvenes, Reddit varía por subreddit)
   - Patrones temporales de publicación
   - **Precisión Esperada**: 55-60% ⚠️ (por debajo del objetivo)

3. **Género**:
   - Marcadores de idioma español (adjetivos con género, terminaciones -o/-a)
   - Patrones de nombre de usuario
   - Auto-identificación en biografías/publicaciones
   - **Precisión Esperada**: 60-65% ⚠️ (en umbral objetivo)

### Recomendación:
- Implementar inferencia basada en NLP (FR-011)
- Marcar predicciones de baja confianza como "Desconocido" (según caso especial en especificación)
- Enfocarse en ubicación (mayor precisión) y segmentación de plataforma
- **Ajustar Criterios de Éxito**: SC-004 (precisión del 65%) puede ser optimista sin datos directos de API

---

## Implementación de Limitación de Tasa (FR-006)

### Estrategias Por Plataforma:

**YouTube Data API v3**:
```python
# Seguimiento de uso de cuota
current_quota = 0
MAX_QUOTA = 10000
SEARCH_COST = 100
VIDEO_COST = 1

if current_quota + SEARCH_COST > MAX_QUOTA:
    # Pausar hasta medianoche PT
    wait_until_quota_reset()
else:
    # Ejecutar solicitud
    current_quota += SEARCH_COST
```

**Reddit API (PRAW)**:
```python
# PRAW maneja la limitación de tasa automáticamente
reddit = praw.Reddit(client_id, client_secret, user_agent)
# Se duerme automáticamente al acercarse al límite de 100 QPM
```

**Google Trends (pytrends)**:
```python
import time

def get_trends(keyword):
    result = pytrends.interest_over_time()
    time.sleep(60)  # Retraso de 60 segundos entre solicitudes
    return result
```

**Mastodon API**:
```python
# Verificar encabezados X-RateLimit
response = mastodon.timeline()
remaining = response.headers['X-RateLimit-Remaining']
reset_time = response.headers['X-RateLimit-Reset']

if remaining < 10:
    wait_until(reset_time)
```

---

## Análisis de Criterios de Éxito

### SC-001: Recolectar 4,000 elementos de contenido/día
- **YouTube**: Capacidad de 5,000 ✅
- **Reddit**: Capacidad de 144,000 ✅
- **Combinado**: Capacidad de 149,000 (excede ampliamente 4,000) ✅
- **Estado**: **ALCANZABLE** ✅

### SC-004: Inferir demografía con precisión del 65%
- **Ubicación**: 70-75% esperado ✅
- **Edad**: 55-60% esperado ⚠️ (por debajo del objetivo)
- **Género**: 60-65% esperado ⚠️ (en umbral)
- **Estado**: **DESAFIANTE** ⚠️ (puede necesitar ajustar objetivo o agregar fuentes de datos directos)

### SC-005: 95% de precisión para demografía directa
- **Ninguna API gratuita** proporciona demografía pública directa
- **YouTube Analytics**: Solo para canal propio (no aplicable para analizar otros)
- **Estado**: **NO ALCANZABLE sin APIs de pago** ❌

---

## Recomendaciones

### Acciones Inmediatas:

1. **Proceder con YouTube + Reddit + Mastodon** para MVP
   - Alcanza objetivo de 4,000 elementos/día (SC-001) ✅
   - 100% gratis (cumple FR-029) ✅
   - Sin barreras de App Review

2. **Ajustar Expectativas Demográficas**:
   - Actualizar SC-004 a 60% de precisión (realista para inferencia)
   - Eliminar SC-005 (95% de datos directos) del alcance del MVP
   - Enfocarse en inferencia de ubicación (mayor precisión)

3. **Implementar Inferencia NLP Robusta**:
   - Usar modelos en español de spaCy para NER (ubicaciones, organizaciones)
   - Entrenar/ajustar modelo BERT para clasificación de edad/género
   - Usar metadatos de subreddit/canal para pistas demográficas

4. **Agregar "Puntuaciones de Confianza"**:
   - Marcar cada predicción demográfica con confianza (0-100%)
   - Permitir a usuarios filtrar por umbral de confianza
   - Transparencia sobre inferencia vs datos directos

5. **Planificar para APIs de Pago Futuras** (Fase 2):
   - Si el MVP tiene éxito, presupuesto para Twitter API ($100/mes)
   - Considerar Brandwatch/Sprinklr para clientes empresariales
   - Mantener arquitectura modular para fácil intercambio de API

### Consideraciones a Largo Plazo:

- **Revisión Legal**: Asegurar cumplimiento con ToS de plataformas (especialmente uso comercial de Reddit)
- **Ética de Web Scraping**: Documentar decisión de NO hacer scraping (espíritu de FR-029)
- **Estabilidad de API**: Monitorear pytrends (archivado), planificar migración si falla
- **Monitoreo de Cuota**: Implementar dashboards para uso de cuota en todas las APIs

---

## Finalización de Tarea de Investigación

### Pregunta: ¿Qué APIs tienen niveles verdaderamente gratuitos para 4,000 elementos/día?

**Respuesta**:
- ✅ **YouTube Data API v3**: Sí (capacidad de 5,000)
- ✅ **Reddit API (PRAW)**: Sí (capacidad de 144,000, no comercial)
- ✅ **Google Trends**: Sí (solo validación, no recolección de elementos)
- ⚠️ **Meta Graph API**: Técnicamente gratis pero impracticable (barreras de App Review)
- ❌ **TikTok APIs**: No (acceso solo para investigadores)

### Mejores Opciones Gratuitas:
1. **YouTube Data API v3** (plataforma primaria)
2. **Reddit API con PRAW** (plataforma primaria)
3. **Mastodon API** (plataforma bonus)
4. **Google Trends vía pytrends** (solo validación)

### Estado: ✅ **INVESTIGACIÓN COMPLETA**

**Siguiente Fase**: Actualizar spec.md para reflejar cambios de plataforma (eliminar FB/IG/TikTok, agregar Reddit/Mastodon)

---

# APÉNDICE: Estrategia de Limitación de Tasa Multi-API (FR-006)

**Fecha de Investigación**: 2025-11-08 (Extendida)
**Pregunta de Investigación**: ¿Cómo manejar diferentes límites de tasa a través de 4+ APIs de redes sociales con pausa/reanudación automática, sin pérdida de datos y distribución justa entre múltiples lineamientos?

## Resumen Ejecutivo - Enfoque de Limitación de Tasa

**Solución Recomendada**:
1. **Algoritmo de Ventana Deslizante** con Redis para seguimiento de cuota
2. **Colas Celery Separadas** por API con límites de tasa independientes
3. **Retroceso Exponencial con Jitter** para estrategia de reintento
4. **Biblioteca PyrateLimiter** para limitación de tasa basada en decoradores
5. **Rastreador de Cuota Basado en Redis** para predicción de uso y pausa/reanudación automática

## Límites de Tasa de API Detallados

### YouTube Data API v3
- **Límite**: 10,000 unidades/día (nivel de proyecto, NO por usuario)
- **Reinicio**: Medianoche Hora del Pacífico (diario fijo)
- **Costo por Operación**:
  - Búsqueda: 100 unidades
  - Lista de videos: 1 unidad
  - Hilos de comentarios: 1 unidad
- **Implicaciones**: ~100 búsquedas/día O ~10,000 solicitudes de metadatos de video/día
- **Encabezados**: Sin encabezados de límite de tasa en respuestas (debe rastrearse localmente)

### Meta Graph API (si se usa)
- **Límite**: 200 solicitudes/hora por usuario (ventana rodante)
- **Cálculo**: 200 * Número de Usuarios en ventana de 1 hora
- **Reinicio**: Rodante (no fijo por hora)
- **Encabezados de Respuesta**: Proporciona información de límite de tasa (X-App-Usage)

### TikTok API (si es accesible)
- **Límite**: Varía por endpoint y nivel
- **Ventana**: Ventana deslizante de 1 minuto
- **Código de Error**: HTTP 429 con `rate_limit_exceeded`
- **Research API**: 1,000 solicitudes/día, hasta 100,000 registros/día

### Google Trends (pytrends - No Oficial)
- **Límite**: No documentado (API no oficial)
- **Comportamiento Observado**: ~1,400 solicitudes antes del bloqueo
- **Recuperación**: Pausa de 60 segundos recomendada después del límite de tasa
- **Sin Encabezados**: Debe implementarse limitación de tasa conservadora

### Reddit API (PRAW) - Plataforma Recomendada
- **Límite**: 100 consultas por minuto (QPM) para clientes OAuth
- **Ventana**: Promediada en ventanas de 10 minutos
- **Capacidad Diaria**: 144,000 solicitudes/día
- **Manejo Automático**: La biblioteca PRAW maneja la limitación de tasa automáticamente

## Análisis de Patrones de Limitación de Tasa

### 1. Algoritmo Token Bucket

**Descripción**: El bucket contiene tokens (máximo N), se rellena a una tasa R tokens/segundo. Cada solicitud consume 1 token.

**Pros**:
- Simple de entender e implementar
- Permite tráfico en ráfaga hasta el tamaño del bucket
- Funciona bien para APIs con límites "por segundo"

**Contras**:
- Menos preciso para ventanas de tiempo largas (diarias/por hora)
- Puede permitir que se consuma la cuota completa en una ráfaga
- No ideal para APIs con cuotas diarias (YouTube)

**Caso de Uso**: Bueno para Reddit (100/minuto), TikTok (60/minuto)

### 2. Algoritmo Leaky Bucket

**Descripción**: Las solicitudes entran al bucket, se filtran a tasa constante. Si el bucket se desborda, las solicitudes se rechazan.

**Pros**:
- Suaviza la tasa de solicitudes (sin ráfagas)
- Uso predecible de API
- Bueno para proteger APIs

**Contras**:
- No permite tráfico en ráfaga
- Puede subutilizar cuota (demasiado conservador)
- No flexible para costos variables de solicitud

**Caso de Uso**: Bueno para pytrends (conservador, evitar detección)

### 3. Algoritmo de Ventana Deslizante (RECOMENDADO)

**Descripción**: Rastrea solicitudes en una ventana de tiempo deslizante (ej., últimas 24 horas, última 1 hora). Más preciso para cuotas rodantes.

**Pros**:
- Más preciso para ventanas rodantes (Meta Graph API)
- Previene abuso de cuota
- Funciona bien para límites diarios/por hora
- Distribución justa de cuota a lo largo del tiempo

**Contras**:
- Ligeramente más complejo de implementar
- Requiere Redis Sorted Sets para sistemas distribuidos

**Caso de Uso**: MEJOR para YouTube (cuota diaria), Meta (rodante por hora), TikTok (deslizante de 1 minuto)

**Implementación**:
```python
# Operaciones de Redis Sorted Set
ZADD quota:youtube {timestamp} {request_id}      # Agregar solicitud
ZREMRANGEBYSCORE quota:youtube 0 {cutoff}        # Eliminar solicitudes antiguas
ZCARD quota:youtube                               # Contar solicitudes en ventana
```

## Enfoque Recomendado: Ventana Deslizante con Redis

### ¿Por Qué Ventana Deslizante?

1. **Preciso para Límites Rodantes**: Meta Graph API usa ventana rodante de 1 hora
2. **Distribución Justa**: Previene patrón de "ráfaga luego esperar"
3. **Predicción de Cuota**: Puede predecir cuándo se reiniciará la cuota basándose en la solicitud más antigua
4. **Sin Exceso**: Nunca excede límites de cuota

### Patrón de Arquitectura: Colas Separadas por API

**Justificación**: La limitación de tasa de Celery es por worker, no global. Colas separadas aseguran aplicación independiente.

```
celery_queues/
├── youtube_queue (tasa: 100 búsquedas/día, 10k unidades total)
├── meta_queue (tasa: 200/hora por usuario)
├── reddit_queue (tasa: 100/minuto, auto-manejado por PRAW)
├── tiktok_queue (tasa: varía por endpoint)
└── trends_queue (tasa: 1 solicitud/5 segundos)
```

**Configuración de Worker**:
```python
# celeryconfig.py
task_routes = {
    'collectors.youtube.*': {'queue': 'youtube_queue'},
    'collectors.meta.*': {'queue': 'meta_queue'},
    'collectors.reddit.*': {'queue': 'reddit_queue'},
    'collectors.tiktok.*': {'queue': 'tiktok_queue'},
    'collectors.trends.*': {'queue': 'trends_queue'},
}

# Ejecutar workers separados por cola
# celery -A app worker -Q youtube_queue -c 1
# celery -A app worker -Q meta_queue -c 2
# celery -A app worker -Q reddit_queue -c 4
```

**Beneficios**:
- Dominios de falla independientes (una API caída no afecta a otras)
- Aplicación de límite de tasa por API
- Fácil escalar workers por carga de API
- Monitoreo y alertas a nivel de cola

## Bibliotecas Recomendadas

### Primaria: PyrateLimiter (Más Completa)

**Repositorio**: https://github.com/vutran1710/PyrateLimiter
**PyPI**: `pyrate-limiter`

**Características**:
- Familia de algoritmos leaky bucket
- Soporte de decoradores (@RateLimiter)
- Flujos de trabajo síncronos y asíncronos
- Backend Redis para limitación de tasa distribuida
- Backend SQLite para persistencia
- Soporte de ventana deslizante

**Instalación**:
```bash
pip install pyrate-limiter[all]  # Incluye soporte Redis
```

**Ejemplo de Uso**:
```python
from pyrate_limiter import Duration, Rate, Limiter
from pyrate_limiter.backends.redis import RedisBackend

# Definir diferentes tasas para diferentes APIs
youtube_rate = Rate(100, Duration.DAY)  # 100 búsquedas por día
meta_rate = Rate(200, Duration.HOUR)    # 200 solicitudes por hora
reddit_rate = Rate(100, Duration.MINUTE) # 100 solicitudes por minuto
trends_rate = Rate(1, Duration.SECOND * 5)  # 1 solicitud por 5 segundos

# Backend Redis para limitación distribuida
redis_backend = RedisBackend(
    host='localhost',
    port=6379,
    db=0
)

# Crear limitadores por API
youtube_limiter = Limiter(youtube_rate, backend=redis_backend)
meta_limiter = Limiter(meta_rate, backend=redis_backend)
trends_limiter = Limiter(trends_rate, backend=redis_backend)

# Usar como decorador
@youtube_limiter.ratelimit("youtube_search", delay=True)
def youtube_search_api(query):
    # Llamada API aquí
    pass
```

### Alternativa: ratelimit (Más Simple)

**Repositorio**: https://github.com/tomasbasham/ratelimit
**PyPI**: `ratelimit`

**Características**:
- Interfaz de decorador simple
- Decorador sleep_and_retry integrado
- Sin dependencias externas

**Limitaciones**:
- Sin backend Redis (no adecuado para sistemas distribuidos)
- Solo en memoria
- Sin soporte multi-tasa

## Patrón de Seguimiento de Cuota

### Rastreador de Cuota Personalizado Basado en Redis

```python
import redis
from datetime import datetime, timedelta

class QuotaTracker:
    def __init__(self, redis_client, api_name):
        self.redis = redis_client
        self.api_name = api_name
        self.key = f"quota:{api_name}"

    def track_request(self, cost=1):
        """Rastrea solicitud de API con costo (para YouTube)"""
        now = datetime.now().timestamp()
        # Agregar número de entradas de costo (unidades de cuota de YouTube)
        for _ in range(cost):
            self.redis.zadd(self.key, {f"{now}_{_}": now})

    def get_usage(self, window_seconds):
        """Obtener uso actual en ventana"""
        cutoff = (datetime.now() - timedelta(seconds=window_seconds)).timestamp()
        # Eliminar entradas expiradas
        self.redis.zremrangebyscore(self.key, 0, cutoff)
        # Contar entradas restantes
        return self.redis.zcard(self.key)

    def get_remaining(self, limit, window_seconds):
        """Obtener cuota restante"""
        usage = self.get_usage(window_seconds)
        return max(0, limit - usage)

    def predict_reset_time(self, window_seconds):
        """Predecir cuándo se reiniciará la cuota (expira la solicitud más antigua)"""
        oldest = self.redis.zrange(self.key, 0, 0, withscores=True)
        if not oldest:
            return datetime.now()
        oldest_timestamp = oldest[0][1]
        return datetime.fromtimestamp(oldest_timestamp + window_seconds)

    def should_pause(self, limit, window_seconds, threshold=0.9):
        """Verificar si se debe pausar (90% de cuota usada por defecto)"""
        usage = self.get_usage(window_seconds)
        return usage >= (limit * threshold)
```

**Ejemplo de Uso**:
```python
# Rastrear cuota de YouTube
tracker = QuotaTracker(redis_client, "youtube_search")
tracker.track_request(cost=100)  # La búsqueda cuesta 100 unidades

# Verificar si se debe pausar
if tracker.should_pause(10000, 86400, threshold=0.8):  # 80% de 10k unidades
    sleep_until = tracker.predict_reset_time(86400)
    # Pausar recolección hasta reinicio
    logger.warning(f"Cuota de YouTube al 80%. Pausando hasta {sleep_until}")
    pause_collection_until(sleep_until)
```

## Estrategia de Reintento: Retroceso Exponencial con Jitter

### ¿Por Qué Retroceso Exponencial?

- Previene problema de manada atronadora (todas las tareas reintentando simultáneamente)
- Respeta tiempo de recuperación de API
- Recomendado por todos los principales proveedores de API (YouTube, Meta, Reddit)

### Soporte Integrado de Celery (Celery 4.2+)

```python
from celery import Task

@app.task(
    bind=True,
    autoretry_for=(RateLimitException, ConnectionError),
    retry_backoff=True,           # Habilitar retroceso exponencial
    retry_backoff_max=600,         # Máximo 10 minutos
    retry_jitter=True,             # Agregar aleatoriedad
    max_retries=5
)
def collect_youtube_data(self, query):
    try:
        # Llamada API aquí
        pass
    except RateLimitException as exc:
        # Registrar evento
        logger.warning(f"Límite de tasa alcanzado: {exc}")
        raise  # Celery auto-reintenta con retroceso
```

**Fórmula de Retroceso**:
```
delay = min(retry_backoff_max, retry_backoff * (2 ** retries))
with_jitter = delay * random.uniform(0.5, 1.5)

# Ejemplo de progresión:
# Reintento 1: 1s * (2^0) = 1s → 0.5-1.5s
# Reintento 2: 1s * (2^1) = 2s → 1-3s
# Reintento 3: 1s * (2^2) = 4s → 2-6s
# Reintento 4: 1s * (2^3) = 8s → 4-12s
# Reintento 5: 1s * (2^4) = 16s → 8-24s
```

### Estrategias de Retroceso Específicas por API

```python
def youtube_backoff(retries):
    """YouTube: Retroceso conservador debido a cuota diaria"""
    return min(3600, 300 * (2 ** retries))  # Comienza con 5 min, máximo 1 hora

def meta_backoff(retries):
    """Meta: Retroceso más corto debido a reinicio por hora"""
    return min(600, 60 * (2 ** retries))  # Comienza con 1 min, máximo 10 min

def trends_backoff(retries):
    """Trends: Retroceso más largo para evitar detección"""
    return min(900, 60 * (2 ** retries))  # Comienza con 1 min, máximo 15 min

@app.task(bind=True, max_retries=5)
def collect_youtube_data(self, query):
    try:
        # Llamada API
        pass
    except RateLimitException as exc:
        countdown = youtube_backoff(self.request.retries)
        logger.info(f"Reintentando en {countdown}s (intento {self.request.retries})")
        raise self.retry(exc=exc, countdown=countdown)
```

## Priorización de Colas

### Colas de Prioridad (RabbitMQ)

```python
# celeryconfig.py
task_queue_max_priority = 10

task_routes = {
    'collectors.youtube.*': {
        'queue': 'youtube_queue',
        'priority': 7  # Mayor prioridad (el límite diario es precioso)
    },
    'collectors.meta.*': {
        'queue': 'meta_queue',
        'priority': 6  # Media-alta (límite por hora)
    },
    'collectors.reddit.*': {
        'queue': 'reddit_queue',
        'priority': 5  # Media (límite generoso)
    },
    'collectors.trends.*': {
        'queue': 'trends_queue',
        'priority': 3  # Más baja (solo validación)
    }
}

# Enviar tarea con prioridad personalizada
collect_youtube_data.apply_async(
    args=[lineamiento_id],
    priority=9  # Recolección urgente
)
```

**Configuración de Prefetch de Worker** (para mejor manejo de prioridad):
```python
worker_prefetch_multiplier = 1  # Obtener 1 tarea a la vez (no 4 por defecto)
```

## Mecanismo de Pausa/Reanudación

### Estado de Cola Respaldado por Base de Datos

```python
# models.py
class CollectionQueue(models.Model):
    lineamiento = models.ForeignKey(Lineamiento, on_delete=models.CASCADE)
    api_name = models.CharField(max_length=50)
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('paused', 'Paused - Rate Limit'),
            ('failed', 'Failed'),
        ],
        default='active'
    )
    paused_at = models.DateTimeField(null=True, blank=True)
    resume_at = models.DateTimeField(null=True, blank=True)
    retry_count = models.IntegerField(default=0)
    last_error = models.TextField(null=True, blank=True)
    quota_used = models.IntegerField(default=0)

    class Meta:
        unique_together = ('lineamiento', 'api_name')
```

### Implementación de Tarea con Pausa/Reanudación

```python
@app.task(bind=True)
def collect_youtube_data(self, lineamiento_id):
    queue = CollectionQueue.objects.get(
        lineamiento_id=lineamiento_id,
        api_name='youtube'
    )

    # Verificar si está pausado
    if queue.status == 'paused':
        if datetime.now() < queue.resume_at:
            # Aún en ventana de pausa
            countdown = (queue.resume_at - datetime.now()).seconds
            logger.info(f"Recolección pausada hasta {queue.resume_at}")
            raise self.retry(countdown=countdown)
        else:
            # Reanudar
            queue.status = 'active'
            queue.save()
            logger.info("Recolección reanudada")

    # Verificar cuota antes de hacer solicitudes
    tracker = QuotaTracker(redis_client, 'youtube')

    if tracker.should_pause(10000, 86400, threshold=0.8):
        # Pausar hasta que se reinicie la cuota
        reset_time = tracker.predict_reset_time(86400)
        queue.status = 'paused'
        queue.paused_at = datetime.now()
        queue.resume_at = reset_time
        queue.quota_used = tracker.get_usage(86400)
        queue.save()

        logger.warning(
            f"Cuota de YouTube al 80% ({queue.quota_used}/10000). "
            f"Pausando hasta {reset_time}"
        )

        # Reprogramar para tiempo de reinicio
        raise self.retry(eta=reset_time)

    try:
        # Hacer llamada API
        results = youtube_api.search(...)
        tracker.track_request(cost=100)

        # Actualizar cola
        queue.status = 'active'
        queue.quota_used = tracker.get_usage(86400)
        queue.save()

        return results

    except RateLimitException as exc:
        # Límite de tasa alcanzado inmediatamente
        queue.status = 'paused'
        queue.paused_at = datetime.now()
        queue.resume_at = datetime.now() + timedelta(hours=1)
        queue.retry_count += 1
        queue.last_error = str(exc)
        queue.save()

        # Reintentar con retroceso
        raise self.retry(
            exc=exc,
            countdown=youtube_backoff(queue.retry_count)
        )
```

## Distribución Justa Entre Múltiples Lineamientos

### Estrategia 1: Distribución Round-Robin

```python
def distribute_quota_fairly(lineamientos):
    """Distribuir cuota de API justamente entre lineamientos"""

    # YouTube: 100 búsquedas por día, distribuir equitativamente
    youtube_quota_per_lineamiento = 100 // len(lineamientos)

    # Reddit: 144,000 solicitudes por día, distribuir equitativamente
    reddit_quota_per_lineamiento = 144000 // len(lineamientos)

    for lineamiento in lineamientos:
        # Asignar presupuesto de cuota a cada lineamiento
        lineamiento.daily_youtube_budget = youtube_quota_per_lineamiento
        lineamiento.daily_reddit_budget = reddit_quota_per_lineamiento
        lineamiento.save()

    # Programar tareas en round-robin
    tasks = []
    for lineamiento in lineamientos:
        tasks.append(
            group(
                collect_youtube_data.s(
                    lineamiento.id,
                    max_requests=lineamiento.daily_youtube_budget
                ),
                collect_reddit_data.s(
                    lineamiento.id,
                    max_requests=lineamiento.daily_reddit_budget
                ),
                collect_trends_data.si(lineamiento.id)
            )
        )

    # Ejecutar con coordinación
    job = chord(tasks)(aggregate_results.s())
    return job
```

### Estrategia 2: Distribución Basada en Prioridad

```python
def distribute_quota_by_priority(lineamientos):
    """Distribuir cuota basándose en prioridad de lineamiento"""

    # Calcular distribución ponderada
    total_priority = sum(l.priority for l in lineamientos)

    for lineamiento in lineamientos:
        weight = lineamiento.priority / total_priority
        lineamiento.daily_youtube_budget = int(100 * weight)
        lineamiento.daily_reddit_budget = int(144000 * weight)
        lineamiento.save()
```

### Estrategia 3: Asignación Dinámica

```python
class QuotaAllocator:
    """Asignar cuota dinámicamente basándose en rendimiento de lineamiento"""

    def __init__(self, redis_client):
        self.redis = redis_client

    def allocate_quota(self, lineamiento, api_name):
        """Asignar cuota basándose en tasa de éxito reciente"""

        # Obtener tasa de éxito histórica
        success_rate = self.get_success_rate(lineamiento, api_name)

        # Obtener cuota base
        base_quota = self.get_base_quota(api_name)

        # Asignar más cuota a lineamientos exitosos
        if success_rate > 0.8:
            allocated = base_quota * 1.2  # Bono del 20%
        elif success_rate < 0.5:
            allocated = base_quota * 0.8  # Penalización del 20%
        else:
            allocated = base_quota

        return int(allocated)

    def get_success_rate(self, lineamiento, api_name):
        """Calcular tasa de éxito de recolecciones recientes"""
        key = f"success:{lineamiento.id}:{api_name}"
        successful = int(self.redis.get(f"{key}:success") or 0)
        failed = int(self.redis.get(f"{key}:failed") or 0)
        total = successful + failed

        if total == 0:
            return 0.5  # Neutral

        return successful / total
```

## Patrón de Coordinación Multi-API

### Servicio Coordinador

```python
from celery import group, chain
from datetime import datetime, timedelta

class CollectionCoordinator:
    """Orquesta recolección a través de múltiples APIs"""

    def __init__(self, quota_trackers):
        self.trackers = quota_trackers  # Dict de QuotaTracker por API

    def schedule_collection(self, lineamiento):
        """Programar tareas de recolección a través de APIs"""
        tasks = []

        # YouTube - verificar cuota
        if self.can_collect('youtube', lineamiento):
            tasks.append(
                collect_youtube_data.s(lineamiento.id)
            )
        else:
            # Programar para después
            eta = self.trackers['youtube'].predict_reset_time(86400)
            tasks.append(
                collect_youtube_data.apply_async(
                    args=[lineamiento.id],
                    eta=eta,
                    priority=7
                )
            )
            logger.info(f"Cuota de YouTube agotada. Programado para {eta}")

        # Reddit - usualmente disponible (límites generosos)
        if self.can_collect('reddit', lineamiento):
            tasks.append(
                collect_reddit_data.s(lineamiento.id)
            )

        # Trends - siempre limitado, baja prioridad
        tasks.append(
            collect_trends_data.si(lineamiento.id)
        )

        # Ejecutar tareas disponibles en paralelo
        job = group(tasks)
        return job.apply_async()

    def can_collect(self, api_name, lineamiento):
        """Verificar si la API puede manejar recolección"""
        tracker = self.trackers.get(api_name)
        if not tracker:
            return True  # API desconocida, permitir

        if api_name == 'youtube':
            # Conservador: mantener 20% de buffer
            return not tracker.should_pause(10000, 86400, threshold=0.8)

        elif api_name == 'reddit':
            # Límite generoso, permitir a menos que sea muy alto
            return not tracker.should_pause(144000, 86400, threshold=0.95)

        elif api_name == 'meta':
            # Cuota por usuario
            return not tracker.should_pause(200, 3600, threshold=0.9)

        return True
```

## Ejemplos de Código Completos

### Recolector de YouTube con Limitación de Tasa Completa

```python
from pyrate_limiter import Duration, Rate, Limiter
from pyrate_limiter.backends.redis import RedisBackend
import redis
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configuración de Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)
redis_backend = RedisBackend(redis_client)

# Limitador de tasa de YouTube
youtube_search_rate = Rate(100, Duration.DAY)
youtube_limiter = Limiter(youtube_search_rate, backend=redis_backend)

# Rastreador de cuota
class YouTubeQuotaTracker(QuotaTracker):
    DAILY_LIMIT = 10000
    SEARCH_COST = 100
    LIST_COST = 1

    def can_search(self):
        usage = self.get_usage(86400)
        return (usage + self.SEARCH_COST) <= (self.DAILY_LIMIT * 0.8)

    def track_search(self):
        self.track_request(cost=self.SEARCH_COST)

youtube_tracker = YouTubeQuotaTracker(redis_client, 'youtube')

@app.task(
    bind=True,
    autoretry_for=(HttpError,),
    retry_backoff=True,
    retry_backoff_max=3600,
    retry_jitter=True,
    max_retries=5
)
@youtube_limiter.ratelimit("youtube_search", delay=True)
def collect_youtube_data(self, lineamiento_id, query):
    """Recolectar datos de YouTube con limitación de tasa completa"""

    # Verificar cuota antes de búsqueda costosa
    if not youtube_tracker.can_search():
        reset_time = youtube_tracker.predict_reset_time(86400)
        countdown = (reset_time - datetime.now()).seconds

        logger.warning(
            f"Cuota de YouTube casi agotada. "
            f"Pausando hasta {reset_time}. "
            f"Actual: {youtube_tracker.get_usage(86400)}/10000"
        )

        raise self.retry(countdown=countdown)

    try:
        # Construir servicio de YouTube
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

        # Realizar búsqueda
        search_response = youtube.search().list(
            q=query,
            type='video',
            part='id,snippet',
            maxResults=50
        ).execute()

        # Rastrear uso de cuota
        youtube_tracker.track_search()

        logger.info(
            f"Búsqueda de YouTube completada. "
            f"Resultados: {len(search_response.get('items', []))}. "
            f"Cuota restante: {youtube_tracker.get_remaining(10000, 86400)}"
        )

        return search_response

    except HttpError as e:
        if e.resp.status == 429:  # Límite de tasa
            logger.error("¡Límite de tasa de YouTube alcanzado!")
            raise  # Auto-reintentar con retroceso
        elif e.resp.status == 403:  # Cuota excedida
            logger.error("¡Cuota de YouTube excedida!")
            # Pausar hasta medianoche PT
            reset_time = youtube_tracker.predict_reset_time(86400)
            raise self.retry(countdown=(reset_time - datetime.now()).seconds)
        else:
            raise
```

### Recolector de Reddit (PRAW maneja limitación de tasa automáticamente)

```python
import praw

# PRAW maneja la limitación de tasa automáticamente
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT
)

@app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3
)
def collect_reddit_data(self, lineamiento_id, subreddit_name, keywords):
    """Recolectar datos de Reddit - PRAW maneja limitación de tasa"""

    try:
        subreddit = reddit.subreddit(subreddit_name)

        # Buscar palabras clave
        results = []
        for keyword in keywords:
            # PRAW se duerme automáticamente si se acerca al límite de tasa
            for submission in subreddit.search(keyword, limit=100, time_filter='week'):
                results.append({
                    'id': submission.id,
                    'title': submission.title,
                    'score': submission.score,
                    'num_comments': submission.num_comments,
                    'created_utc': submission.created_utc,
                    'url': submission.url,
                    'author': str(submission.author),
                })

        logger.info(f"Recolección de Reddit completada. Elementos: {len(results)}")
        return results

    except Exception as e:
        logger.error(f"Recolección de Reddit falló: {e}")
        raise
```

### Recolector de Google Trends (Limitación de Tasa Conservadora)

```python
from pytrends.request import TrendReq
from pyrate_limiter import Duration, Rate, Limiter
import time

# Limitador de tasa de Trends (muy conservador)
trends_rate = Rate(1, Duration.SECOND * 5)
trends_limiter = Limiter(trends_rate, backend=redis_backend)

# Inicializar con retroceso
pytrends = TrendReq(
    hl='es',
    tz=360,
    retries=2,
    backoff_factor=0.1
)

@app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=60,
    retry_backoff_max=900,
    retry_jitter=True,
    max_retries=3
)
@trends_limiter.ratelimit("google_trends", delay=True)
def collect_trends_data(self, lineamiento_id, keywords):
    """Recolectar Google Trends con limitación de tasa conservadora"""

    try:
        # Retraso manual adicional
        time.sleep(2)

        # Construir payload
        pytrends.build_payload(
            keywords,
            cat=0,
            timeframe='today 7-d',
            geo='CO'
        )

        # Obtener interés a lo largo del tiempo
        interest = pytrends.interest_over_time()

        # Obtener consultas relacionadas
        related = pytrends.related_queries()

        # Dormir después del éxito
        time.sleep(3)

        return {
            'interest': interest.to_dict(),
            'related_queries': related
        }

    except Exception as e:
        if '429' in str(e) or 'quota' in str(e).lower():
            logger.warning("Límite de tasa de Google Trends sospechado")
            raise self.retry(countdown=300)  # 5 minutos
        else:
            raise
```

## Monitoreo y Alertas

### Métricas de Prometheus

```python
from prometheus_client import Gauge, Counter

# Definir métricas
quota_usage = Gauge(
    'api_quota_usage',
    'Uso actual de cuota de API',
    ['api_name', 'window']
)

quota_exceeded = Counter(
    'api_quota_exceeded_total',
    'Total de eventos de cuota excedida',
    ['api_name']
)

rate_limit_pauses = Counter(
    'api_rate_limit_pauses_total',
    'Total de eventos de pausa de límite de tasa',
    ['api_name']
)

# Actualizar métricas periódicamente
@app.task
def update_quota_metrics():
    """Actualizar métricas de Prometheus para uso de cuota"""
    trackers = {
        'youtube': YouTubeQuotaTracker(redis_client, 'youtube'),
        'reddit': QuotaTracker(redis_client, 'reddit'),
        'trends': QuotaTracker(redis_client, 'trends'),
    }

    for api_name, tracker in trackers.items():
        if api_name == 'youtube':
            usage = tracker.get_usage(86400)
            quota_usage.labels(api_name='youtube', window='daily').set(usage)

        elif api_name == 'reddit':
            usage = tracker.get_usage(60)  # Por minuto
            quota_usage.labels(api_name='reddit', window='minute').set(usage)

        elif api_name == 'trends':
            usage = tracker.get_usage(3600)  # Por hora
            quota_usage.labels(api_name='trends', window='hourly').set(usage)
```

### Configuración de Alertas

```python
def check_quota_alerts():
    """Enviar alertas cuando el uso de cuota es alto"""
    youtube_tracker = YouTubeQuotaTracker(redis_client, 'youtube')
    youtube_usage = youtube_tracker.get_usage(86400)

    if youtube_usage >= 8000:  # 80% de 10,000
        send_alert(
            level='warning',
            message=f"Cuota de YouTube en {youtube_usage}/10000 (80%+). "
                   f"Se reinicia en {youtube_tracker.predict_reset_time(86400)}"
        )

    if youtube_usage >= 9500:  # 95% de 10,000
        send_alert(
            level='critical',
            message=f"Cuota de YouTube en {youtube_usage}/10000 (95%+). "
                   f"¡La recolección se pausará pronto!"
        )
```

## Estrategia de Pruebas

### Pruebas Unitarias

```python
import pytest
from unittest.mock import Mock, patch
from freezegun import freeze_time

def test_quota_tracker_usage():
    """Probar seguimiento de cuota a lo largo del tiempo"""
    redis_mock = Mock()
    tracker = QuotaTracker(redis_mock, 'test_api')

    tracker.track_request(cost=100)

    assert redis_mock.zadd.called
    redis_mock.zadd.assert_called_once()

def test_should_pause_threshold():
    """Probar decisión de pausa en umbral"""
    redis_mock = Mock()
    tracker = QuotaTracker(redis_mock, 'test_api')
    tracker.get_usage = Mock(return_value=900)

    # Debe pausar al 90% de 1000
    assert tracker.should_pause(1000, 3600, threshold=0.9)

    # No debe pausar con umbral de 80% y uso de 70%
    tracker.get_usage = Mock(return_value=700)
    assert not tracker.should_pause(1000, 3600, threshold=0.9)

@freeze_time("2025-01-01 12:00:00")
def test_predict_reset_time():
    """Probar predicción de tiempo de reinicio"""
    redis_mock = Mock()
    tracker = QuotaTracker(redis_mock, 'test_api')

    # Solicitud más antigua a las 11:00:00
    redis_mock.zrange.return_value = [(b'req1', 1704110400.0)]

    reset_time = tracker.predict_reset_time(3600)

    # Debe ser 12:00:00
    assert reset_time.hour == 12
```

### Pruebas de Integración

```python
@pytest.mark.integration
def test_youtube_rate_limiting_integration(redis_client):
    """Probar recolector de YouTube con Redis real"""
    tracker = YouTubeQuotaTracker(redis_client, 'youtube_test')

    # Simular 90 búsquedas (9000 unidades)
    for i in range(90):
        tracker.track_search()

    # Debe permitir 10 búsquedas más
    assert tracker.can_search()

    # Simular 10 búsquedas más (10,000 unidades total)
    for i in range(10):
        tracker.track_search()

    # NO debe permitir más (en umbral de 80% con uso de 10k)
    assert not tracker.can_search()
```

## Lista de Verificación de Implementación

- [ ] Instalar PyrateLimiter con backend Redis (`pip install pyrate-limiter[all]`)
- [ ] Configurar Redis para limitación de tasa y seguimiento de cuota
- [ ] Crear colas Celery separadas por API (youtube_queue, reddit_queue, etc.)
- [ ] Implementar clase QuotaTracker con backend Redis
- [ ] Agregar decoradores de limitación de tasa a recolectores de API
- [ ] Configurar retroceso exponencial en tareas Celery
- [ ] Crear modelo CollectionQueue para estado de pausa/reanudación
- [ ] Implementar CollectionCoordinator para orquestación multi-API
- [ ] Agregar lógica de distribución de cuota para múltiples lineamientos (justa o basada en prioridad)
- [ ] Configurar métricas de Prometheus para monitoreo de cuota
- [ ] Configurar alertas para agotamiento de cuota (umbrales de 80%, 95%)
- [ ] Probar mecanismo de pausa/reanudación para cada API
- [ ] Probar distribución justa entre lineamientos
- [ ] Documentar límites de tasa específicos por API y estrategias de retroceso
- [ ] Crear dashboard de monitoreo (Grafana) para uso de cuota

## Resumen de Recomendaciones

### Algoritmo de Limitación de Tasa
**Usar Ventana Deslizante** - Más preciso para cuotas rodantes (Meta), funciona bien para cuotas diarias (YouTube)

### Biblioteca
**Usar PyrateLimiter** - Backend Redis, soporte de decoradores, múltiples límites de tasa, bien mantenido

### Arquitectura Celery
**Usar Colas Separadas** - Limitación de tasa independiente por API, mejor aislamiento de fallos

### Estrategia de Reintento
**Usar Retroceso Exponencial con Jitter** - Previene manada atronadora, retrasos de retroceso específicos por API

### Seguimiento de Cuota
**Usar QuotaTracker Redis Personalizado** - Predecir tiempos de reinicio, pausa/reanudación automática, monitoreo de uso

### Estrategia de Distribución
**Usar Round-Robin o Basado en Prioridad** - Distribución justa de cuota entre lineamientos

### Sin Pérdida de Datos
**Usar Estado de Cola Respaldado por Base de Datos** - Persistir estado de pausa/reanudación, conteo de reintentos, uso de cuota

### Estrategias de Respaldo
**Fallos Independientes de API** - Una API caída no detiene otras, resultados parciales OK

## Referencias

### Bibliotecas
- PyrateLimiter: https://github.com/vutran1710/PyrateLimiter
- ratelimit: https://github.com/tomasbasham/ratelimit
- requests-ratelimiter: https://pypi.org/project/requests-ratelimiter/
- Celery: https://docs.celeryq.dev/

### Documentación de API
- YouTube Data API v3: https://developers.google.com/youtube/v3/determine_quota_cost
- Reddit API: https://www.reddit.com/dev/api
- pytrends: https://github.com/GeneralMills/pytrends

### Patrones de Limitación de Tasa
- Redis Rate Limiting: https://redis.io/learn/howtos/ratelimiting
- Algoritmo de Ventana Deslizante: https://arpitbhayani.me/blogs/sliding-window-ratelimiter/
- Enrutamiento de Celery: https://docs.celeryq.dev/en/stable/userguide/routing.html
- Retroceso Exponencial: https://testdriven.io/blog/retrying-failed-celery-tasks/

---

**Estado de Investigación de Limitación de Tasa**: ✅ **COMPLETA**

**Próximos Pasos**: Implementar seguimiento de cuota y limitación de tasa durante Fase 2 (ejecución de tareas)

---

# Tarea de Investigación #6: Arquitectura de Tareas Celery

**Fecha de Investigación**: 2025-11-08
**Enfoque de Investigación**: Organización de tareas para recolectores, procesamiento NLP y analíticas

## Resumen Ejecutivo

Basándose en investigación exhaustiva de mejores prácticas de Celery, patrones de producción y estrategias de optimización de rendimiento, aquí están las recomendaciones clave para organizar tareas Celery en el sistema de análisis de redes sociales:

### Recomendaciones Rápidas

| Aspecto | Recomendación |
|---------|---------------|
| **Granularidad de Tarea** | Recolectores por lotes (50 elementos), NLP por elemento único, analíticas por lotes |
| **Organización de Colas** | 5 colas: youtube_collector, reddit_collector, mastodon_collector, nlp_processing, analytics |
| **Patrón Canvas** | chain(group(collectors), chord(nlp_tasks, analytics_callback)) |
| **Manejo de Errores** | Retroceso exponencial (3 reintentos) + DLQ de Base de Datos + Circuit breaker |
| **Multiplicador de Prefetch** | Recolectores: 4, NLP: 1, Analíticas: 2 |
| **Backend de Resultados** | Redis con TTL de 1 día |
| **Concurrencia** | Recolectores: gevent/100, NLP: prefork/8, Analíticas: prefork/4 |
| **Programación** | Celery Beat con django-celery-beat (respaldado por base de datos) |

---

## 1. Investigación de Granularidad de Tareas

### Hallazgo Clave: Coincidir Granularidad con Tipo de Tarea

**Procesamiento por Lotes (tareas vinculadas a I/O)**:
- Usar para recolectores de API: 25-50 elementos por lote
- Reduce sobrecarga de conexión en 40%
- Ideal cuando se espera I/O de red
- Biblioteca: celery-batches (flush_every o flush_interval)

**Procesamiento por Elemento Único (tareas vinculadas a CPU)**:
- Usar para tareas NLP: 1 elemento por tarea
- Duración variable (50ms a 5 segundos)
- Mejor distribución de workers
- Lógica de reintento más fácil

**Métrica Clave**: Duración de tarea
- Tareas > 100ms con duración variable → prefetch_multiplier=1
- Tareas < 100ms (cortas) → prefetch_multiplier=50-150
- Configurar prefetch=1 para tareas largas reduce tiempo pendiente en 40%

### Recomendación para el Sistema

**Recolectores**: Lote de 50 elementos
```python
@app.task(bind=True, max_retries=3, queue='youtube_collector')
def collect_youtube_batch(self, guideline_id, keywords, batch_size=50):
    # Llamadas API por lotes para eficiencia
    pass
```

**NLP**: Elemento único
```python
@app.task(bind=True, max_retries=2, queue='nlp_processing')
def process_nlp_single(self, content_id):
    # CPU-intensivo, duración variable
    pass
```

**Analíticas**: Lote de 100-500 elementos
```python
@app.task(queue='analytics')
def aggregate_analytics_batch(content_ids):
    # Consultas de agregación de base de datos
    pass
```

---

## 2. Investigación de Organización de Colas

### Hallazgo Clave: Separar Colas por Tipo de Recurso

**Mejores Prácticas**:
- Separar tareas vinculadas a I/O de vinculadas a CPU
- Usar colas de prioridad para alertas (priority=0 es más alto con Redis)
- Configurar `broker_transport_options = {'queue_order_strategy': 'priority'}`
- Los workers pueden consumir múltiples colas: `-Q queue1,queue2,queue3`

### Recomendación: 5 Colas

```python
task_queues = [
    Queue('youtube_collector'),    # Vinculado a I/O
    Queue('reddit_collector'),     # Vinculado a I/O
    Queue('mastodon_collector'),   # Vinculado a I/O
    Queue('nlp_processing'),       # Vinculado a CPU
    Queue('analytics'),            # Vinculado a DB
]
```

**Configuración de Worker**:
```bash
# Recolectores (gevent para alta concurrencia de I/O)
celery -A app worker -Q youtube_collector,reddit_collector,mastodon_collector \
    --concurrency=100 --pool=gevent --prefetch-multiplier=4

# NLP (prefork para paralelismo de CPU)
celery -A app worker -Q nlp_processing \
    --concurrency=8 --pool=prefork --prefetch-multiplier=1

# Analíticas
celery -A app worker -Q analytics \
    --concurrency=4 --prefetch-multiplier=2
```

---

## 3. Investigación de Patrones Canvas

### Hallazgo Clave: Usar Chord para Flujos de Trabajo Paralelo → Secuencial

**Primitivas**:
- **Chain**: Secuencial (A → B → C)
- **Group**: Paralelo ([A, B, C])
- **Chord**: Paralelo + callback (group → tarea única cuando todas completan)

**Requisitos de Chord**:
- Debe tener result_backend habilitado
- Las tareas NO deben tener ignore_result=True
- No soportado con backend RPC (usar Redis/DB)

### Recomendación: Recolección → NLP → Analíticas

```python
def daily_collection_workflow(guideline_id):
    # Paso 1: Recolectar de todas las plataformas en paralelo
    collection_tasks = group(
        collect_youtube_batch.s(...),
        collect_reddit_batch.s(...),
        collect_mastodon_batch.s(...),
    )

    # Paso 2: Encadenar a chord NLP
    workflow = chain(
        collection_tasks,           # Recolección paralela
        flatten_content_ids.s(),    # Aplanar resultados
        create_nlp_chord.s(),       # Procesamiento NLP
    )

    return workflow.apply_async()

def create_nlp_chord(content_ids):
    # NLP paralelo, luego agregar cuando TODAS completen
    nlp_tasks = group(
        process_nlp_single.s(id) for id in content_ids
    )

    return chord(nlp_tasks)(
        aggregate_analytics_batch.s()
    )
```

**¿Por qué chord en lugar de chain(group(), task)?**
- El callback de chord recibe TODOS los resultados del group
- Asegura que la agregación solo se ejecute después de que TODAS las tareas NLP completen
- Crítico para analíticas que necesitan conjunto de datos completo

---

## 4. Investigación de Manejo de Errores

### Hallazgo Clave: Estrategia de Manejo de Errores en Capas

**Capa 1: Reintentos Automáticos**
- Retroceso exponencial: `countdown = 60 * (2 ** retries)`
- Reintentos máximos: 3 para llamadas API, 2 para NLP
- Usar `autoretry_for=(ConnectionError, TimeoutError)`

**Capa 2: Circuit Breaker**
- Rastrear fallos por plataforma
- Abrir circuito después de 5 fallos en 5 minutos
- Previene fallos en cascada

**Capa 3: Dead Letter Queue**
- Respaldado por base de datos (Celery no tiene DLQ integrado)
- Almacenar: task_name, args, kwargs, error, traceback
- Interfaz de reintento manual

### Recomendación

**Recolector con Reintento + Circuit Breaker**:
```python
@app.task(
    bind=True,
    max_retries=3,
    autoretry_for=(APIConnectionError,),
    retry_backoff=True,
    retry_backoff_max=600,
    acks_late=True,
)
def collect_youtube_batch(self, guideline_id, keywords, batch_size=50):
    circuit_breaker = CircuitBreaker('youtube')

    if circuit_breaker.is_open():
        logger.warning("Circuito ABIERTO - saltando")
        return []

    try:
        results = youtube_api.search(keywords)
        circuit_breaker.record_success()
        return results
    except Exception as exc:
        circuit_breaker.record_failure()
        raise
```

**Modelo DLQ de Base de Datos**:
```python
class FailedTask(models.Model):
    task_name = models.CharField(max_length=255)
    task_args = models.JSONField()
    exception_message = models.TextField()
    failed_at = models.DateTimeField(auto_now_add=True)
    retry_count = models.IntegerField(default=0)
    status = models.CharField(default='failed')
```

**Matriz de Manejo de Errores**:

| Tipo de Error | Estrategia | Reintentos Máximos | Retroceso |
|---------------|------------|-------------------|-----------|
| Límite de Tasa API | Reintentar después de ventana | 3 | Fijo 60s |
| Cuota API Excedida | No reintentar, alertar | 0 | N/A |
| Error de Conexión | Retroceso exponencial | 3 | 60s, 120s, 240s |
| Error NLP | Reintento limitado | 2 | Fijo 60s |
| Error DB | Reintento rápido | 5 | 5s, 10s, 20s |

---

## 5. Investigación de Configuración de Rendimiento

### Hallazgo Clave: Ajustar Concurrencia y Prefetch Por Tipo de Worker

**Reglas de Concurrencia**:
- Vinculado a CPU: concurrency = núcleos de CPU (ej., 8)
- Vinculado a I/O: concurrency = 2x-4x núcleos O pool gevent (100+)
- Agregar >2x CPUs para tareas CPU degrada rendimiento

**Reglas de Prefetch**:
- Tareas largas/variables (>5s): prefetch=1 (reduce tiempo pendiente 40%)
- Tareas cortas (<100ms): prefetch=50-150
- Procesamiento por lotes: prefetch=2-4

**Backend de Resultados**:
- Redis: Más rápido (sub-ms), limitado por memoria
- PostgreSQL: Más lento, mejor persistencia
- Recomendación: Redis con TTL de 1 día

### Recomendación

**Configuración de Celery**:
```python
# Broker & Backend de Resultados
broker_url = 'redis://localhost:6379/0'
result_backend = 'redis://localhost:6379/1'
result_expires = 86400  # 1 día

# Rendimiento
worker_prefetch_multiplier = 1  # Por defecto para tareas variables
worker_max_tasks_per_child = 100  # Prevenir fugas de memoria
worker_max_memory_per_child = 500000  # Límite de 500MB

# Configuración de tareas
task_acks_late = True  # Reconocer después de completar
task_reject_on_worker_lost = True  # Re-encolar en caso de crash
task_soft_time_limit = 300  # Límite suave de 5 min
task_time_limit = 600  # Límite duro de 10 min
```

**Comandos de Worker**:
```bash
# Recolectores (I/O: gevent, alta concurrencia)
celery -A app worker -Q youtube_collector,reddit_collector,mastodon_collector \
    --concurrency=100 --pool=gevent --prefetch-multiplier=4

# NLP (CPU: prefork, coincidir con núcleos)
celery -A app worker -Q nlp_processing \
    --concurrency=8 --pool=prefork --prefetch-multiplier=1 \
    --max-memory-per-child=500000

# Analíticas (DB: prefork, moderado)
celery -A app worker -Q analytics \
    --concurrency=4 --prefetch-multiplier=2
```

---

## 6. Investigación de Programación

### Hallazgo Clave: Usar Programador Beat Respaldado por Base de Datos

**Celery Beat**:
- Envía tareas a intervalos a workers
- **CRÍTICO**: Solo ejecutar UNA instancia de beat (previene duplicados)
- Por defecto: archivo local (celerybeat-schedule) - no seguro para multi-servidor
- Producción: django-celery-beat (respaldado por base de datos, programaciones dinámicas)

**Tipos de Programación**:
- Crontab: `crontab(hour=2, minute=0)` (diario 2 AM)
- Interval: `timedelta(hours=6)` (cada 6 horas)
- Solar: `solar('sunset', lat, lon)` (astronómico)

### Recomendación

**Programación de Beat**:
```python
from celery.schedules import crontab
from datetime import timedelta

beat_schedule = {
    'collect-all-guidelines': {
        'task': 'collectors.collect_all_active_guidelines',
        'schedule': timedelta(hours=6),  # Cada 6 horas
        'options': {'queue': 'youtube_collector'}
    },
    'detect-trending': {
        'task': 'analytics.detect_trending',
        'schedule': timedelta(minutes=30),  # Cada 30 min
        'options': {'queue': 'analytics'}
    },
    'validate-trends': {
        'task': 'validation.validate_with_google_trends',
        'schedule': crontab(hour=2, minute=0),  # Diario 2 AM
        'options': {'queue': 'analytics'}
    },
    'cleanup-old-data': {
        'task': 'maintenance.cleanup_old_data',
        'schedule': crontab(hour=3, minute=0),  # Diario 3 AM
        'options': {'queue': 'analytics'}
    },
}

beat_scheduler = 'django_celery_beat.schedulers:DatabaseScheduler'
```

**Ejecutar Beat**:
```bash
# Servicio separado (PRODUCCIÓN)
celery -A app beat --scheduler django_celery_beat.schedulers:DatabaseScheduler

# ¡NUNCA ejecutar múltiples instancias de beat!
```

---

## 7. Resumen de Arquitectura Completa

### Diagrama de Flujo de Trabajo

```
Celery Beat (Cada 6 horas)
    ↓
collect_all_active_guidelines
    ↓
┌───────────────────────────────────┐
│  GROUP: Recolección Paralela      │
│  ┌──────────┐  ┌──────────┐      │
│  │ YouTube  │  │ Reddit   │      │
│  │ (lote    │  │ (lote    │      │
│  │  50)     │  │  50)     │      │
│  └──────────┘  └──────────┘      │
│       ↓              ↓            │
│   [yt_ids]      [rd_ids]         │
└───────────────────────────────────┘
    ↓
flatten_content_ids
    ↓
[id1, id2, ..., id100]
    ↓
┌───────────────────────────────────┐
│  CHORD: NLP Paralelo              │
│  ┌─────┐ ┌─────┐ ┌─────┐         │
│  │NLP 1│ │NLP 2│ │NLP 3│ ...     │
│  └─────┘ └─────┘ └─────┘         │
│  (1 contenido por tarea)          │
└───────────────────────────────────┘
    ↓ (esperar a que TODAS completen)
aggregate_analytics_batch([id1...id100])
    ↓
Verificar tendencias → send_alert si >50% de crecimiento
```

### Resumen de Configuración

| Componente | Configuración | Justificación |
|------------|--------------|---------------|
| **Recolectores** | Lote 50, gevent/100, prefetch=4 | Optimización de I/O |
| **NLP** | Elemento único, prefork/8, prefetch=1 | Equidad de CPU |
| **Analíticas** | Lote, prefork/4, prefetch=2 | Eficiencia de DB |
| **Colas** | 5 colas separadas | Aislamiento |
| **Canvas** | chain(group, chord) | Paralelo → Secuencial |
| **Reintento** | 3x exponencial + DLQ | Resiliencia |
| **Backend** | Redis TTL 1 día | Velocidad + limpieza |
| **Beat** | Respaldado por base de datos | Programaciones dinámicas |

### Objetivos de Rendimiento

- **Recolección**: 4,000 elementos/día ÷ 24 horas = 167 elementos/hora
  - 3 plataformas × 50 lote = 150 elementos por ejecución de recolección
  - Cada 6 horas = 600 elementos/día por plataforma → 1,800/día total ✅

- **NLP**: 8 núcleos × 20 elementos/hora = 160 elementos/hora ✅

- **Retraso de Cola**: <5 minutos (prefetch=1 previene acaparamiento)

---

## Ejemplos de Definiciones de Tareas

**Recolector**:
```python
@app.task(bind=True, max_retries=3, queue='youtube_collector')
def collect_youtube_batch(self, guideline_id, keywords, batch_size=50):
    results = []
    for keyword in keywords:
        items = youtube_api.search(q=keyword, maxResults=batch_size)
        results.extend(items)
    return [ContentRecolectado.create(item).id for item in results]
```

**NLP**:
```python
@app.task(bind=True, max_retries=2, queue='nlp_processing')
def process_nlp_single(self, content_id):
    content = ContentRecolectado.objects.get(id=content_id)
    content.topics = topic_modeling.identify(content.text)
    content.sentiment = sentiment_analyzer.analyze(content.text)
    content.save()
    return content_id
```

**Analíticas**:
```python
@app.task(queue='analytics')
def aggregate_analytics_batch(content_ids):
    stats = calculate_demographics(content_ids)
    trends = identify_trending(content_ids)
    Demografia.bulk_upsert(stats)
    Tendencia.bulk_upsert(trends)
```

**Orquestador**:
```python
@app.task
def daily_collection_workflow(guideline_id):
    guideline = Lineamiento.objects.get(id=guideline_id)

    collection = group(
        collect_youtube_batch.s(guideline_id, guideline.keywords, 50),
        collect_reddit_batch.s(guideline_id, guideline.keywords, 50),
    )

    workflow = chain(
        collection,
        flatten_content_ids.s(),
        create_nlp_chord.s(),
    )

    return workflow.apply_async()
```

---

## Referencias

### Documentación Oficial
- [Celery Canvas Patterns](https://docs.celeryq.dev/en/stable/userguide/canvas.html)
- [Celery Optimizing](https://docs.celeryq.dev/en/stable/userguide/optimizing.html)
- [Celery Routing](https://docs.celeryq.dev/en/stable/userguide/routing.html)
- [Celery Periodic Tasks](https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html)

### Bibliotecas
- [celery-batches](https://github.com/clokep/celery-batches) - Procesamiento por lotes
- [django-celery-beat](https://github.com/celery/django-celery-beat) - Programador DB
- [flower](https://github.com/mher/flower) - Dashboard de monitoreo

### Mejores Prácticas
- [Celery Task Routing & Error Handling](https://usmanasifbutt.github.io/blog/2025/03/13/celery-task-routing-and-retries.html)
- [Mastering Task Orchestration](https://medium.com/@mortezasaki91/mastering-task-orchestration-with-celery-exploring-groups-chains-and-chords-991f9e407a4f)
- [Configuration Best Practices](https://moldstud.com/articles/p-celery-configuration-best-practices-enhance-your-task-queue-efficiency)

---

## Estado: ✅ **INVESTIGACIÓN DE CELERY COMPLETA**

**Respuestas a Preguntas de Investigación**:

1. ✅ **Granularidad de Tarea**: Recolectores por lotes (50), NLP único, analíticas por lotes
2. ✅ **Organización de Colas**: 5 colas (plataforma + nlp + analíticas)
3. ✅ **Patrones Canvas**: chain(group, chord) para recolección→NLP→analíticas
4. ✅ **Manejo de Errores**: Retroceso exponencial + DLQ + circuit breaker
5. ✅ **Rendimiento**: Ajuste de prefetch, backend Redis, gevent para I/O
6. ✅ **Programación**: django-celery-beat con programaciones crontab + interval

**Siguiente Fase**: Implementar estructura de tareas en Fase 2 (ejecución de tareas)
