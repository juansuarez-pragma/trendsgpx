"""
Endpoints REST para Lineamientos
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Annotated
import logging

from src.models.base import get_db
from src.api.auth import get_api_key
from src.schemas.lineamiento import (
    LineamientoCreate,
    LineamientoUpdate,
    LineamientoResponse,
    LineamientoListResponse,
)
from src.services.lineamiento_service import LineamientoService

logger = logging.getLogger(__name__)

# Crear router
router = APIRouter(
    prefix="/lineamientos",
    tags=["Lineamientos"],
    dependencies=[Depends(get_api_key)],  # Todos los endpoints requieren autenticación
)


@router.post(
    "/",
    response_model=LineamientoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear lineamiento",
    description="Crea un nuevo lineamiento de búsqueda con keywords y plataformas asociadas",
)
async def create_lineamiento(
    lineamiento_data: LineamientoCreate,
    db: Annotated[Session, Depends(get_db)],
) -> LineamientoResponse:
    """
    Crea un nuevo lineamiento.

    - **nombre**: Nombre único del lineamiento (ej: "Tecnología 2025")
    - **keywords**: Lista de keywords para buscar (ej: ["IA", "machine learning"])
    - **plataformas**: Plataformas donde buscar (youtube, reddit, mastodon)

    Returns:
        Lineamiento creado con su ID y metadatos
    """
    try:
        lineamiento = LineamientoService.create(db, lineamiento_data)
        logger.info(f"Lineamiento creado exitosamente: {lineamiento.id}")
        return LineamientoResponse.model_validate(lineamiento)

    except ValueError as e:
        logger.warning(f"Error de validación al crear lineamiento: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/",
    response_model=LineamientoListResponse,
    summary="Listar lineamientos",
    description="Obtiene lista paginada de lineamientos",
)
async def list_lineamientos(
    db: Annotated[Session, Depends(get_db)],
    skip: Annotated[int, Query(ge=0, description="Número de registros a saltar")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Número máximo de registros")] = 100,
    activo_only: Annotated[bool, Query(description="Solo lineamientos activos")] = False,
) -> LineamientoListResponse:
    """
    Lista lineamientos con paginación.

    - **skip**: Offset para paginación (default: 0)
    - **limit**: Máximo de resultados (default: 100, max: 100)
    - **activo_only**: Si true, solo retorna lineamientos activos

    Returns:
        Lista de lineamientos con total
    """
    lineamientos = LineamientoService.get_all(db, skip=skip, limit=limit, activo_only=activo_only)
    total = LineamientoService.count(db, activo_only=activo_only)

    logger.info(f"Listados {len(lineamientos)} lineamientos (total: {total})")

    return LineamientoListResponse(
        total=total,
        items=[LineamientoResponse.model_validate(l) for l in lineamientos],
    )


@router.get(
    "/{lineamiento_id}",
    response_model=LineamientoResponse,
    summary="Obtener lineamiento por ID",
    description="Obtiene un lineamiento específico por su UUID",
)
async def get_lineamiento(
    lineamiento_id: UUID,
    db: Annotated[Session, Depends(get_db)],
) -> LineamientoResponse:
    """
    Obtiene un lineamiento por ID.

    - **lineamiento_id**: UUID del lineamiento

    Returns:
        Lineamiento con todos sus datos
    """
    lineamiento = LineamientoService.get_by_id(db, lineamiento_id)

    if not lineamiento:
        logger.warning(f"Lineamiento no encontrado: {lineamiento_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lineamiento {lineamiento_id} no encontrado",
        )

    logger.info(f"Lineamiento obtenido: {lineamiento_id}")
    return LineamientoResponse.model_validate(lineamiento)


@router.put(
    "/{lineamiento_id}",
    response_model=LineamientoResponse,
    summary="Actualizar lineamiento",
    description="Actualiza un lineamiento existente (parcial o completo)",
)
async def update_lineamiento(
    lineamiento_id: UUID,
    lineamiento_data: LineamientoUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> LineamientoResponse:
    """
    Actualiza un lineamiento existente.

    Todos los campos son opcionales. Solo se actualizan los campos enviados.

    - **nombre**: Nuevo nombre (opcional)
    - **keywords**: Nueva lista de keywords (opcional)
    - **plataformas**: Nueva lista de plataformas (opcional)
    - **activo**: Nuevo estado activo/inactivo (opcional)

    Returns:
        Lineamiento actualizado
    """
    try:
        lineamiento = LineamientoService.update(db, lineamiento_id, lineamiento_data)

        if not lineamiento:
            logger.warning(f"Lineamiento no encontrado para actualizar: {lineamiento_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lineamiento {lineamiento_id} no encontrado",
            )

        logger.info(f"Lineamiento actualizado: {lineamiento_id}")
        return LineamientoResponse.model_validate(lineamiento)

    except ValueError as e:
        logger.warning(f"Error de validación al actualizar lineamiento: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    "/{lineamiento_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar lineamiento (soft delete)",
    description="Marca un lineamiento como inactivo (no lo elimina de la BD)",
)
async def delete_lineamiento(
    lineamiento_id: UUID,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    """
    Elimina un lineamiento (soft delete).

    Marca el lineamiento como inactivo pero no lo elimina de la base de datos.
    El contenido recolectado se mantiene.

    - **lineamiento_id**: UUID del lineamiento a eliminar

    Returns:
        204 No Content si se eliminó correctamente
    """
    deleted = LineamientoService.delete(db, lineamiento_id)

    if not deleted:
        logger.warning(f"Lineamiento no encontrado para eliminar: {lineamiento_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lineamiento {lineamiento_id} no encontrado",
        )

    logger.info(f"Lineamiento eliminado (soft delete): {lineamiento_id}")
    return None


@router.post(
    "/{lineamiento_id}/activate",
    response_model=LineamientoResponse,
    summary="Reactivar lineamiento",
    description="Reactiva un lineamiento previamente marcado como inactivo",
)
async def activate_lineamiento(
    lineamiento_id: UUID,
    db: Annotated[Session, Depends(get_db)],
) -> LineamientoResponse:
    """
    Reactiva un lineamiento inactivo.

    - **lineamiento_id**: UUID del lineamiento a reactivar

    Returns:
        Lineamiento reactivado
    """
    lineamiento = LineamientoService.activate(db, lineamiento_id)

    if not lineamiento:
        logger.warning(f"Lineamiento no encontrado para reactivar: {lineamiento_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lineamiento {lineamiento_id} no encontrado",
        )

    logger.info(f"Lineamiento reactivado: {lineamiento_id}")
    return LineamientoResponse.model_validate(lineamiento)


@router.delete(
    "/{lineamiento_id}/permanent",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar lineamiento permanentemente (PELIGRO)",
    description="Elimina permanentemente un lineamiento y todo su contenido (CASCADE)",
)
async def hard_delete_lineamiento(
    lineamiento_id: UUID,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    """
    Elimina PERMANENTEMENTE un lineamiento de la base de datos.

    ⚠️ ADVERTENCIA: Esta operación es IRREVERSIBLE.
    Se eliminará también todo el contenido recolectado asociado (CASCADE).

    - **lineamiento_id**: UUID del lineamiento a eliminar

    Returns:
        204 No Content si se eliminó correctamente
    """
    deleted = LineamientoService.hard_delete(db, lineamiento_id)

    if not deleted:
        logger.warning(f"Lineamiento no encontrado para hard delete: {lineamiento_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lineamiento {lineamiento_id} no encontrado",
        )

    logger.warning(f"Lineamiento HARD DELETED: {lineamiento_id}")
    return None
