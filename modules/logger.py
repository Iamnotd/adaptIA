"""
modules/logger.py
Configuración centralizada del sistema de logs con loguru.
"""

import sys
import os
from loguru import logger
from config import LOGS_DIR

logger.remove()  # quitar handler por defecto

# Log en consola
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{module}</cyan> - <level>{message}</level>",
    level="INFO"
)

# Log en archivo, rotación diaria, se conserva 7 días
logger.add(
    os.path.join(LOGS_DIR, "adaptia_{time:YYYY-MM-DD}.log"),
    rotation="00:00",
    retention="7 days",
    encoding="utf-8",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {module}:{function}:{line} - {message}"
)


def get_logger():
    """Devuelve la instancia configurada del logger."""
    return logger
