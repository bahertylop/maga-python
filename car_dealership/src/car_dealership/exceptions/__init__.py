"""
Экспорт исключений.

Позволяет импортировать всё напрямую из пакета exceptions:

    from src.car_dealership.exceptions import CarNotFoundError
"""

from .errors import (
    DealershipError,
    CarNotFoundError,
    CarAlreadySoldError,
    CarAlreadyRentedError,
    DuplicateCarError,
    InvalidVinError,
    InvalidPriceError,
    InvalidMileageError,
    DatabaseError,
)

__all__ = [
    "DealershipError",
    "CarNotFoundError",
    "CarAlreadySoldError",
    "CarAlreadyRentedError",
    "DuplicateCarError",
    "InvalidVinError",
    "InvalidPriceError",
    "InvalidMileageError",
    "DatabaseError",
]
