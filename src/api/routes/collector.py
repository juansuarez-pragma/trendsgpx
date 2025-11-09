"""
Endpoints REST para disparar recolección de contenido
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Annotated
import logging

from src.models.base import get_db
from src.api.auth import get_api_key
from src.models.lineamiento import Lineamiento
from src.tasks.collector_tasks import (
    collect_all_platforms,
    collect_youtube,
    collect_reddit,
    collect_mastodon,
    collect_all_lineamientos,
)

logger = logging.getLogger(__name__)

# Crear router
router = APIRouter(
    prefix="/collect",
    tags=["Recolección"],
    dependencies=[Depends(get_api_key)],
)


@router.post(
    "/lineamiento/{lineamiento_id}",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Recolectar contenido para un lineamiento",
    description="Dispara tareas asíncronas para recolectar contenido en todas las plataformas del lineamiento",
)
async def collect_lineamiento(
    lineamiento_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    hours_back: int = 24,
) -> dict:
    """
    Dispara recolección de contenido para un lineamiento específico.

    - **lineamiento_id**: UUID del lineamiento
    - **hours_back**: Horas hacia atrás a buscar (default: 24)

    Returns:
        Task ID de Celery y estado
    """
    # Verificar que el lineamiento existe
    lineamiento = db.query(Lineamiento).filter(Lineamiento.id == lineamiento_id).first()

    if not lineamiento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lineamiento {lineamiento_id} no encontrado",
        )

    if not lineamiento.activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Lineamiento {lineamiento_id} está inactivo",
        )

    logger.info(f"Disparando recolección para lineamiento: {lineamiento_id}")

    # Disparar tarea de Celery
    task = collect_all_platforms.delay(
        lineamiento_id=str(lineamiento_id),
        keywords=lineamiento.keywords,
        plataformas=lineamiento.plataformas,
        hours_back=hours_back,
    )

    return {
        "task_id": task.id,
        "lineamiento_id": str(lineamiento_id),
        "lineamiento_nombre": lineamiento.nombre,
        "plataformas": lineamiento.plataformas,
        "hours_back": hours_back,
        "status": "accepted",
        "message": "Tarea de recolección iniciada en segundo plano",
    }


@router.post(
    "/lineamiento/{lineamiento_id}/platform/{platform}",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Recolectar contenido de una plataforma específica",
    description="Dispara tarea asíncrona para recolectar contenido de una plataforma específica",
)
async def collect_lineamiento_platform(
    lineamiento_id: UUID,
    platform: str,
    db: Annotated[Session, Depends(get_db)],
    hours_back: int = 24,
) -> dict:
    """
    Dispara recolección de contenido para una plataforma específica.

    - **lineamiento_id**: UUID del lineamiento
    - **platform**: Plataforma (youtube, reddit, mastodon)
    - **hours_back**: Horas hacia atrás a buscar

    Returns:
        Task ID de Celery y estado
    """
    # Validar plataforma
    valid_platforms = {"youtube", "reddit", "mastodon"}
    if platform not in valid_platforms:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Plataforma inválida. Válidas: {valid_platforms}",
        )

    # Verificar lineamiento
    lineamiento = db.query(Lineamiento).filter(Lineamiento.id == lineamiento_id).first()

    if not lineamiento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lineamiento {lineamiento_id} no encontrado",
        )

    if not lineamiento.activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Lineamiento {lineamiento_id} está inactivo",
        )

    # Verificar que la plataforma está en el lineamiento
    if platform not in lineamiento.plataformas:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Plataforma {platform} no configurada en lineamiento {lineamiento.nombre}",
        )

    logger.info(
        f"Disparando recolección {platform} para lineamiento: {lineamiento_id}"
    )

    # Seleccionar tarea según plataforma
    task_map = {
        "youtube": collect_youtube,
        "reddit": collect_reddit,
        "mastodon": collect_mastodon,
    }

    task_func = task_map[platform]

    # Disparar tarea
    task = task_func.delay(
        lineamiento_id=str(lineamiento_id),
        keywords=lineamiento.keywords,
        hours_back=hours_back,
    )

    return {
        "task_id": task.id,
        "lineamiento_id": str(lineamiento_id),
        "lineamiento_nombre": lineamiento.nombre,
        "platform": platform,
        "hours_back": hours_back,
        "status": "accepted",
        "message": f"Tarea de recolección {platform} iniciada en segundo plano",
    }


@router.post(
    "/all",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Recolectar contenido para todos los lineamientos activos",
    description="Dispara tareas para recolectar contenido de todos los lineamientos activos",
)
async def collect_all(
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    """
    Dispara recolección de contenido para TODOS los lineamientos activos.

    Esta operación puede ser costosa en términos de API quota.
    Usar con precaución.

    Returns:
        Task ID de Celery y estadísticas
    """
    # Contar lineamientos activos
    count = db.query(Lineamiento).filter(Lineamiento.activo == True).count()

    logger.info(f"Disparando recolección para {count} lineamientos activos")

    # Disparar tarea
    task = collect_all_lineamientos.delay()

    return {
        "task_id": task.id,
        "total_lineamientos": count,
        "status": "accepted",
        "message": f"Tarea de recolección masiva iniciada para {count} lineamientos",
    }


@router.get(
    "/task/{task_id}",
    summary="Consultar estado de tarea de recolección",
    description="Obtiene el estado de una tarea de recolección",
)
async def get_task_status(task_id: str) -> dict:
    """
    Consulta el estado de una tarea de Celery.

    - **task_id**: ID de la tarea de Celery

    Returns:
        Estado de la tarea
    """
    from celery.result import AsyncResult

    task = AsyncResult(task_id)

    response = {
        "task_id": task_id,
        "status": task.status,
        "ready": task.ready(),
    }

    if task.ready():
        if task.successful():
            response["result"] = task.result
        else:
            response["error"] = str(task.info)

    return response
