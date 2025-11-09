"""
Configuración de Celery para tareas asíncronas
"""

from celery import Celery
from celery.schedules import crontab
import logging

from src.utils.config import settings
from src.utils.logging import setup_logging

# Configurar logging
setup_logging(
    log_level=settings.log_level,
    log_format=settings.log_format,
    log_file=settings.log_file,
)

logger = logging.getLogger(__name__)

# Crear app de Celery
celery_app = Celery(
    "trendsgpx",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

# Configuración de Celery
celery_app.conf.update(
    # Serialización
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Resultados
    result_expires=3600,  # 1 hora
    result_backend_transport_options={"master_name": "mymaster"},
    # Tareas
    task_track_started=True,
    task_time_limit=3600,  # 1 hora timeout
    task_soft_time_limit=3000,  # 50 minutos soft timeout
    # Workers
    worker_prefetch_multiplier=1,  # Tomar 1 tarea a la vez
    worker_max_tasks_per_child=100,  # Reiniciar worker cada 100 tareas
    # Colas
    task_routes={
        "src.tasks.collector_tasks.collect_youtube": {"queue": "collectors"},
        "src.tasks.collector_tasks.collect_reddit": {"queue": "collectors"},
        "src.tasks.collector_tasks.collect_mastodon": {"queue": "collectors"},
        "src.tasks.collector_tasks.collect_all_platforms": {"queue": "collectors"},
        "src.tasks.nlp_tasks.*": {"queue": "nlp"},
        "src.tasks.analytics_tasks.*": {"queue": "analytics"},
    },
    # Beat schedule (tareas programadas)
    beat_schedule={
        # Recolectar contenido cada 30 minutos
        "collect-content-every-30min": {
            "task": "src.tasks.collector_tasks.collect_all_lineamientos",
            "schedule": crontab(minute="*/30"),
        },
        # Procesar NLP cada hora
        "process-nlp-hourly": {
            "task": "src.tasks.nlp_tasks.process_pending_content",
            "schedule": crontab(minute=0),
        },
        # Analizar tendencias cada hora
        "analyze-trends-hourly": {
            "task": "src.tasks.analytics_tasks.analyze_trends",
            "schedule": crontab(minute=15),
        },
        # Validar tendencias con Google Trends cada 6 horas
        "validate-trends-6hourly": {
            "task": "src.tasks.analytics_tasks.validate_trends",
            "schedule": crontab(minute=30, hour="*/6"),
        },
        # Limpiar datos antiguos diariamente
        "cleanup-old-data-daily": {
            "task": "src.tasks.maintenance_tasks.cleanup_old_data",
            "schedule": crontab(minute=0, hour=3),  # 3 AM
        },
    },
)

# Auto-descubrir tareas en módulos
celery_app.autodiscover_tasks(
    [
        "src.tasks.collector_tasks",
        "src.tasks.nlp_tasks",
        "src.tasks.analytics_tasks",
        "src.tasks.maintenance_tasks",
    ]
)

logger.info("Celery app configurada")


@celery_app.task(bind=True)
def debug_task(self):
    """Tarea de debug para verificar que Celery funciona"""
    logger.info(f"Request: {self.request!r}")
    return f"Task executed: {self.request.id}"
