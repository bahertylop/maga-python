"""
Настройка логирования.

Функция setup_logging создаёт и настраивает логгер.
Класс DealershipLogger — удобная обёртка над логгером.
"""

import logging


def setup_logging(level=logging.INFO) -> logging.Logger:
    """
    Настраивает и возвращает логгер для проекта.

    Если у логгера уже есть обработчики, повторная настройка
    не выполняется — это защита от дублирования сообщений.
    """
    logger = logging.getLogger("car_dealership")
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


class DealershipLogger:
    """
    Обёртка над стандартным логгером.

    Предоставляет методы info, warning, error
    для удобной записи сообщений.
    """

    def __init__(self, name: str = "dealership"):
        self.logger = logging.getLogger(f"car_dealership.{name}")

    def info(self, message: str) -> None:
        """Записывает информационное сообщение."""
        self.logger.info(message)

    def warning(self, message: str) -> None:
        """Записывает предупреждение."""
        self.logger.warning(message)

    def error(self, message: str) -> None:
        """Записывает сообщение об ошибке."""
        self.logger.error(message)
