"""
Tareas Celery para mantenimiento
"""

import logging
from src.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task
def cleanup_old_data():
    """
    Tarea programada que limpia datos antiguos según política de retención.

    TODO: Implementar limpieza basada en settings.data_retention_days
    """
    logger.info("cleanup_old_data: placeholder - implementar cleanup")
    return {"status": "not_implemented"}
