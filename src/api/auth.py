"""
Middleware de autenticación por API key
"""

from fastapi import Header, HTTPException, status
from fastapi.security import APIKeyHeader
from typing import Annotated
import logging

from src.utils.config import settings

logger = logging.getLogger(__name__)

# Definir el esquema de seguridad para API key en header
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(
    x_api_key: Annotated[str | None, Header()] = None
) -> str:
    """
    Verifica que el header X-API-Key contenga una API key válida.

    Args:
        x_api_key: Valor del header X-API-Key

    Returns:
        La API key válida

    Raises:
        HTTPException: Si la API key no es válida o está ausente
    """
    # Verificar que el header existe
    if not x_api_key:
        logger.warning("Request sin API key en header X-API-Key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key requerida. Incluir header X-API-Key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # Verificar que coincide con la configurada
    if x_api_key != settings.api_key:
        logger.warning(f"API key inválida recibida: {x_api_key[:8]}...")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key inválida",
        )

    logger.debug("API key validada correctamente")
    return x_api_key


# Dependency para usar en endpoints
def get_api_key(
    api_key: Annotated[str | None, api_key_header] = None
) -> str:
    """
    Dependency para FastAPI que valida la API key.

    Uso:
        @app.get("/protected")
        def protected_endpoint(api_key: str = Depends(get_api_key)):
            ...

    Args:
        api_key: Valor del header X-API-Key (inyectado por FastAPI)

    Returns:
        La API key válida

    Raises:
        HTTPException: Si la API key no es válida o está ausente
    """
    if not api_key:
        logger.warning("Request sin API key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key requerida. Incluir header X-API-Key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    if api_key != settings.api_key:
        logger.warning(f"API key inválida: {api_key[:8]}...")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key inválida",
        )

    logger.debug("API key validada")
    return api_key
