"""
Schemas Pydantic para Tendencias
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any
from uuid import UUID
from datetime import datetime


class TendenciaBase(BaseModel):
    """Schema base para tendencias"""
    tema_nombre: str = Field(..., description="Nombre del tema")
    plataforma: str = Field(..., description="Plataforma de origen")
    ubicacion: str = Field(..., description="Ubicación geográfica")
    edad_rango: str = Field(..., description="Rango de edad")
    genero: str = Field(..., description="Género")
    volumen_menciones: int = Field(..., ge=0, description="Número de menciones")
    tasa_crecimiento: float = Field(..., description="Tasa de crecimiento")
    sentimiento_promedio: float = Field(..., ge=-1.0, le=1.0, description="Sentimiento promedio")
    es_tendencia: bool = Field(..., description="Si es tendencia activa")


class TendenciaResponse(TendenciaBase):
    """Schema de respuesta para una tendencia"""
    id: UUID = Field(..., description="ID de la tendencia")
    tema_id: UUID = Field(..., description="ID del tema")
    fecha_hora: datetime = Field(..., description="Fecha y hora de la tendencia")
    keywords: List[str] = Field(default=[], description="Keywords del tema")
    validada: bool | None = Field(None, description="Si fue validada con Google Trends")

    class Config:
        from_attributes = True


class TendenciaAgregada(BaseModel):
    """Schema para tendencias agregadas"""
    tema_nombre: str = Field(..., description="Nombre del tema")
    plataformas: List[str] = Field(..., description="Plataformas donde aparece")
    volumen_total: int = Field(..., ge=0, description="Volumen total de menciones")
    tasa_crecimiento_promedio: float = Field(..., description="Tasa de crecimiento promedio")
    sentimiento_promedio: float = Field(..., description="Sentimiento promedio")
    keywords: List[str] = Field(..., description="Keywords del tema")
    ubicaciones: List[str] = Field(..., description="Ubicaciones donde es tendencia")


class TendenciaJerarquica(BaseModel):
    """Schema para respuesta jerárquica de tendencias"""
    plataforma: str = Field(..., description="Plataforma")
    ubicaciones: List[Dict[str, Any]] = Field(..., description="Datos por ubicación")


class TendenciaListResponse(BaseModel):
    """Schema para lista de tendencias"""
    total: int = Field(..., ge=0, description="Total de tendencias")
    items: List[TendenciaResponse] = Field(..., description="Lista de tendencias")


class TendenciaJerarquicaResponse(BaseModel):
    """Schema para respuesta jerárquica"""
    total_tendencias: int = Field(..., ge=0)
    plataformas: List[TendenciaJerarquica] = Field(...)
