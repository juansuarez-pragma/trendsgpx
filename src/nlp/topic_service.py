"""
Servicio de Topic Modeling con BERTopic
"""

from typing import List, Dict, Any, Tuple
import logging

try:
    from bertopic import BERTopic
    from sentence_transformers import SentenceTransformer
except ImportError:
    BERTopic = None
    SentenceTransformer = None

from src.utils.config import settings

logger = logging.getLogger(__name__)


class TopicService:
    """
    Servicio para topic modeling con BERTopic.

    Usa embeddings de RoBERTuito para español.
    """

    def __init__(self):
        """Inicializa el servicio de topics"""
        self.model: BERTopic | None = None
        self.embedding_model = None

    def _create_model(self) -> BERTopic:
        """
        Crea un modelo BERTopic configurado para español.

        Returns:
            Modelo BERTopic inicializado
        """
        if BERTopic is None or SentenceTransformer is None:
            raise ImportError(
                "BERTopic y sentence-transformers deben estar instalados"
            )

        logger.info("Creando modelo BERTopic para español")

        # Usar RoBERTuito para embeddings en español
        # Alternativa: "hiiamsid/sentence_similarity_spanish_es"
        try:
            embedding_model = SentenceTransformer(
                "PlanTL-GOB-ES/roberta-base-bne"
            )
        except Exception as e:
            logger.warning(f"Error cargando RoBERTuito: {e}")
            # Fallback a modelo multilingüe
            embedding_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

        # Configurar BERTopic
        nr_topics = settings.bertopic_nr_topics
        if nr_topics != "auto":
            nr_topics = int(nr_topics)

        topic_model = BERTopic(
            embedding_model=embedding_model,
            language="spanish",
            min_topic_size=settings.bertopic_min_topic_size,
            nr_topics=nr_topics,
            verbose=True,
        )

        logger.info("Modelo BERTopic creado")
        return topic_model

    def fit_transform(
        self, documentos: List[str]
    ) -> Tuple[List[int], List[float]]:
        """
        Entrena el modelo y asigna topics a documentos.

        Args:
            documentos: Lista de textos

        Returns:
            Tupla de (topics, probabilities)
        """
        if not documentos:
            logger.warning("Lista de documentos vacía")
            return [], []

        logger.info(f"Entrenando BERTopic con {len(documentos)} documentos")

        # Crear modelo
        self.model = self._create_model()

        # Entrenar y transformar
        topics, probs = self.model.fit_transform(documentos)

        logger.info(
            f"BERTopic entrenado. Topics únicos: {len(set(topics))}"
        )

        return topics.tolist(), probs.tolist()

    def transform(self, documentos: List[str]) -> Tuple[List[int], List[float]]:
        """
        Asigna topics a nuevos documentos usando modelo entrenado.

        Args:
            documentos: Lista de textos

        Returns:
            Tupla de (topics, probabilities)
        """
        if self.model is None:
            raise ValueError("Modelo no entrenado. Llamar fit_transform primero.")

        if not documentos:
            return [], []

        topics, probs = self.model.transform(documentos)

        return topics.tolist(), probs.tolist()

    def get_topic_info(self, topic_id: int | None = None) -> List[Dict[str, Any]]:
        """
        Obtiene información sobre topics.

        Args:
            topic_id: ID del topic específico. Si None, retorna todos

        Returns:
            Lista de dicts con info de topics
        """
        if self.model is None:
            raise ValueError("Modelo no entrenado")

        if topic_id is not None:
            # Topic específico
            topic_words = self.model.get_topic(topic_id)
            if topic_words:
                return [
                    {
                        "topic_id": topic_id,
                        "keywords": [word for word, _ in topic_words[:10]],
                        "scores": [score for _, score in topic_words[:10]],
                    }
                ]
            return []

        # Todos los topics
        topic_info = self.model.get_topic_info()

        topics = []
        for _, row in topic_info.iterrows():
            topic_id = row["Topic"]
            if topic_id == -1:  # Outliers
                continue

            topic_words = self.model.get_topic(topic_id)
            if topic_words:
                topics.append(
                    {
                        "topic_id": topic_id,
                        "count": row.get("Count", 0),
                        "keywords": [word for word, _ in topic_words[:10]],
                        "name": row.get("Name", f"Topic {topic_id}"),
                    }
                )

        return topics

    def get_topic_name(self, topic_id: int) -> str:
        """
        Genera un nombre descriptivo para un topic.

        Args:
            topic_id: ID del topic

        Returns:
            Nombre del topic
        """
        if self.model is None:
            return f"Topic {topic_id}"

        topic_words = self.model.get_topic(topic_id)

        if not topic_words:
            return f"Topic {topic_id}"

        # Usar las 3 palabras más importantes
        top_words = [word for word, _ in topic_words[:3]]
        return ", ".join(top_words)

    def identify_topics_batch(
        self, documentos: List[str], min_docs: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Identifica topics en un batch de documentos.

        Args:
            documentos: Lista de textos
            min_docs: Mínimo de documentos para formar un topic

        Returns:
            Lista de topics identificados con metadata
        """
        if len(documentos) < min_docs:
            logger.warning(
                f"Muy pocos documentos ({len(documentos)}) para topic modeling"
            )
            return []

        try:
            # Entrenar modelo
            topics, probs = self.fit_transform(documentos)

            # Obtener info de topics
            topic_info = self.get_topic_info()

            # Enriquecer con estadísticas
            for topic in topic_info:
                topic_id = topic["topic_id"]

                # Contar documentos en este topic
                doc_count = sum(1 for t in topics if t == topic_id)
                topic["doc_count"] = doc_count

                # Probabilidad promedio
                topic_probs = [
                    probs[i] for i, t in enumerate(topics) if t == topic_id
                ]
                topic["avg_probability"] = (
                    sum(topic_probs) / len(topic_probs) if topic_probs else 0.0
                )

            # Filtrar topics con muy pocos documentos
            topic_info = [t for t in topic_info if t.get("doc_count", 0) >= min_docs]

            # Ordenar por número de documentos
            topic_info.sort(key=lambda x: x.get("doc_count", 0), reverse=True)

            logger.info(f"Topics identificados: {len(topic_info)}")

            return topic_info

        except Exception as e:
            logger.error(f"Error en topic modeling: {e}", exc_info=True)
            return []


# Instancia global
topic_service = TopicService()
