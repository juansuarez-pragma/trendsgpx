"""
Modelos de base de datos SQLAlchemy
"""

from src.models.lineamiento import Lineamiento
from src.models.contenido import ContenidoRecolectado
from src.models.tema import TemaIdentificado
from src.models.demografia import Demografia
from src.models.tendencia import Tendencia
from src.models.validacion import ValidacionTendencia

__all__ = [
    "Lineamiento",
    "ContenidoRecolectado",
    "TemaIdentificado",
    "Demografia",
    "Tendencia",
    "ValidacionTendencia",
]
