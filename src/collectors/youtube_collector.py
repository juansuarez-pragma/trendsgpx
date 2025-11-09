"""
Collector para YouTube usando YouTube Data API v3
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.utils.config import settings
from src.utils.rate_limiter import rate_limiter_manager

logger = logging.getLogger(__name__)


class YouTubeCollector:
    """
    Recolecta contenido de YouTube usando YouTube Data API v3.

    Límites de API:
    - 10,000 unidades por día (configurable)
    - Búsqueda: 100 unidades por query
    - Video details: 1 unidad por video
    """

    def __init__(self, api_key: str | None = None):
        """
        Inicializa el collector de YouTube.

        Args:
            api_key: API key de YouTube. Si None, usa settings.youtube_api_key
        """
        self.api_key = api_key or settings.youtube_api_key

        if not self.api_key:
            logger.warning("YouTube API key no configurada")

        # Inicializar cliente de YouTube API
        self.youtube = None
        if self.api_key:
            try:
                self.youtube = build("youtube", "v3", developerKey=self.api_key)
                logger.info("Cliente YouTube API inicializado")
            except Exception as e:
                logger.error(f"Error al inicializar YouTube API: {e}")

        # Obtener rate limiter
        self.rate_limiter = rate_limiter_manager.get_limiter(
            name="youtube",
            max_requests=settings.youtube_rate_limit_requests,
            period_seconds=settings.youtube_rate_limit_period_seconds,
        )

    def search_videos(
        self,
        keywords: List[str],
        max_results: int = 50,
        published_after: datetime | None = None,
        region_code: str = "MX",
        language: str = "es",
    ) -> List[Dict[str, Any]]:
        """
        Busca videos en YouTube por keywords.

        Args:
            keywords: Lista de keywords a buscar
            max_results: Máximo de resultados (máx 50 por request)
            published_after: Fecha mínima de publicación
            region_code: Código de región (ej: MX, ES, AR)
            language: Código de idioma (ej: es, en)

        Returns:
            Lista de videos con metadata

        Raises:
            ValueError: Si no hay API key configurada
            HttpError: Si hay error en la API de YouTube
        """
        if not self.youtube:
            raise ValueError("YouTube API no inicializada. Configurar API key.")

        # Construir query de búsqueda
        query = " OR ".join(keywords)

        # Configurar parámetros de búsqueda
        search_params: Dict[str, Any] = {
            "q": query,
            "part": "snippet",
            "type": "video",
            "maxResults": min(max_results, 50),  # Máximo 50 por request
            "regionCode": region_code,
            "relevanceLanguage": language,
            "order": "date",  # Ordenar por fecha para obtener lo más reciente
        }

        # Agregar filtro de fecha si se especifica
        if published_after:
            # Formato RFC 3339
            search_params["publishedAfter"] = published_after.strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            )

        logger.info(
            f"Buscando videos en YouTube: query='{query}', "
            f"max_results={max_results}, region={region_code}"
        )

        # Adquirir token de rate limiter (esto consume ~100 unidades)
        self.rate_limiter.acquire()

        try:
            # Ejecutar búsqueda
            search_response = self.youtube.search().list(**search_params).execute()

            videos = []
            video_ids = []

            # Extraer IDs de videos
            for item in search_response.get("items", []):
                if item["id"]["kind"] == "youtube#video":
                    video_ids.append(item["id"]["videoId"])

            # Obtener detalles de videos (estadísticas, duración, etc.)
            if video_ids:
                videos = self._get_video_details(video_ids)

            logger.info(f"Videos encontrados: {len(videos)}")
            return videos

        except HttpError as e:
            logger.error(f"Error en YouTube API: {e}")
            raise

    def _get_video_details(self, video_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Obtiene detalles completos de videos por sus IDs.

        Args:
            video_ids: Lista de IDs de videos

        Returns:
            Lista de videos con detalles completos
        """
        if not video_ids:
            return []

        # YouTube API permite hasta 50 IDs por request
        videos = []

        for i in range(0, len(video_ids), 50):
            batch_ids = video_ids[i : i + 50]

            # Adquirir token de rate limiter (1 unidad por request)
            self.rate_limiter.acquire()

            try:
                video_response = (
                    self.youtube.videos()
                    .list(
                        part="snippet,statistics,contentDetails",
                        id=",".join(batch_ids),
                    )
                    .execute()
                )

                for item in video_response.get("items", []):
                    video = self._parse_video(item)
                    videos.append(video)

            except HttpError as e:
                logger.error(f"Error al obtener detalles de videos: {e}")
                # Continuar con el siguiente batch

        return videos

    def _parse_video(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parsea un video de la respuesta de YouTube API.

        Args:
            item: Item de la respuesta de YouTube API

        Returns:
            Video parseado con campos normalizados
        """
        snippet = item.get("snippet", {})
        statistics = item.get("statistics", {})
        content_details = item.get("contentDetails", {})

        return {
            "plataforma_id": item["id"],
            "titulo": snippet.get("title", ""),
            "descripcion": snippet.get("description", ""),
            "autor": snippet.get("channelTitle", ""),
            "autor_id": snippet.get("channelId", ""),
            "fecha_publicacion": snippet.get("publishedAt", ""),
            "url": f"https://www.youtube.com/watch?v={item['id']}",
            "metadata": {
                "view_count": int(statistics.get("viewCount", 0)),
                "like_count": int(statistics.get("likeCount", 0)),
                "comment_count": int(statistics.get("commentCount", 0)),
                "duration": content_details.get("duration", ""),
                "tags": snippet.get("tags", []),
                "category_id": snippet.get("categoryId", ""),
                "thumbnails": snippet.get("thumbnails", {}),
            },
        }

    def get_video_comments(
        self,
        video_id: str,
        max_results: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Obtiene comentarios de un video.

        Args:
            video_id: ID del video de YouTube
            max_results: Máximo de comentarios a obtener

        Returns:
            Lista de comentarios

        Note:
            Los comentarios pueden estar deshabilitados en algunos videos.
        """
        if not self.youtube:
            raise ValueError("YouTube API no inicializada")

        logger.info(f"Obteniendo comentarios del video: {video_id}")

        comments = []

        try:
            # Adquirir token de rate limiter
            self.rate_limiter.acquire()

            request = self.youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=min(max_results, 100),
                order="relevance",
                textFormat="plainText",
            )

            while request and len(comments) < max_results:
                response = request.execute()

                for item in response.get("items", []):
                    comment = item["snippet"]["topLevelComment"]["snippet"]
                    comments.append(
                        {
                            "comment_id": item["snippet"]["topLevelComment"]["id"],
                            "texto": comment.get("textDisplay", ""),
                            "autor": comment.get("authorDisplayName", ""),
                            "fecha_publicacion": comment.get("publishedAt", ""),
                            "like_count": comment.get("likeCount", 0),
                        }
                    )

                # Obtener siguiente página si existe
                request = self.youtube.commentThreads().list_next(request, response)

                if request:
                    # Adquirir token para siguiente página
                    self.rate_limiter.acquire()

        except HttpError as e:
            if e.resp.status == 403:
                logger.warning(f"Comentarios deshabilitados para video {video_id}")
            else:
                logger.error(f"Error al obtener comentarios: {e}")

        logger.info(f"Comentarios obtenidos: {len(comments)}")
        return comments

    def collect_for_lineamiento(
        self,
        keywords: List[str],
        hours_back: int = 24,
        max_results: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Recolecta videos para un lineamiento.

        Args:
            keywords: Keywords del lineamiento
            hours_back: Horas hacia atrás para buscar
            max_results: Máximo de resultados

        Returns:
            Lista de videos recolectados
        """
        # Calcular fecha de inicio
        published_after = datetime.utcnow() - timedelta(hours=hours_back)

        logger.info(
            f"Recolectando contenido YouTube: keywords={keywords}, "
            f"hours_back={hours_back}, max_results={max_results}"
        )

        try:
            videos = self.search_videos(
                keywords=keywords,
                max_results=max_results,
                published_after=published_after,
            )

            return videos

        except Exception as e:
            logger.error(f"Error al recolectar contenido de YouTube: {e}")
            return []
