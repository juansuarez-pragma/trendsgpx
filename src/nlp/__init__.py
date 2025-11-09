"""
Servicios de procesamiento NLP
"""

from src.nlp.spacy_service import SpacyService
from src.nlp.sentiment_service import SentimentService
from src.nlp.topic_service import TopicService

__all__ = [
    "SpacyService",
    "SentimentService",
    "TopicService",
]
