"""
Servicio de procesamiento NLP con spaCy para español
"""

from typing import List, Dict, Any
import logging
import spacy
from spacy.language import Language

from src.utils.config import settings

logger = logging.getLogger(__name__)


class SpacyService:
    """
    Servicio para procesamiento NLP con spaCy.

    Funcionalidades:
    - Named Entity Recognition (NER)
    - Extracción de keywords
    - Análisis lingüístico básico
    """

    _instance = None
    _nlp: Language | None = None

    def __new__(cls):
        """Singleton para evitar cargar el modelo múltiples veces"""
        if cls._instance is None:
            cls._instance = super(SpacyService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Inicializa el modelo de spaCy si no está cargado"""
        if self._nlp is None:
            self._load_model()

    def _load_model(self) -> None:
        """Carga el modelo de spaCy configurado"""
        try:
            logger.info(f"Cargando modelo spaCy: {settings.spacy_model}")
            self._nlp = spacy.load(settings.spacy_model)
            logger.info(f"Modelo spaCy cargado: {settings.spacy_model}")
        except OSError:
            logger.error(
                f"Modelo spaCy '{settings.spacy_model}' no encontrado. "
                "Ejecutar: python -m spacy download es_core_news_md"
            )
            raise

    @property
    def nlp(self) -> Language:
        """Retorna el modelo de spaCy"""
        if self._nlp is None:
            self._load_model()
        return self._nlp

    def extract_entities(self, texto: str) -> Dict[str, List[str]]:
        """
        Extrae entidades nombradas del texto.

        Args:
            texto: Texto a procesar

        Returns:
            Dict con entidades por tipo (PER, LOC, ORG, MISC)
        """
        doc = self.nlp(texto)

        entities: Dict[str, List[str]] = {
            "PER": [],  # Personas
            "LOC": [],  # Ubicaciones
            "ORG": [],  # Organizaciones
            "MISC": [],  # Misceláneos
        }

        for ent in doc.ents:
            # Mapear tipos de spaCy a categorías simplificadas
            if ent.label_ in ["PER", "PERSON"]:
                entities["PER"].append(ent.text)
            elif ent.label_ in ["LOC", "GPE", "LOCATION"]:
                entities["LOC"].append(ent.text)
            elif ent.label_ in ["ORG", "ORGANIZATION"]:
                entities["ORG"].append(ent.text)
            else:
                entities["MISC"].append(ent.text)

        # Eliminar duplicados manteniendo orden
        for key in entities:
            seen = set()
            entities[key] = [
                x for x in entities[key] if not (x in seen or seen.add(x))
            ]

        return entities

    def extract_keywords(
        self, texto: str, max_keywords: int = 10
    ) -> List[str]:
        """
        Extrae keywords importantes del texto.

        Usa una heurística simple basada en:
        - Sustantivos y nombres propios
        - Excluye stopwords
        - Ordena por frecuencia

        Args:
            texto: Texto a procesar
            max_keywords: Máximo de keywords a retornar

        Returns:
            Lista de keywords ordenadas por importancia
        """
        doc = self.nlp(texto)

        # Filtrar tokens relevantes
        keywords_freq: Dict[str, int] = {}

        for token in doc:
            # Considerar solo sustantivos y nombres propios
            if token.pos_ in ["NOUN", "PROPN"]:
                # Excluir stopwords y tokens cortos
                if not token.is_stop and len(token.text) > 2:
                    lemma = token.lemma_.lower()
                    keywords_freq[lemma] = keywords_freq.get(lemma, 0) + 1

        # Ordenar por frecuencia
        sorted_keywords = sorted(
            keywords_freq.items(), key=lambda x: x[1], reverse=True
        )

        # Retornar top keywords
        return [kw for kw, _ in sorted_keywords[:max_keywords]]

    def process_text(self, texto: str) -> Dict[str, Any]:
        """
        Procesa un texto completo y extrae toda la información NLP.

        Args:
            texto: Texto a procesar

        Returns:
            Dict con entidades, keywords y estadísticas
        """
        doc = self.nlp(texto)

        # Extraer entidades
        entities = self.extract_entities(texto)

        # Extraer keywords
        keywords = self.extract_keywords(texto)

        # Estadísticas básicas
        stats = {
            "num_tokens": len(doc),
            "num_sentences": len(list(doc.sents)),
            "num_entities": sum(len(v) for v in entities.values()),
        }

        return {
            "entities": entities,
            "keywords": keywords,
            "stats": stats,
        }

    def extract_location_from_text(self, texto: str) -> str | None:
        """
        Extrae la ubicación principal mencionada en el texto.

        Args:
            texto: Texto a procesar

        Returns:
            Ubicación principal o None si no se encuentra
        """
        entities = self.extract_entities(texto)
        locations = entities.get("LOC", [])

        if locations:
            # Retornar la primera ubicación encontrada
            return locations[0]

        return None

    def is_spanish(self, texto: str, min_confidence: float = 0.7) -> bool:
        """
        Verifica si un texto está en español.

        Usa una heurística simple basada en palabras en español.

        Args:
            texto: Texto a verificar
            min_confidence: Confianza mínima (0.0 a 1.0)

        Returns:
            True si el texto parece estar en español
        """
        doc = self.nlp(texto)

        if len(doc) == 0:
            return False

        # Contar tokens que no son stopwords en español
        spanish_tokens = sum(1 for token in doc if token.is_alpha)

        if spanish_tokens == 0:
            return False

        # Calcular proporción de tokens reconocidos
        recognized = sum(1 for token in doc if not token.is_oov)
        confidence = recognized / spanish_tokens if spanish_tokens > 0 else 0

        return confidence >= min_confidence


# Instancia global
spacy_service = SpacyService()
