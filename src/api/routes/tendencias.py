"""
Endpoints REST para consultar Tendencias
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import Annotated, List
from datetime import datetime, timedelta
import logging

from src.models.base import get_db
from src.api.auth import get_api_key
from src.models.tendencia import Tendencia
from src.models.tema import TemaIdentificado
from src.models.validacion import ValidacionTendencia
from src.schemas.tendencia import (
    TendenciaResponse,
    TendenciaListResponse,
    TendenciaAgregada,
    TendenciaJerarquica,
    TendenciaJerarquicaResponse,
)

logger = logging.getLogger(__name__)

# Crear router
router = APIRouter(
    prefix="/tendencias",
    tags=["Tendencias"],
    dependencies=[Depends(get_api_key)],
)


@router.get(
    "/",
    response_model=TendenciaListResponse,
    summary="Listar tendencias",
    description="Obtiene lista de tendencias activas con filtros",
)
async def list_tendencias(
    db: Annotated[Session, Depends(get_db)],
    plataforma: Annotated[str | None, Query(description="Filtrar por plataforma")] = None,
    ubicacion: Annotated[str | None, Query(description="Filtrar por ubicación")] = None,
    solo_activas: Annotated[bool, Query(description="Solo tendencias activas")] = True,
    hours_back: Annotated[int, Query(ge=1, le=168, description="Horas hacia atrás (max 7 días)")] = 24,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> TendenciaListResponse:
    """
    Lista tendencias con filtros opcionales.

    - **plataforma**: youtube, reddit, mastodon (opcional)
    - **ubicacion**: País o ciudad (opcional)
    - **solo_activas**: Si true, solo tendencias marcadas como activas
    - **hours_back**: Ventana de tiempo en horas
    - **skip**: Offset para paginación
    - **limit**: Máximo de resultados

    Returns:
        Lista de tendencias ordenadas por fecha descendente
    """
    cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)

    # Construir query
    query = db.query(Tendencia).filter(Tendencia.fecha_hora >= cutoff_time)

    if solo_activas:
        query = query.filter(Tendencia.es_tendencia == True)

    if plataforma:
        query = query.filter(Tendencia.plataforma == plataforma.lower())

    if ubicacion:
        query = query.filter(Tendencia.ubicacion.ilike(f"%{ubicacion}%"))

    # Ordenar por fecha descendente
    query = query.order_by(desc(Tendencia.fecha_hora))

    # Obtener total
    total = query.count()

    # Aplicar paginación
    tendencias = query.offset(skip).limit(limit).all()

    # Enriquecer con datos de tema y validación
    items = []
    for tendencia in tendencias:
        # Obtener tema
        tema = db.query(TemaIdentificado).filter(
            TemaIdentificado.id == tendencia.tema_id
        ).first()

        # Obtener validación
        validacion = db.query(ValidacionTendencia).filter(
            ValidacionTendencia.tendencia_id == tendencia.id
        ).first()

        item_data = {
            "id": tendencia.id,
            "tema_id": tendencia.tema_id,
            "tema_nombre": tema.tema_nombre if tema else "Desconocido",
            "plataforma": tendencia.plataforma,
            "ubicacion": tendencia.ubicacion,
            "edad_rango": tendencia.edad_rango,
            "genero": tendencia.genero,
            "volumen_menciones": tendencia.volumen_menciones,
            "tasa_crecimiento": tendencia.tasa_crecimiento,
            "sentimiento_promedio": tendencia.sentimiento_promedio,
            "es_tendencia": tendencia.es_tendencia,
            "fecha_hora": tendencia.fecha_hora,
            "keywords": tema.keywords if tema else [],
            "validada": validacion.validada if validacion else None,
        }

        items.append(TendenciaResponse(**item_data))

    logger.info(f"Tendencias listadas: {len(items)} de {total}")

    return TendenciaListResponse(total=total, items=items)


@router.get(
    "/agregadas",
    response_model=List[TendenciaAgregada],
    summary="Tendencias agregadas por tema",
    description="Obtiene tendencias agregando por tema across plataformas",
)
async def tendencias_agregadas(
    db: Annotated[Session, Depends(get_db)],
    hours_back: Annotated[int, Query(ge=1, le=168)] = 24,
    top_n: Annotated[int, Query(ge=1, le=50)] = 10,
) -> List[TendenciaAgregada]:
    """
    Lista las top N tendencias agregando datos de todas las plataformas.

    - **hours_back**: Ventana de tiempo en horas
    - **top_n**: Número de tendencias a retornar

    Returns:
        Lista de tendencias agregadas ordenadas por volumen
    """
    cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)

    # Obtener todas las tendencias activas
    tendencias = (
        db.query(Tendencia)
        .filter(
            and_(
                Tendencia.fecha_hora >= cutoff_time,
                Tendencia.es_tendencia == True,
            )
        )
        .all()
    )

    # Agrupar por tema
    temas_dict = {}

    for tendencia in tendencias:
        # Obtener tema
        tema = db.query(TemaIdentificado).filter(
            TemaIdentificado.id == tendencia.tema_id
        ).first()

        if not tema:
            continue

        tema_nombre = tema.tema_nombre

        if tema_nombre not in temas_dict:
            temas_dict[tema_nombre] = {
                "tema_nombre": tema_nombre,
                "plataformas": set(),
                "volumen_total": 0,
                "tasas_crecimiento": [],
                "sentimientos": [],
                "keywords": tema.keywords or [],
                "ubicaciones": set(),
            }

        temas_dict[tema_nombre]["plataformas"].add(tendencia.plataforma)
        temas_dict[tema_nombre]["volumen_total"] += tendencia.volumen_menciones
        temas_dict[tema_nombre]["tasas_crecimiento"].append(
            tendencia.tasa_crecimiento
        )
        temas_dict[tema_nombre]["sentimientos"].append(
            tendencia.sentimiento_promedio
        )
        temas_dict[tema_nombre]["ubicaciones"].add(tendencia.ubicacion)

    # Convertir a lista y calcular promedios
    result = []

    for tema_data in temas_dict.values():
        avg_crecimiento = (
            sum(tema_data["tasas_crecimiento"]) / len(tema_data["tasas_crecimiento"])
            if tema_data["tasas_crecimiento"]
            else 0.0
        )

        avg_sentimiento = (
            sum(tema_data["sentimientos"]) / len(tema_data["sentimientos"])
            if tema_data["sentimientos"]
            else 0.0
        )

        result.append(
            TendenciaAgregada(
                tema_nombre=tema_data["tema_nombre"],
                plataformas=list(tema_data["plataformas"]),
                volumen_total=tema_data["volumen_total"],
                tasa_crecimiento_promedio=avg_crecimiento,
                sentimiento_promedio=avg_sentimiento,
                keywords=tema_data["keywords"],
                ubicaciones=list(tema_data["ubicaciones"]),
            )
        )

    # Ordenar por volumen y tomar top N
    result.sort(key=lambda x: x.volumen_total, reverse=True)

    logger.info(f"Tendencias agregadas: {len(result[:top_n])}")

    return result[:top_n]


@router.get(
    "/jerarquicas",
    response_model=TendenciaJerarquicaResponse,
    summary="Tendencias en estructura jerárquica",
    description="Retorna tendencias en estructura jerárquica (Plataforma → Ubicación → Edad → Género)",
)
async def tendencias_jerarquicas(
    db: Annotated[Session, Depends(get_db)],
    hours_back: Annotated[int, Query(ge=1, le=168)] = 24,
) -> TendenciaJerarquicaResponse:
    """
    Retorna tendencias organizadas jerárquicamente.

    Estructura: Plataforma → Ubicación → Edad → Género

    - **hours_back**: Ventana de tiempo en horas

    Returns:
        Tendencias en estructura jerárquica
    """
    cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)

    tendencias = (
        db.query(Tendencia)
        .filter(
            and_(
                Tendencia.fecha_hora >= cutoff_time,
                Tendencia.es_tendencia == True,
            )
        )
        .all()
    )

    # Organizar jerárquicamente
    jerarquia = {}

    for tendencia in tendencias:
        plataforma = tendencia.plataforma
        ubicacion = tendencia.ubicacion
        edad = tendencia.edad_rango
        genero = tendencia.genero

        # Inicializar niveles
        if plataforma not in jerarquia:
            jerarquia[plataforma] = {}

        if ubicacion not in jerarquia[plataforma]:
            jerarquia[plataforma][ubicacion] = {}

        if edad not in jerarquia[plataforma][ubicacion]:
            jerarquia[plataforma][ubicacion][edad] = {}

        if genero not in jerarquia[plataforma][ubicacion][edad]:
            jerarquia[plataforma][ubicacion][edad][genero] = []

        # Obtener tema
        tema = db.query(TemaIdentificado).filter(
            TemaIdentificado.id == tendencia.tema_id
        ).first()

        jerarquia[plataforma][ubicacion][edad][genero].append(
            {
                "tema_nombre": tema.tema_nombre if tema else "Desconocido",
                "volumen": tendencia.volumen_menciones,
                "crecimiento": tendencia.tasa_crecimiento,
                "sentimiento": tendencia.sentimiento_promedio,
                "keywords": tema.keywords if tema else [],
            }
        )

    # Convertir a formato de respuesta
    plataformas = []

    for plat_nombre, ubicaciones_data in jerarquia.items():
        ubicaciones = []

        for ubic_nombre, edades_data in ubicaciones_data.items():
            edades = []

            for edad_nombre, generos_data in edades_data.items():
                generos = []

                for gen_nombre, temas_list in generos_data.items():
                    generos.append(
                        {
                            "genero": gen_nombre,
                            "temas": temas_list,
                        }
                    )

                edades.append(
                    {
                        "edad_rango": edad_nombre,
                        "generos": generos,
                    }
                )

            ubicaciones.append(
                {
                    "ubicacion": ubic_nombre,
                    "edades": edades,
                }
            )

        plataformas.append(
            TendenciaJerarquica(
                plataforma=plat_nombre,
                ubicaciones=ubicaciones,
            )
        )

    total = len(tendencias)

    logger.info(f"Tendencias jerárquicas: {total} tendencias, {len(plataformas)} plataformas")

    return TendenciaJerarquicaResponse(
        total_tendencias=total,
        plataformas=plataformas,
    )
