"""
Tareas Celery para recolección de contenido
"""

from typing import List, Dict, Any
from uuid import UUID
from datetime import datetime
import logging

from celery import group, chord
from sqlalchemy.orm import Session

from src.celery_app import celery_app
from src.models.base import SessionLocal
from src.models.lineamiento import Lineamiento
from src.models.contenido import ContenidoRecolectado
from src.collectors.youtube_collector import YouTubeCollector
from src.collectors.reddit_collector import RedditCollector
from src.collectors.mastodon_collector import MastodonCollector

logger = logging.getLogger(__name__)


def get_db() -> Session:
    """Helper para obtener sesión de base de datos"""
    return SessionLocal()


@celery_app.task(bind=True, max_retries=3)
def collect_youtube(
    self,
    lineamiento_id: str,
    keywords: List[str],
    hours_back: int = 24,
    max_results: int = 50,
) -> Dict[str, Any]:
    """
    Tarea Celery para recolectar contenido de YouTube.

    Args:
        lineamiento_id: UUID del lineamiento
        keywords: Lista de keywords a buscar
        hours_back: Horas hacia atrás
        max_results: Máximo de resultados

    Returns:
        Diccionario con estadísticas de recolección
    """
    try:
        logger.info(
            f"Iniciando recolección YouTube: lineamiento={lineamiento_id}, "
            f"keywords={keywords}"
        )

        collector = YouTubeCollector()
        videos = collector.collect_for_lineamiento(
            keywords=keywords,
            hours_back=hours_back,
            max_results=max_results,
        )

        # Guardar en base de datos
        db = get_db()
        saved_count = 0

        try:
            for video in videos:
                # Verificar si ya existe
                existing = (
                    db.query(ContenidoRecolectado)
                    .filter(
                        ContenidoRecolectado.plataforma == "youtube",
                        ContenidoRecolectado.plataforma_id == video["plataforma_id"],
                    )
                    .first()
                )

                if not existing:
                    contenido = ContenidoRecolectado(
                        lineamiento_id=UUID(lineamiento_id),
                        plataforma="youtube",
                        plataforma_id=video["plataforma_id"],
                        contenido_texto=f"{video['titulo']} {video['descripcion']}",
                        autor=video["autor"],
                        fecha_publicacion=datetime.fromisoformat(
                            video["fecha_publicacion"].replace("Z", "+00:00")
                        ),
                        url=video["url"],
                        metadata=video["metadata"],
                        nlp_procesado=False,
                    )
                    db.add(contenido)
                    saved_count += 1

            db.commit()

            logger.info(
                f"Recolección YouTube completada: {len(videos)} encontrados, "
                f"{saved_count} nuevos guardados"
            )

            return {
                "platform": "youtube",
                "lineamiento_id": lineamiento_id,
                "total_found": len(videos),
                "new_saved": saved_count,
                "status": "success",
            }

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error en recolección YouTube: {e}", exc_info=True)
        # Reintentar con backoff exponencial
        raise self.retry(exc=e, countdown=60 * (2**self.request.retries))


@celery_app.task(bind=True, max_retries=3)
def collect_reddit(
    self,
    lineamiento_id: str,
    keywords: List[str],
    hours_back: int = 24,
    max_results: int = 100,
    subreddits: List[str] | None = None,
) -> Dict[str, Any]:
    """
    Tarea Celery para recolectar contenido de Reddit.

    Args:
        lineamiento_id: UUID del lineamiento
        keywords: Lista de keywords a buscar
        hours_back: Horas hacia atrás
        max_results: Máximo de resultados
        subreddits: Subreddits específicos (opcional)

    Returns:
        Diccionario con estadísticas de recolección
    """
    try:
        logger.info(
            f"Iniciando recolección Reddit: lineamiento={lineamiento_id}, "
            f"keywords={keywords}, subreddits={subreddits}"
        )

        collector = RedditCollector()
        posts = collector.collect_for_lineamiento(
            keywords=keywords,
            subreddits=subreddits,
            hours_back=hours_back,
            max_results=max_results,
        )

        # Guardar en base de datos
        db = get_db()
        saved_count = 0

        try:
            for post in posts:
                # Verificar si ya existe
                existing = (
                    db.query(ContenidoRecolectado)
                    .filter(
                        ContenidoRecolectado.plataforma == "reddit",
                        ContenidoRecolectado.plataforma_id == post["plataforma_id"],
                    )
                    .first()
                )

                if not existing:
                    contenido = ContenidoRecolectado(
                        lineamiento_id=UUID(lineamiento_id),
                        plataforma="reddit",
                        plataforma_id=post["plataforma_id"],
                        contenido_texto=f"{post['titulo']} {post['descripcion']}",
                        autor=post["autor"],
                        fecha_publicacion=datetime.fromisoformat(
                            post["fecha_publicacion"]
                        ),
                        url=post["url"],
                        metadata=post["metadata"],
                        nlp_procesado=False,
                    )
                    db.add(contenido)
                    saved_count += 1

            db.commit()

            logger.info(
                f"Recolección Reddit completada: {len(posts)} encontrados, "
                f"{saved_count} nuevos guardados"
            )

            return {
                "platform": "reddit",
                "lineamiento_id": lineamiento_id,
                "total_found": len(posts),
                "new_saved": saved_count,
                "status": "success",
            }

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error en recolección Reddit: {e}", exc_info=True)
        raise self.retry(exc=e, countdown=60 * (2**self.request.retries))


