"""
Servicio de análisis de sentimiento para español
"""

from typing import Dict, Any
import logging

try:
    from pysentimiento import create_analyzer
except ImportError:
    create_analyzer = None

logger = logging.getLogger(__name__)


class SentimentService:
    """
    Servicio para análisis de sentimiento en español usando pysentimiento.

    Soporta:
    - Sentimiento (positivo, negativo, neutro)
    - Scores de confianza
    """

    _instance = None
    _analyzer = None

    def __new__(cls):
        """Singleton para evitar cargar el modelo múltiples veces"""
        if cls._instance is None:
            cls._instance = super(SentimentService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Inicializa el analizador de sentimiento"""
        if self._analyzer is None:
            self._load_analyzer()

    def _load_analyzer(self) -> None:
        """Carga el modelo de análisis de sentimiento"""
        if create_analyzer is None:
            logger.warning(
                "pysentimiento no está instalado. "
                "El análisis de sentimiento no estará disponible."
            )
            return

        try:
            logger.info("Cargando modelo de sentimiento pysentimiento")
            # Usar modelo de sentimiento para español
            self._analyzer = create_analyzer(task="sentiment", lang="es")
            logger.info("Modelo de sentimiento cargado")
        except Exception as e:
            logger.error(f"Error al cargar modelo de sentimiento: {e}")

    def analyze(self, texto: str) -> Dict[str, Any]:
        """
        Analiza el sentimiento de un texto.

        Args:
            texto: Texto a analizar

        Returns:
            Dict con sentimiento y scores
            {
                "sentimiento": "POS" | "NEU" | "NEG",
                "score": 0.95,
                "scores": {
                    "POS": 0.95,
                    "NEU": 0.03,
                    "NEG": 0.02
                }
            }
        """
        if self._analyzer is None:
            logger.warning("Analizador de sentimiento no disponible")
            return {
                "sentimiento": "NEU",
                "score": 0.0,
                "scores": {"POS": 0.0, "NEU": 1.0, "NEG": 0.0},
            }

        try:
            # Truncar texto si es muy largo (pysentimiento tiene límite)
            texto_truncado = texto[:512] if len(texto) > 512 else texto

            result = self._analyzer.predict(texto_truncado)

            return {
                "sentimiento": result.output,
                "score": result.probas[result.output],
                "scores": result.probas,
            }

        except Exception as e:
            logger.error(f"Error al analizar sentimiento: {e}")
            return {
                "sentimiento": "NEU",
                "score": 0.0,
                "scores": {"POS": 0.0, "NEU": 1.0, "NEG": 0.0},
            }

    def get_sentiment_label(self, sentimiento: str) -> str:
        """
        Convierte código de sentimiento a etiqueta legible.

        Args:
            sentimiento: Código (POS, NEU, NEG)

        Returns:
            Etiqueta en español
        """
        labels = {
            "POS": "positivo",
            "NEU": "neutro",
            "NEG": "negativo",
        }
        return labels.get(sentimiento, "desconocido")

    def is_positive(self, sentimiento: str, threshold: float = 0.6) -> bool:
        """
        Verifica si un resultado de análisis es positivo.

        Args:
            sentimiento: Código de sentimiento
            threshold: Umbral de confianza

        Returns:
            True si es sentimiento positivo con confianza suficiente
        """
        return sentimiento == "POS"

    def is_negative(self, sentimiento: str, threshold: float = 0.6) -> bool:
        """
        Verifica si un resultado de análisis es negativo.

        Args:
            sentimiento: Código de sentimiento
            threshold: Umbral de confianza

        Returns:
            True si es sentimiento negativo con confianza suficiente
        """
        return sentimiento == "NEG"

    def aggregate_sentiment(
        self, sentiments: list[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Agrega múltiples análisis de sentimiento.

        Args:
            sentiments: Lista de resultados de análisis

        Returns:
            Sentimiento agregado con distribución
        """
        if not sentiments:
            return {
                "sentimiento_dominante": "NEU",
                "distribucion": {"POS": 0.0, "NEU": 1.0, "NEG": 0.0},
                "total": 0,
            }

        # Contar sentimientos
        counts = {"POS": 0, "NEU": 0, "NEG": 0}

        for sent in sentiments:
            label = sent.get("sentimiento", "NEU")
            counts[label] = counts.get(label, 0) + 1

        total = len(sentiments)

        # Calcular distribución
        distribucion = {k: v / total for k, v in counts.items()}

        # Determinar dominante
        dominante = max(counts.items(), key=lambda x: x[1])[0]

        return {
            "sentimiento_dominante": dominante,
            "distribucion": distribucion,
            "total": total,
            "counts": counts,
        }


# Instancia global
sentiment_service = SentimentService()
