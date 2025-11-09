"""
Configuración de la aplicación usando pydantic BaseSettings
"""

from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """
    Configuración de la aplicación cargada desde variables de entorno.
    Los valores por defecto se usan si no se encuentra la variable.
    """

    # Base de datos
    database_url: str = Field(
        default="postgresql://trendsgpx:password@localhost:5432/trendsgpx",
        description="URL de conexión a PostgreSQL con TimescaleDB",
    )
    sql_echo: bool = Field(
        default=False,
        description="Habilitar logging de queries SQL (solo desarrollo)",
    )

    # Redis
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="URL de conexión a Redis para Celery",
    )

    # Celery
    celery_broker_url: str = Field(
        default="redis://localhost:6379/0",
        description="URL del broker para Celery (Redis)",
    )
    celery_result_backend: str = Field(
        default="redis://localhost:6379/0",
        description="URL del backend de resultados para Celery",
    )

    # API Keys - Plataformas
    youtube_api_key: str = Field(
        default="",
        description="API key para YouTube Data API v3",
    )
    reddit_client_id: str = Field(
        default="",
        description="Client ID para Reddit API",
    )
    reddit_client_secret: str = Field(
        default="",
        description="Client Secret para Reddit API",
    )
    reddit_user_agent: str = Field(
        default="TrendsGPX/1.0",
        description="User Agent para Reddit API",
    )
    mastodon_instance: str = Field(
        default="https://mastodon.social",
        description="URL de la instancia de Mastodon",
    )
    mastodon_access_token: str = Field(
        default="",
        description="Access token para Mastodon API",
    )

    # Rate Limiting - YouTube
    youtube_rate_limit_requests: int = Field(
        default=10000,
        description="Límite de requests diarios para YouTube API",
    )
    youtube_rate_limit_period_seconds: int = Field(
        default=86400,
        description="Período de rate limiting para YouTube (86400 = 1 día)",
    )

    # Rate Limiting - Reddit
    reddit_rate_limit_requests: int = Field(
        default=60,
        description="Límite de requests para Reddit API",
    )
    reddit_rate_limit_period_seconds: int = Field(
        default=60,
        description="Período de rate limiting para Reddit (60 = 1 minuto)",
    )

    # Rate Limiting - Mastodon
    mastodon_rate_limit_requests: int = Field(
        default=300,
        description="Límite de requests para Mastodon API",
    )
    mastodon_rate_limit_period_seconds: int = Field(
        default=300,
        description="Período de rate limiting para Mastodon (300 = 5 minutos)",
    )

    # NLP Configuración
    spacy_model: str = Field(
        default="es_core_news_md",
        description="Modelo de spaCy para español",
    )
    bertopic_min_topic_size: int = Field(
        default=5,
        description="Tamaño mínimo de topic para BERTopic",
    )
    bertopic_nr_topics: str = Field(
        default="auto",
        description="Número de topics para BERTopic ('auto' o número)",
    )

    # Análisis de tendencias
    trending_growth_threshold: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Umbral de crecimiento para marcar como tendencia (50% = 0.5)",
    )
    trending_min_mentions: int = Field(
        default=10,
        ge=1,
        description="Mínimo de menciones para considerar tendencia",
    )

    # Retención de datos
    data_retention_days: int = Field(
        default=7,
        ge=1,
        description="Días de retención de datos en TimescaleDB",
    )

    # API Security
    api_key: str = Field(
        default="dev-api-key-change-in-production",
        description="API key estática para autenticación",
    )

    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Orígenes permitidos para CORS",
    )

    # Logging
    log_level: str = Field(
        default="INFO",
        description="Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )
    log_format: str = Field(
        default="structured",
        description="Formato de logs ('json' o 'structured')",
    )
    log_file: str | None = Field(
        default=None,
        description="Path del archivo de log (None = solo consola)",
    )

    # Servidor
    host: str = Field(
        default="0.0.0.0",
        description="Host para el servidor FastAPI",
    )
    port: int = Field(
        default=8000,
        ge=1,
        le=65535,
        description="Puerto para el servidor FastAPI",
    )
    reload: bool = Field(
        default=False,
        description="Habilitar hot-reload (solo desarrollo)",
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Valida que el nivel de logging sea válido"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"log_level debe ser uno de: {valid_levels}")
        return v_upper

    @field_validator("log_format")
    @classmethod
    def validate_log_format(cls, v: str) -> str:
        """Valida que el formato de log sea válido"""
        valid_formats = ["json", "structured"]
        if v not in valid_formats:
            raise ValueError(f"log_format debe ser uno de: {valid_formats}")
        return v

    class Config:
        """Configuración de pydantic"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False  # Las variables de entorno son case-insensitive


# Instancia global de configuración
settings = Settings()
