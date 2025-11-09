"""
Configuración de logging estructurado
"""

import logging
import logging.handlers
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


class JSONFormatter(logging.Formatter):
    """
    Formatter que produce logs en formato JSON para facilitar
    parsing y análisis con herramientas como ELK stack.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Formatea el log record como JSON"""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Agregar información de excepción si existe
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Agregar campos extra si existen
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        return json.dumps(log_data, ensure_ascii=False)


class StructuredFormatter(logging.Formatter):
    """
    Formatter para desarrollo que produce logs legibles en consola
    """

    def format(self, record: logging.LogRecord) -> str:
        """Formatea el log record de forma estructurada y legible"""
        timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")

        # Colorear por nivel (solo para terminales que soporten ANSI)
        level_colors = {
            "DEBUG": "\033[36m",  # Cyan
            "INFO": "\033[32m",   # Green
            "WARNING": "\033[33m",  # Yellow
            "ERROR": "\033[31m",  # Red
            "CRITICAL": "\033[35m",  # Magenta
        }
        reset_color = "\033[0m"

        level = record.levelname
        color = level_colors.get(level, "")

        # Formato: [timestamp] LEVEL module.function:line - message
        formatted = f"[{timestamp}] {color}{level:8s}{reset_color} {record.name}:{record.lineno} - {record.getMessage()}"

        # Agregar excepción si existe
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"

        return formatted


def setup_logging(
    log_level: str = "INFO",
    log_format: str = "structured",
    log_file: str | None = None,
    enable_rotation: bool = True,
) -> None:
    """
    Configura el sistema de logging para la aplicación.

    Args:
        log_level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Formato de logs ("json" o "structured")
        log_file: Path del archivo de log. Si None, solo se loguea a consola
        enable_rotation: Si True, habilita rotación de archivos de log
    """
    # Convertir string a nivel de logging
    level = getattr(logging, log_level.upper(), logging.INFO)

    # Obtener root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Limpiar handlers existentes
    root_logger.handlers.clear()

    # Seleccionar formatter
    if log_format == "json":
        formatter = JSONFormatter()
    else:
        formatter = StructuredFormatter()

    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Handler para archivo (opcional)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        if enable_rotation:
            # Rotación: 10MB por archivo, mantener 5 backups
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
                encoding="utf-8",
            )
        else:
            file_handler = logging.FileHandler(log_file, encoding="utf-8")

        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Configurar niveles para librerías de terceros
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("celery").setLevel(logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    # Log inicial
    root_logger.info(
        f"Logging configurado: level={log_level}, format={log_format}, file={log_file}"
    )


def get_logger(name: str) -> logging.Logger:
    """
    Obtiene un logger con el nombre especificado.

    Args:
        name: Nombre del logger (usualmente __name__ del módulo)

    Returns:
        Logger configurado
    """
    return logging.getLogger(name)
