"""
Collector para Reddit usando PRAW (Python Reddit API Wrapper)
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging

import praw
from praw.exceptions import PRAWException

from src.utils.config import settings
from src.utils.rate_limiter import rate_limiter_manager

logger = logging.getLogger(__name__)


class RedditCollector:
    """
    Recolecta contenido de Reddit usando PRAW.

    Límites de API:
    - 60 requests por minuto (configurable)
    - PRAW maneja rate limiting automáticamente
    """

    def __init__(
        self,
        client_id: str | None = None,
        client_secret: str | None = None,
        user_agent: str | None = None,
    ):
        """
        Inicializa el collector de Reddit.

        Args:
            client_id: Client ID de Reddit. Si None, usa settings
            client_secret: Client Secret de Reddit. Si None, usa settings
            user_agent: User Agent. Si None, usa settings
        """
        self.client_id = client_id or settings.reddit_client_id
        self.client_secret = client_secret or settings.reddit_client_secret
        self.user_agent = user_agent or settings.reddit_user_agent

        # Inicializar cliente PRAW
        self.reddit = None
        if self.client_id and self.client_secret:
            try:
                self.reddit = praw.Reddit(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    user_agent=self.user_agent,
                )
                # Verificar autenticación
                self.reddit.user.me()
                logger.info(f"Cliente Reddit inicializado: {self.user_agent}")
            except PRAWException as e:
                logger.error(f"Error al inicializar Reddit API: {e}")
        else:
            logger.warning("Credenciales de Reddit no configuradas")

        # Obtener rate limiter
        self.rate_limiter = rate_limiter_manager.get_limiter(
            name="reddit",
            max_requests=settings.reddit_rate_limit_requests,
            period_seconds=settings.reddit_rate_limit_period_seconds,
        )

    def search_posts(
        self,
        keywords: List[str],
        subreddits: List[str] | None = None,
        time_filter: str = "day",
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Busca posts en Reddit por keywords.

        Args:
            keywords: Lista de keywords a buscar
            subreddits: Lista de subreddits específicos. Si None, busca en todos
            time_filter: Filtro de tiempo (hour, day, week, month, year, all)
            limit: Máximo de resultados

        Returns:
            Lista de posts con metadata

        Raises:
            ValueError: Si Reddit API no está inicializada
        """
        if not self.reddit:
            raise ValueError("Reddit API no inicializada. Configurar credenciales.")

        # Construir query de búsqueda
        query = " OR ".join(keywords)

        # Determinar subreddits a buscar
        if subreddits:
            subreddit_str = "+".join(subreddits)
            subreddit = self.reddit.subreddit(subreddit_str)
        else:
            # Buscar en todos los subreddits
            subreddit = self.reddit.subreddit("all")

        logger.info(
            f"Buscando posts en Reddit: query='{query}', "
            f"subreddits={subreddits or 'all'}, time_filter={time_filter}, limit={limit}"
        )

        posts = []

        try:
            # Adquirir token de rate limiter
            self.rate_limiter.acquire()

            # Buscar posts
            search_results = subreddit.search(
                query=query,
                time_filter=time_filter,
                sort="new",
                limit=limit,
            )

            for submission in search_results:
                post = self._parse_post(submission)
                posts.append(post)

                # Adquirir token para cada post procesado
                # (puede haber requests adicionales automáticos)
                if len(posts) % 10 == 0:
                    self.rate_limiter.acquire()

            logger.info(f"Posts encontrados: {len(posts)}")

        except PRAWException as e:
            logger.error(f"Error al buscar en Reddit: {e}")
            raise

        return posts

    def get_hot_posts(
        self,
        subreddits: List[str],
        limit: int = 25,
    ) -> List[Dict[str, Any]]:
        """
        Obtiene posts "hot" (trending) de subreddits específicos.

        Args:
            subreddits: Lista de subreddits
            limit: Máximo de posts por subreddit

        Returns:
            Lista de posts hot
        """
        if not self.reddit:
            raise ValueError("Reddit API no inicializada")

        logger.info(f"Obteniendo posts hot de: {subreddits}")

        all_posts = []

        for subreddit_name in subreddits:
            try:
                # Adquirir token de rate limiter
                self.rate_limiter.acquire()

                subreddit = self.reddit.subreddit(subreddit_name)

                for submission in subreddit.hot(limit=limit):
                    post = self._parse_post(submission)
                    all_posts.append(post)

            except PRAWException as e:
                logger.error(f"Error al obtener posts de r/{subreddit_name}: {e}")
                continue

        logger.info(f"Total posts hot obtenidos: {len(all_posts)}")
        return all_posts

    def _parse_post(self, submission: praw.models.Submission) -> Dict[str, Any]:
        """
        Parsea un post de Reddit.

        Args:
            submission: Submission de PRAW

        Returns:
            Post parseado con campos normalizados
        """
        return {
            "plataforma_id": submission.id,
            "titulo": submission.title,
            "descripcion": submission.selftext or "",
            "autor": str(submission.author) if submission.author else "[deleted]",
            "autor_id": submission.author.id if submission.author else None,
            "fecha_publicacion": datetime.fromtimestamp(
                submission.created_utc
            ).isoformat(),
            "url": f"https://www.reddit.com{submission.permalink}",
            "metadata": {
                "subreddit": submission.subreddit.display_name,
                "score": submission.score,
                "upvote_ratio": submission.upvote_ratio,
                "num_comments": submission.num_comments,
                "is_self": submission.is_self,
                "link_flair_text": submission.link_flair_text,
                "over_18": submission.over_18,
                "spoiler": submission.spoiler,
                "stickied": submission.stickied,
            },
        }

    def get_post_comments(
        self,
        post_id: str,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Obtiene comentarios de un post.

        Args:
            post_id: ID del post de Reddit
            limit: Máximo de comentarios a obtener

        Returns:
            Lista de comentarios
        """
        if not self.reddit:
            raise ValueError("Reddit API no inicializada")

        logger.info(f"Obteniendo comentarios del post: {post_id}")

        comments = []

        try:
            # Adquirir token de rate limiter
            self.rate_limiter.acquire()

            submission = self.reddit.submission(id=post_id)

            # Expandir todos los "MoreComments"
            submission.comments.replace_more(limit=0)

            for comment in submission.comments.list()[:limit]:
                if isinstance(comment, praw.models.Comment):
                    comments.append(
                        {
                            "comment_id": comment.id,
                            "texto": comment.body,
                            "autor": str(comment.author) if comment.author else "[deleted]",
                            "fecha_publicacion": datetime.fromtimestamp(
                                comment.created_utc
                            ).isoformat(),
                            "score": comment.score,
                        }
                    )

        except PRAWException as e:
            logger.error(f"Error al obtener comentarios: {e}")

        logger.info(f"Comentarios obtenidos: {len(comments)}")
        return comments

    def collect_for_lineamiento(
        self,
        keywords: List[str],
        subreddits: List[str] | None = None,
        hours_back: int = 24,
        max_results: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Recolecta posts para un lineamiento.

        Args:
            keywords: Keywords del lineamiento
            subreddits: Subreddits específicos a buscar
            hours_back: Horas hacia atrás (usado para determinar time_filter)
            max_results: Máximo de resultados

        Returns:
            Lista de posts recolectados
        """
        # Determinar time_filter basado en hours_back
        if hours_back <= 1:
            time_filter = "hour"
        elif hours_back <= 24:
            time_filter = "day"
        elif hours_back <= 168:  # 7 días
            time_filter = "week"
        else:
            time_filter = "month"

        logger.info(
            f"Recolectando contenido Reddit: keywords={keywords}, "
            f"subreddits={subreddits}, time_filter={time_filter}, max_results={max_results}"
        )

        # Subreddits recomendados en español si no se especifican
        if not subreddits:
            subreddits = [
                "es",  # r/es - España
                "mexico",  # r/mexico
                "argentina",  # r/argentina
                "chile",  # r/chile
                "colombia",  # r/colombia
                "AskReddit",  # General (multiidioma)
            ]

        try:
            posts = self.search_posts(
                keywords=keywords,
                subreddits=subreddits,
                time_filter=time_filter,
                limit=max_results,
            )

            return posts

        except Exception as e:
            logger.error(f"Error al recolectar contenido de Reddit: {e}")
            return []
