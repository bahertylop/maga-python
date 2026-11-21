"""
Сервис проката.

Отвечает только за прокат (SRP, глава 27).
Отделён от DealService, потому что продажа и прокат —
разные бизнес-операции.
"""

from ..interfaces import Rentable, Notifier
from ..exceptions import CarAlreadyRentedError, CarAlreadySoldError


class RentalService:
    """
    Сервис проката автомобилей.

    Зависимости передаются через конструктор (DIP, глава 40).
    """

    # Стоимость суток проката — доля от цены автомобиля.
    DAILY_RATE = 0.0008

    def __init__(self, storage, notifier: Notifier):
        self.storage = storage
        self.notifier = notifier

    def rent(self, vin: str, tenant: str, days: int) -> dict:
        """
        Выдаёт автомобиль в прокат.

        Шаги:
        1. Проверить срок (положительное число суток).
        2. Найти объект.
        3. Проверить, что он не продан, не в прокате и Rentable.
        4. Пометить как арендованный и посчитать стоимость.
        5. Отправить уведомление и вернуть информацию об аренде.
        """
        if days <= 0:
            raise ValueError("Срок проката должен быть больше нуля")

        item = self.storage.find_by_vin(vin)

        if getattr(item, "is_sold", False):
            raise CarAlreadySoldError(vin)

        if not isinstance(item, Rentable):
            raise TypeError(f"{vin} не выдаётся в прокат")

        if getattr(item, "is_rented", False):
            raise CarAlreadyRentedError(vin)

        item.rent()
        item.is_rented = True
        cost = round(item.price * self.DAILY_RATE * days)

        self.notifier.send(
            f"Прокат: {item.title} ({vin}) → {tenant} на {days} дн."
        )

        return {"item": item, "tenant": tenant, "days": days, "cost": cost}

    def return_item(self, vin: str) -> dict:
        """
        Принимает автомобиль из проката.

        Помечает объект как доступный.
        """
        item = self.storage.find_by_vin(vin)
        item.is_rented = False

        self.notifier.send(f"Возвращено из проката: {item.title} ({vin})")

        return {"item": item}
