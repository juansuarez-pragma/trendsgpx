"""
Rate limiter para controlar requests a APIs externas
"""

import time
from threading import Lock
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Rate limiter simple basado en token bucket.
    Thread-safe para uso concurrente.
    """

    def __init__(self, max_requests: int, period_seconds: int, name: str = "default"):
        """
        Inicializa el rate limiter.

        Args:
            max_requests: Número máximo de requests permitidos
            period_seconds: Período en segundos
            name: Nombre del limiter para logging
        """
        self.max_requests = max_requests
        self.period_seconds = period_seconds
        self.name = name

        # Estado interno
        self._tokens = max_requests
        self._last_refill = time.time()
        self._lock = Lock()

        logger.info(
            f"RateLimiter '{name}' inicializado: "
            f"{max_requests} requests / {period_seconds}s"
        )

    def _refill_tokens(self) -> None:
        """
        Rellena tokens basado en el tiempo transcurrido.
        Debe llamarse con el lock adquirido.
        """
        now = time.time()
        elapsed = now - self._last_refill

        # Calcular tokens a agregar basado en tiempo transcurrido
        tokens_to_add = (elapsed / self.period_seconds) * self.max_requests

        if tokens_to_add > 0:
            self._tokens = min(self.max_requests, self._tokens + tokens_to_add)
            self._last_refill = now

    def acquire(self, blocking: bool = True, timeout: float | None = None) -> bool:
        """
        Intenta adquirir un token para hacer un request.

        Args:
            blocking: Si True, espera hasta obtener token. Si False, retorna inmediatamente
            timeout: Tiempo máximo a esperar (solo si blocking=True)

        Returns:
            True si se adquirió token, False si no (solo en modo no-blocking)
        """
        start_time = time.time()

        while True:
            with self._lock:
                self._refill_tokens()

                if self._tokens >= 1:
                    self._tokens -= 1
                    logger.debug(
                        f"RateLimiter '{self.name}': token adquirido "
                        f"({self._tokens:.2f} restantes)"
                    )
                    return True

                if not blocking:
                    logger.warning(f"RateLimiter '{self.name}': sin tokens disponibles")
                    return False

                # Calcular tiempo a esperar para el próximo token
                time_for_next_token = self.period_seconds / self.max_requests

            # Verificar timeout
            if timeout is not None:
                elapsed = time.time() - start_time
                if elapsed >= timeout:
                    logger.warning(
                        f"RateLimiter '{self.name}': timeout después de {elapsed:.2f}s"
                    )
                    return False

            # Esperar un poco antes de reintentar
            sleep_time = min(time_for_next_token, 0.1)
            logger.debug(
                f"RateLimiter '{self.name}': esperando {sleep_time:.2f}s para próximo token"
            )
            time.sleep(sleep_time)

    def get_available_tokens(self) -> float:
        """
        Retorna el número de tokens disponibles actualmente.

        Returns:
            Número de tokens disponibles (puede ser decimal)
        """
        with self._lock:
            self._refill_tokens()
            return self._tokens

    def reset(self) -> None:
        """Resetea el limiter a su estado inicial"""
        with self._lock:
            self._tokens = self.max_requests
            self._last_refill = time.time()
            logger.info(f"RateLimiter '{self.name}': reseteado")


class RateLimiterManager:
    """
    Gestor de múltiples rate limiters.
    Mantiene un rate limiter por plataforma.
    """

    def __init__(self):
        self._limiters: Dict[str, RateLimiter] = {}
        self._lock = Lock()

    def get_limiter(
        self,
        name: str,
        max_requests: int,
        period_seconds: int,
    ) -> RateLimiter:
        """
        Obtiene o crea un rate limiter.

        Args:
            name: Nombre del limiter (ej: "youtube", "reddit")
            max_requests: Máximo de requests
            period_seconds: Período en segundos

        Returns:
            RateLimiter configurado
        """
        with self._lock:
            if name not in self._limiters:
                self._limiters[name] = RateLimiter(
                    max_requests=max_requests,
                    period_seconds=period_seconds,
                    name=name,
                )
                logger.info(f"RateLimiter creado para '{name}'")

            return self._limiters[name]

    def reset_all(self) -> None:
        """Resetea todos los limiters"""
        with self._lock:
            for limiter in self._limiters.values():
                limiter.reset()
            logger.info("Todos los RateLimiters reseteados")


# Instancia global del manager
rate_limiter_manager = RateLimiterManager()
