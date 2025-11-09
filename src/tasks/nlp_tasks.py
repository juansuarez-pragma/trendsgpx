"""
Tareas Celery para procesamiento NLP
"""

from typing import Dict, Any, List
from uuid import UUID
import logging

from sqlalchemy.orm import Session

from src.celery_app import celery_app
from src.models.base import SessionLocal
from src.models.contenido import ContenidoRecolectado
from src.models.tema import TemaIdentificado
from src.models.demografia import Demografia
from src.nlp.spacy_service import spacy_service
from src.nlp.sentiment_service import sentiment_service
from src.nlp.topic_service import topic_service

logger = logging.getLogger(__name__)


def get_db() -> Session:
    """Helper para obtener sesión de base de datos"""
    return SessionLocal()


@celery_app.task(bind=True, max_retries=3)
def process_content_nlp(self, contenido_id: str) -> Dict[str, Any]:
    """
    Procesa un contenido con NLP (NER, sentiment, keywords).

    Args:
        contenido_id: UUID del contenido

    Returns:
        Resultado del procesamiento
    """
    db = get_db()

    try:
        # Obtener contenido
        contenido = (
            db.query(ContenidoRecolectado)
            .filter(ContenidoRecolectado.id == UUID(contenido_id))
            .first()
        )

        if not contenido:
            logger.warning(f"Contenido no encontrado: {contenido_id}")
            return {"status": "not_found"}

        if contenido.nlp_procesado:
            logger.info(f"Contenido ya procesado: {contenido_id}")
            return {"status": "already_processed"}

        logger.info(f"Procesando NLP para contenido: {contenido_id}")

        texto = contenido.contenido_texto

        # Procesar con spaCy
        nlp_result = spacy_service.process_text(texto)

        # Análisis de sentimiento
        sentiment_result = sentiment_service.analyze(texto)

        # Extraer ubicación del texto o metadata
        ubicacion = None
        if contenido.metadata:
            # Reddit tiene subreddit
            if contenido.plataforma == "reddit":
                ubicacion = contenido.metadata.get("subreddit")
            # YouTube puede tener región en metadata
            elif contenido.plataforma == "youtube":
                ubicacion = None  # YouTube no provee ubicación fácilmente

        # Si no hay ubicación en metadata, intentar extraer del texto
        if not ubicacion:
            ubicacion = spacy_service.extract_location_from_text(texto)

        # Crear tema identificado (uno por contenido por ahora)
        # En producción, se haría topic modeling en batches
        tema = TemaIdentificado(
            contenido_id=contenido.id,
            lineamiento_id=contenido.lineamiento_id,
            tema_nombre=f"{contenido.plataforma}_{contenido.id}",  # Temporal
            keywords=nlp_result["keywords"],
            entidades_mencionadas=nlp_result["entities"],
            sentimiento=sentiment_result["sentimiento"],
            sentimiento_score=sentiment_result["score"],
        )

        db.add(tema)
        db.flush()  # Obtener ID del tema

        # Crear registro demográfico
        demografia = Demografia(
            tema_id=tema.id,
            plataforma=contenido.plataforma,
            ubicacion_pais=ubicacion if ubicacion else None,
            confianza_score=0.5,  # Score por defecto
        )

        db.add(demografia)

        # Marcar contenido como procesado
        contenido.nlp_procesado = True

        db.commit()

        logger.info(f"NLP procesado exitosamente: {contenido_id}")

        return {
            "status": "success",
            "contenido_id": contenido_id,
            "tema_id": str(tema.id),
            "sentimiento": sentiment_result["sentimiento"],
            "keywords": nlp_result["keywords"][:5],
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Error procesando NLP: {e}", exc_info=True)
        raise self.retry(exc=e, countdown=60 * (2**self.request.retries))

    finally:
        db.close()


@celery_app.task
def process_pending_content() -> Dict[str, Any]:
    """
    Tarea programada que procesa contenido pendiente de NLP.

    Returns:
        Estadísticas de procesamiento
    """
    logger.info("Iniciando procesamiento de contenido pendiente")

    db = get_db()

    try:
        # Obtener contenidos no procesados (límite para no saturar)
        contenidos = (
            db.query(ContenidoRecolectado)
            .filter(ContenidoRecolectado.nlp_procesado == False)
            .limit(100)
            .all()
        )

        logger.info(f"Contenidos pendientes encontrados: {len(contenidos)}")

        if not contenidos:
            return {"status": "no_pending", "processed": 0}

        # Procesar cada contenido
        processed = 0
        errors = 0

        for contenido in contenidos:
            try:
                # Disparar tarea individual
                process_content_nlp.delay(str(contenido.id))
                processed += 1
            except Exception as e:
                logger.error(f"Error al disparar tarea NLP: {e}")
                errors += 1

        logger.info(
            f"Procesamiento iniciado: {processed} tareas, {errors} errores"
        )

        return {
            "status": "success",
            "total_pending": len(contenidos),
            "tasks_dispatched": processed,
            "errors": errors,
        }

    finally:
        db.close()


@celery_app.task
def batch_topic_modeling(lineamiento_id: str | None = None) -> Dict[str, Any]:
    """
    Ejecuta topic modeling en batch sobre contenidos procesados.

    Args:
        lineamiento_id: Si se especifica, solo procesa ese lineamiento

    Returns:
        Topics identificados
    """
    logger.info(f"Iniciando batch topic modeling: lineamiento={lineamiento_id}")

    db = get_db()

    try:
        # Obtener contenidos procesados sin topic asignado
        query = db.query(ContenidoRecolectado).filter(
            ContenidoRecolectado.nlp_procesado == True
        )

        if lineamiento_id:
            query = query.filter(
                ContenidoRecolectado.lineamiento_id == UUID(lineamiento_id)
            )

        contenidos = query.limit(1000).all()

        if len(contenidos) < 10:
            logger.warning(f"Muy pocos contenidos para topic modeling: {len(contenidos)}")
            return {"status": "insufficient_data", "count": len(contenidos)}

        logger.info(f"Ejecutando topic modeling con {len(contenidos)} documentos")

        # Preparar documentos
        documentos = [c.contenido_texto for c in contenidos]

        # Ejecutar topic modeling
        topics_info = topic_service.identify_topics_batch(documentos, min_docs=5)

        logger.info(f"Topics identificados: {len(topics_info)}")

        # Actualizar temas en base de datos
        # Por ahora, solo retornar la información
        # En producción, se actualizarían los registros de TemaIdentificado

        return {
            "status": "success",
            "total_docs": len(contenidos),
            "topics_found": len(topics_info),
            "topics": topics_info[:10],  # Top 10
        }

    except Exception as e:
        logger.error(f"Error en batch topic modeling: {e}", exc_info=True)
        return {"status": "error", "error": str(e)}

    finally:
        db.close()
