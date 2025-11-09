"""
Aplicación FastAPI principal
"""

from fastapi import FastAPI, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from src.utils.config import settings
from src.utils.logging import setup_logging
from src.api.auth import get_api_key
from src.api.routes import lineamientos, collector, tendencias

# Configurar logging al inicio
setup_logging(
    log_level=settings.log_level,
    log_format=settings.log_format,
    log_file=settings.log_file,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager para eventos de inicio y cierre de la aplicación.
    """
    # Startup
    logger.info("Iniciando aplicación TrendsGPX API")
    logger.info(f"Configuración: log_level={settings.log_level}, database={settings.database_url.split('@')[1] if '@' in settings.database_url else 'local'}")

    yield

    # Shutdown
    logger.info("Cerrando aplicación TrendsGPX API")


# Crear app FastAPI
app = FastAPI(
    title="TrendsGPX API",
    description="API REST para análisis de tendencias en redes sociales",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Routers ====================

# Incluir routers de endpoints
app.include_router(lineamientos.router)
app.include_router(collector.router)
app.include_router(tendencias.router)


# ==================== Endpoints ====================

@app.get(
    "/health",
    summary="Health check",
    description="Endpoint para verificar el estado de la API",
    status_code=status.HTTP_200_OK,
    tags=["System"],
)
async def health_check():
    """
    Health check endpoint para verificar que la API está funcionando.
    No requiere autenticación.

    Returns:
        Dict con status "healthy" y versión de la API
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "TrendsGPX API",
    }


@app.get(
    "/",
    summary="Root endpoint",
    description="Endpoint raíz con información básica de la API",
    tags=["System"],
)
async def root():
    """
    Root endpoint con información básica de la API.
    No requiere autenticación.

    Returns:
        Dict con mensaje de bienvenida y links a documentación
    """
    return {
        "message": "TrendsGPX API - Análisis de tendencias en redes sociales",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/health",
    }


@app.get(
    "/protected",
    summary="Protected endpoint (ejemplo)",
    description="Endpoint de ejemplo que requiere autenticación con API key",
    tags=["System"],
    dependencies=[Depends(get_api_key)],
)
async def protected_example():
    """
    Endpoint de ejemplo que requiere autenticación.

    Incluir header: X-API-Key: <tu-api-key>

    Returns:
        Dict con mensaje de éxito
    """
    return {
        "message": "Acceso autorizado con API key válida",
        "authenticated": True,
    }


# ==================== Error Handlers ====================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Handler global para excepciones no controladas.
    """
    logger.error(f"Error no controlado: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Error interno del servidor",
            "type": "internal_server_error",
        },
    )


# ==================== Startup Info ====================

if __name__ == "__main__":
    import uvicorn

    logger.info(f"Iniciando servidor en {settings.host}:{settings.port}")
    uvicorn.run(
        "src.api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower(),
    )
