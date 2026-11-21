"""
Экспорт всех сервисов.

Позволяет импортировать всё напрямую:

    from src.car_dealership.services import CarStorage, DealService
"""

from .storage import CarStorage
from .commission import (
    CommissionStrategy,
    FixedCommission,
    PercentCommission,
    LoyaltyCommission,
)
from .notification_service import (
    NotificationService,
    EmailNotifier,
    SmsNotifier,
)
from .deal_service import DealService
from .rental_service import RentalService
from .report_service import ReportService

__all__ = [
    "CarStorage",
    "CommissionStrategy",
    "FixedCommission",
    "PercentCommission",
    "LoyaltyCommission",
    "NotificationService",
    "EmailNotifier",
    "SmsNotifier",
    "DealService",
    "RentalService",
    "ReportService",
]
