"""
Collector para Mastodon usando Mastodon.py
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging

from mastodon import Mastodon
from mastodon.errors import MastodonError

from src.utils.config import settings
from src.utils.rate_limiter import rate_limiter_manager

logger = logging.getLogger(__name__)


class MastodonCollector:
    """
    Recolecta contenido de Mastodon usando Mastodon.py.

    Límites de API:
    - 300 requests por 5 minutos (configurable)
    - Varía por instancia
    """

    def __init__(
        self,
        access_token: str | None = None,
        instance_url: str | None = None,
    ):
        """
        Inicializa el collector de Mastodon.

        Args:
            access_token: Access token de Mastodon. Si None, usa settings
            instance_url: URL de la instancia. Si None, usa settings
        """
        self.access_token = access_token or settings.mastodon_access_token
        self.instance_url = instance_url or settings.mastodon_instance

        # Inicializar cliente Mastodon
        self.mastodon = None
        if self.access_token and self.instance_url:
            try:
                self.mastodon = Mastodon(
                    access_token=self.access_token,
                    api_base_url=self.instance_url,
                )
                # Verificar autenticación
                self.mastodon.account_verify_credentials()
                logger.info(f"Cliente Mastodon inicializado: {self.instance_url}")
            except MastodonError as e:
                logger.error(f"Error al inicializar Mastodon API: {e}")
        else:
            logger.warning("Credenciales de Mastodon no configuradas")

        # Obtener rate limiter
        self.rate_limiter = rate_limiter_manager.get_limiter(
            name="mastodon",
            max_requests=settings.mastodon_rate_limit_requests,
            period_seconds=settings.mastodon_rate_limit_period_seconds,
        )

    def search_toots(
        self,
        keywords: List[str],
        limit: int = 40,
    ) -> List[Dict[str, Any]]:
        """
        Busca toots (posts) en Mastodon por keywords.

        Args:
            keywords: Lista de keywords a buscar
            limit: Máximo de resultados (máx 40 por request en Mastodon)

        Returns:
            Lista de toots con metadata

        Raises:
            ValueError: Si Mastodon API no está inicializada
        """
        if not self.mastodon:
            raise ValueError("Mastodon API no inicializada. Configurar credenciales.")

        # Construir query de búsqueda
        # Mastodon soporta búsqueda con espacios, no necesita OR explícito
        query = " ".join(keywords)

        logger.info(f"Buscando toots en Mastodon: query='{query}', limit={limit}")

        toots = []

        try:
            # Adquirir token de rate limiter
            self.rate_limiter.acquire()

            # Buscar toots
            # type='statuses' para buscar solo posts/toots
            search_results = self.mastodon.search_v2(
                q=query,
                result_type="statuses",
                limit=min(limit, 40),  # Mastodon limita a 40
            )

            for status in search_results.get("statuses", []):
                toot = self._parse_toot(status)
                toots.append(toot)

            logger.info(f"Toots encontrados: {len(toots)}")

        except MastodonError as e:
            logger.error(f"Error al buscar en Mastodon: {e}")
            raise

        return toots

    def get_timeline_public(
        self,
        limit: int = 40,
        only_local: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Obtiene toots del timeline público.

        Args:
            limit: Máximo de toots
            only_local: Si True, solo toots de la instancia local

        Returns:
            Lista de toots del timeline público
        """
        if not self.mastodon:
            raise ValueError("Mastodon API no inicializada")

        logger.info(
            f"Obteniendo timeline público: limit={limit}, only_local={only_local}"
        )

        toots = []

        try:
            # Adquirir token de rate limiter
            self.rate_limiter.acquire()

            timeline = self.mastodon.timeline_public(
                limit=limit,
                only_local=only_local,
            )

            for status in timeline:
                toot = self._parse_toot(status)
                toots.append(toot)

            logger.info(f"Toots obtenidos del timeline: {len(toots)}")

        except MastodonError as e:
            logger.error(f"Error al obtener timeline público: {e}")
            raise

        return toots

    def get_trending_tags(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtiene hashtags trending en la instancia.

        Args:
            limit: Máximo de tags

        Returns:
            Lista de trending tags con estadísticas
        """
        if not self.mastodon:
            raise ValueError("Mastodon API no inicializada")

        logger.info(f"Obteniendo trending tags: limit={limit}")

        try:
            # Adquirir token de rate limiter
            self.rate_limiter.acquire()

            trending = self.mastodon.trending_tags(limit=limit)

            tags = []
            for tag in trending:
                tags.append(
                    {
                        "name": tag.get("name", ""),
                        "url": tag.get("url", ""),
                        "history": tag.get("history", []),
                    }
                )

            logger.info(f"Trending tags obtenidos: {len(tags)}")
            return tags

        except MastodonError as e:
            logger.error(f"Error al obtener trending tags: {e}")
            return []

    def _parse_toot(self, status: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parsea un toot de Mastodon.

        Args:
            status: Status de Mastodon API

        Returns:
            Toot parseado con campos normalizados
        """
        account = status.get("account", {})

        # Limpiar HTML del contenido
        import re

        content = status.get("content", "")
        # Remover tags HTML simples
        content_text = re.sub(r"<[^>]+>", "", content)

        return {
            "plataforma_id": status.get("id", ""),
            "titulo": "",  # Mastodon no tiene títulos separados
            "descripcion": content_text,
            "autor": account.get("username", ""),
            "autor_id": account.get("id", ""),
            "fecha_publicacion": status.get("created_at", "").isoformat()
            if status.get("created_at")
            else "",
            "url": status.get("url", ""),
            "metadata": {
                "account_display_name": account.get("display_name", ""),
                "account_followers": account.get("followers_count", 0),
                "favourites_count": status.get("favourites_count", 0),
                "reblogs_count": status.get("reblogs_count", 0),
                "replies_count": status.get("replies_count", 0),
                "language": status.get("language", ""),
                "tags": [tag.get("name", "") for tag in status.get("tags", [])],
                "mentions": [
                    mention.get("username", "")
                    for mention in status.get("mentions", [])
                ],
                "sensitive": status.get("sensitive", False),
                "visibility": status.get("visibility", "public"),
            },
        }

    def get_toot_context(self, toot_id: str) -> Dict[str, Any]:
        """
        Obtiene el contexto de un toot (respuestas y thread).

        Args:
            toot_id: ID del toot

        Returns:
            Contexto del toot con ancestros y descendientes
        """
        if not self.mastodon:
            raise ValueError("Mastodon API no inicializada")

        logger.info(f"Obteniendo contexto del toot: {toot_id}")

        try:
            # Adquirir token de rate limiter
            self.rate_limiter.acquire()

            context = self.mastodon.status_context(toot_id)

            return {
                "ancestors": [self._parse_toot(s) for s in context.get("ancestors", [])],
                "descendants": [
                    self._parse_toot(s) for s in context.get("descendants", [])
                ],
            }

        except MastodonError as e:
            logger.error(f"Error al obtener contexto: {e}")
            return {"ancestors": [], "descendants": []}

    def collect_for_lineamiento(
        self,
        keywords: List[str],
        hours_back: int = 24,
        max_results: int = 40,
    ) -> List[Dict[str, Any]]:
        """
        Recolecta toots para un lineamiento.

        Args:
            keywords: Keywords del lineamiento
            hours_back: Horas hacia atrás (no usado directamente en Mastodon)
            max_results: Máximo de resultados

        Returns:
            Lista de toots recolectados

        Note:
            Mastodon search no soporta filtro de fecha en todas las instancias,
            pero retorna resultados recientes por defecto.
        """
        logger.info(
            f"Recolectando contenido Mastodon: keywords={keywords}, "
            f"max_results={max_results}"
        )

        try:
            toots = self.search_toots(
                keywords=keywords,
                limit=max_results,
            )

            # Filtrar por fecha si es necesario
            cutoff_date = datetime.utcnow() - timedelta(hours=hours_back)

            filtered_toots = []
            for toot in toots:
                try:
                    # Parsear fecha de publicación
                    pub_date = datetime.fromisoformat(
                        toot["fecha_publicacion"].replace("Z", "+00:00")
                    )

                    if pub_date >= cutoff_date:
                        filtered_toots.append(toot)
                except Exception as e:
                    logger.warning(f"Error al filtrar toot por fecha: {e}")
                    # Incluir el toot si no se puede validar la fecha
                    filtered_toots.append(toot)

            logger.info(f"Toots después de filtro de fecha: {len(filtered_toots)}")
            return filtered_toots

        except Exception as e:
            logger.error(f"Error al recolectar contenido de Mastodon: {e}")
            return []