@celery_app.task(bind=True, max_retries=3)
def collect_mastodon(
    self,
    lineamiento_id: str,
    keywords: List[str],
    hours_back: int = 24,
    max_results: int = 40,
) -> Dict[str, Any]:
    """
    Tarea Celery para recolectar contenido de Mastodon.

    Args:
        lineamiento_id: UUID del lineamiento
        keywords: Lista de keywords a buscar
        hours_back: Horas hacia atrás
        max_results: Máximo de resultados

    Returns:
        Diccionario con estadísticas de recolección
    """
    try:
        logger.info(
            f"Iniciando recolección Mastodon: lineamiento={lineamiento_id}, "
            f"keywords={keywords}"
        )

        collector = MastodonCollector()
        toots = collector.collect_for_lineamiento(
            keywords=keywords,
            hours_back=hours_back,
            max_results=max_results,
        )

        # Guardar en base de datos
        db = get_db()
        saved_count = 0

        try:
            for toot in toots:
                # Verificar si ya existe
                existing = (
                    db.query(ContenidoRecolectado)
                    .filter(
                        ContenidoRecolectado.plataforma == "mastodon",
                        ContenidoRecolectado.plataforma_id == toot["plataforma_id"],
                    )
                    .first()
                )

                if not existing:
                    # Mastodon puede tener fecha en diferentes formatos
                    try:
                        fecha_pub = datetime.fromisoformat(
                            toot["fecha_publicacion"].replace("Z", "+00:00")
                        )
                    except Exception:
                        fecha_pub = datetime.utcnow()

                    contenido = ContenidoRecolectado(
                        lineamiento_id=UUID(lineamiento_id),
                        plataforma="mastodon",
                        plataforma_id=toot["plataforma_id"],
                        contenido_texto=toot["descripcion"],
                        autor=toot["autor"],
                        fecha_publicacion=fecha_pub,
                        url=toot["url"],
                        metadata=toot["metadata"],
                        nlp_procesado=False,
                    )
                    db.add(contenido)
                    saved_count += 1

            db.commit()

            logger.info(
                f"Recolección Mastodon completada: {len(toots)} encontrados, "
                f"{saved_count} nuevos guardados"
            )

            return {
                "platform": "mastodon",
                "lineamiento_id": lineamiento_id,
                "total_found": len(toots),
                "new_saved": saved_count,
                "status": "success",
            }

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error en recolección Mastodon: {e}", exc_info=True)
        raise self.retry(exc=e, countdown=60 * (2**self.request.retries))


@celery_app.task
def collect_all_platforms(
    lineamiento_id: str,
    keywords: List[str],
    plataformas: List[str],
    hours_back: int = 24,
) -> Dict[str, Any]:
    """
    Tarea que coordina la recolección en todas las plataformas especificadas.

    Args:
        lineamiento_id: UUID del lineamiento
        keywords: Lista de keywords
        plataformas: Plataformas a recolectar
        hours_back: Horas hacia atrás

    Returns:
        Diccionario con estadísticas combinadas
    """
    logger.info(
        f"Iniciando recolección multi-plataforma: lineamiento={lineamiento_id}, "
        f"plataformas={plataformas}"
    )

    # Crear tasks para cada plataforma
    tasks = []

    if "youtube" in plataformas:
        tasks.append(
            collect_youtube.s(
                lineamiento_id=lineamiento_id,
                keywords=keywords,
                hours_back=hours_back,
                max_results=50,
            )
        )

    if "reddit" in plataformas:
        tasks.append(
            collect_reddit.s(
                lineamiento_id=lineamiento_id,
                keywords=keywords,
                hours_back=hours_back,
                max_results=100,
            )
        )

    if "mastodon" in plataformas:
        tasks.append(
            collect_mastodon.s(
                lineamiento_id=lineamiento_id,
                keywords=keywords,
                hours_back=hours_back,
                max_results=40,
            )
        )

    # Ejecutar en paralelo usando group
    if tasks:
        job = group(tasks)
        results = job.apply_async()
        results.get()  # Esperar a que terminen todas

        logger.info(f"Recolección multi-plataforma completada: lineamiento={lineamiento_id}")

        return {
            "lineamiento_id": lineamiento_id,
            "platforms": plataformas,
            "status": "success",
        }

    return {
        "lineamiento_id": lineamiento_id,
        "platforms": [],
        "status": "no_platforms",
    }


@celery_app.task
def collect_all_lineamientos() -> Dict[str, Any]:
    """
    Tarea programada que recolecta contenido para todos los lineamientos activos.

    Returns:
        Estadísticas de recolección
    """
    logger.info("Iniciando recolección para todos los lineamientos activos")

    db = get_db()

    try:
        # Obtener lineamientos activos
        lineamientos = db.query(Lineamiento).filter(Lineamiento.activo == True).all()

        logger.info(f"Lineamientos activos encontrados: {len(lineamientos)}")

        # Crear tareas para cada lineamiento
        tasks = []

        for lineamiento in lineamientos:
            task = collect_all_platforms.s(
                lineamiento_id=str(lineamiento.id),
                keywords=lineamiento.keywords,
                plataformas=lineamiento.plataformas,
                hours_back=24,
            )
            tasks.append(task)

        # Ejecutar en paralelo
        if tasks:
            job = group(tasks)
            results = job.apply_async()
            results.get(timeout=3600)  # Timeout de 1 hora

        logger.info(f"Recolección completada para {len(lineamientos)} lineamientos")

        return {
            "total_lineamientos": len(lineamientos),
            "status": "success",
        }

    finally:
        db.close()
