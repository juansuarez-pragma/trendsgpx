"""
Tareas Celery para análisis de tendencias
"""

from typing import Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
import logging

from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from src.celery_app import celery_app
from src.models.base import SessionLocal
from src.models.tema import TemaIdentificado
from src.models.demografia import Demografia
from src.models.tendencia import Tendencia
from src.models.validacion import ValidacionTendencia
from src.utils.config import settings

try:
    from pytrends.request import TrendReq
except ImportError:
    TrendReq = None

logger = logging.getLogger(__name__)


def get_db() -> Session:
    """Helper para obtener sesión de base de datos"""
    return SessionLocal()


@celery_app.task
def analyze_trends() -> Dict[str, Any]:
    """
    Tarea programada que analiza tendencias basándose en temas identificados.

    Calcula:
    - Volumen de menciones por tema
    - Crecimiento en las últimas horas
    - Marca como tendencia si cumple umbrales
    """
    logger.info("Iniciando análisis de tendencias")

    db = get_db()

    try:
        # Ventana de tiempo: última hora
        now = datetime.utcnow()
        hour_ago = now - timedelta(hours=1)

        # Agrupar temas por nombre y datos demográficos
        query = (
            db.query(
                TemaIdentificado.tema_nombre,
                Demografia.plataforma,
                Demografia.ubicacion_pais,
                Demografia.edad_rango,
                Demografia.genero,
                func.count(TemaIdentificado.id).label("volumen"),
                func.avg(TemaIdentificado.sentimiento_score).label("avg_sentiment"),
            )
            .join(Demografia, Demografia.tema_id == TemaIdentificado.id)
            .filter(TemaIdentificado.created_at >= hour_ago)
            .group_by(
                TemaIdentificado.tema_nombre,
                Demografia.plataforma,
                Demografia.ubicacion_pais,
                Demografia.edad_rango,
                Demografia.genero,
            )
        )

        resultados = query.all()

        logger.info(f"Segmentos encontrados: {len(resultados)}")

        tendencias_creadas = 0

        for row in resultados:
            tema_nombre = row.tema_nombre
            plataforma = row.plataforma
            ubicacion = row.ubicacion_pais or "Desconocido"
            edad_rango = row.edad_rango or "Desconocido"
            genero = row.genero or "Desconocido"
            volumen = row.volumen
            avg_sentiment = row.avg_sentiment or 0.0

            # Calcular crecimiento comparando con hora anterior
            two_hours_ago = hour_ago - timedelta(hours=1)

            volumen_anterior = (
                db.query(func.count(TemaIdentificado.id))
                .join(Demografia, Demografia.tema_id == TemaIdentificado.id)
                .filter(
                    and_(
                        TemaIdentificado.tema_nombre == tema_nombre,
                        TemaIdentificado.created_at >= two_hours_ago,
                        TemaIdentificado.created_at < hour_ago,
                        Demografia.plataforma == plataforma,
                    )
                )
                .scalar()
                or 0
            )

            # Calcular tasa de crecimiento
            if volumen_anterior > 0:
                tasa_crecimiento = (volumen - volumen_anterior) / volumen_anterior
            else:
                tasa_crecimiento = 1.0 if volumen > 0 else 0.0

            # Determinar si es tendencia
            es_tendencia = (
                volumen >= settings.trending_min_mentions
                and tasa_crecimiento >= settings.trending_growth_threshold
            )

            # Obtener un tema representativo (el primero)
            tema_id = (
                db.query(TemaIdentificado.id)
                .join(Demografia, Demografia.tema_id == TemaIdentificado.id)
                .filter(
                    and_(
                        TemaIdentificado.tema_nombre == tema_nombre,
                        Demografia.plataforma == plataforma,
                    )
                )
                .first()
            )

            if not tema_id:
                continue

            # Crear o actualizar registro de tendencia
            tendencia = Tendencia(
                tema_id=tema_id[0],
                fecha_hora=now,
                plataforma=plataforma,
                ubicacion=ubicacion,
                edad_rango=edad_rango,
                genero=genero,
                volumen_menciones=volumen,
                tasa_crecimiento=tasa_crecimiento,
                sentimiento_promedio=avg_sentiment,
                es_tendencia=es_tendencia,
            )

            db.add(tendencia)
            tendencias_creadas += 1

        db.commit()

        logger.info(f"Tendencias analizadas: {tendencias_creadas}")

        return {
            "status": "success",
            "total_segments": len(resultados),
            "trends_created": tendencias_creadas,
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Error analizando tendencias: {e}", exc_info=True)
        return {"status": "error", "error": str(e)}

    finally:
        db.close()


@celery_app.task
def validate_trends() -> Dict[str, Any]:
    """
    Tarea programada que valida tendencias con Google Trends.

    Obtiene datos de Google Trends para las tendencias detectadas
    y las marca como validadas o no validadas.
    """
    if TrendReq is None:
        logger.warning("pytrends no instalado, validación no disponible")
        return {"status": "pytrends_not_installed"}

    logger.info("Iniciando validación de tendencias con Google Trends")

    db = get_db()

    try:
        # Obtener tendencias recientes sin validar
        tendencias = (
            db.query(Tendencia)
            .outerjoin(ValidacionTendencia)
            .filter(
                and_(
                    Tendencia.es_tendencia == True,
                    ValidacionTendencia.id.is_(None),
                )
            )
            .limit(10)  # Limitar para no saturar API
            .all()
        )

        logger.info(f"Tendencias a validar: {len(tendencias)}")

        pytrends = TrendReq(hl="es", tz=360)

        validadas = 0

        for tendencia in tendencias:
            try:
                # Obtener tema
                tema = (
                    db.query(TemaIdentificado)
                    .filter(TemaIdentificado.id == tendencia.tema_id)
                    .first()
                )

                if not tema or not tema.keywords:
                    continue

                # Usar primeras keywords para consultar Google Trends
                keywords = tema.keywords[:3]  # Máximo 3 keywords

                # Consultar Google Trends
                pytrends.build_payload(
                    keywords,
                    cat=0,
                    timeframe="now 7-d",  # Últimos 7 días
                    geo="",  # Global, se puede especificar país
                )

                # Obtener interest over time
                interest_df = pytrends.interest_over_time()

                google_trends_data = {}
                validada = False

                if not interest_df.empty:
                    # Convertir a dict
                    google_trends_data = interest_df.to_dict("list")

                    # Verificar si hay interés significativo
                    for keyword in keywords:
                        if keyword in interest_df.columns:
                            avg_interest = interest_df[keyword].mean()
                            if avg_interest > 50:  # Umbral arbitrario
                                validada = True
                                break

                # Crear registro de validación
                validacion = ValidacionTendencia(
                    tendencia_id=tendencia.id,
                    google_trends_data=google_trends_data,
                    validada=validada,
                )

                db.add(validacion)
                validadas += 1

                # Pequeña pausa para no saturar API
                import time

                time.sleep(2)

            except Exception as e:
                logger.error(f"Error validando tendencia {tendencia.id}: {e}")
                continue

        db.commit()

        logger.info(f"Tendencias validadas: {validadas}")

        return {
            "status": "success",
            "total_validated": validadas,
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Error en validación de tendencias: {e}", exc_info=True)
        return {"status": "error", "error": str(e)}

    finally:
        db.close()
