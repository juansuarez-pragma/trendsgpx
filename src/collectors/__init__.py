"""
Colectores de contenido para diferentes plataformas sociales
"""

from src.collectors.youtube_collector import YouTubeCollector
from src.collectors.reddit_collector import RedditCollector
from src.collectors.mastodon_collector import MastodonCollector

__all__ = [
    "YouTubeCollector",
    "RedditCollector",
    "MastodonCollector",
]
