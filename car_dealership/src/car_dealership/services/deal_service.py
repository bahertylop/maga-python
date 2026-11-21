"""
Сервис оформления сделок.

Отвечает только за сделки (SRP, глава 27).
Зависит от абстракций: Storage, Notifier, CommissionStrategy (DIP, глава 40).
"""

from datetime import date

from ..interfaces import Sellable, Notifier
from ..exceptions import CarAlreadyRentedError, CarAlreadySoldError


class DealService:
    """
    Сервис оформления сделок.

    Зависимости передаются через конструктор. Сервис не создаёт
    их сам: это позволяет подменять реализации.
    """

    def __init__(self, storage, notifier: Notifier, commission=None,
                 publisher=None):
        self.storage = storage
        self.notifier = notifier
        self.commission = commission
        self.publisher = publisher  # NotificationService (Observer), необязателен
        self.history: list = []

    def sell(self, vin: str, buyer: str) -> dict:
        """
        Продаёт транспортное средство по VIN.

        Шаги:
        1. Найти объект в хранилище.
        2. Проверить, что он не продан и не находится в прокате.
        3. Проверить, что он продаётся (интерфейс Sellable).
        4. Пометить проданным.
        5. Рассчитать комиссию (если стратегия задана).
        6. Отправить уведомление и оповестить подписчиков.
        7. Записать сделку в историю и вернуть её.
        """
        item = self.storage.find_by_vin(vin)

        if getattr(item, "is_sold", False):
            raise CarAlreadySoldError(vin)

        if getattr(item, "is_rented", False):
            raise CarAlreadyRentedError(vin)

        if not isinstance(item, Sellable):
            raise TypeError(f"{vin} не продаётся")

        item.sell()

        commission = (
            self.commission.calculate(item.price)
            if self.commission else 0
        )

        self.notifier.send(f"Продано: {item.title} ({vin}) → {buyer}")
        if self.publisher is not None:
            self.publisher.notify(f"Продан {item.title}")

        deal = {
            "item": item,
            "buyer": buyer,
            "commission": commission,
            "date": date.today().isoformat(),
        }
        self.history.append(deal)
        return deal
