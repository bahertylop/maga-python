"""
Демо 2: сервисы и паттерны.

Запуск:  python examples/demo_services.py
"""

import _path  # noqa: F401

from src.car_dealership.exceptions import CarAlreadySoldError, DealershipError
from src.car_dealership.models import Client
from src.car_dealership.patterns import (
    CarAdapter, CarFactory, CreditDecorator, WarrantyDecorator,
)
from src.car_dealership.services import (
    CarStorage, DealService, EmailNotifier, FixedCommission,
    LoyaltyCommission, NotificationService, PercentCommission,
    RentalService, ReportService,
)


def main() -> None:
    storage = CarStorage()
    for kind, vin, brand, model, price in (
        ("sedan", "XTA210930Y2765432", "Toyota", "Camry", 3_000_000),
        ("suv", "XTA210930Y2765433", "Volkswagen", "Tiguan", 3_500_000),
        ("motorcycle", "XTA210930Y2765434", "BMW", "R1250GS", 1_900_000),
    ):
        storage.add(CarFactory.create(kind, vin=vin, brand=brand,
                                      model=model, price=price))

    print("— Observer: клиенты подписаны на события —")
    publisher = NotificationService()
    ivan, olga = Client("Иван", 4_000_000), Client("Ольга", 3_000_000)
    publisher.subscribe(ivan)
    publisher.subscribe(olga)

    print("\n— Strategy: одну и ту же сделку считаем по-разному —")
    for strategy in (FixedCommission(), PercentCommission(), LoyaltyCommission()):
        print(f"  {type(strategy).__name__}: "
              f"{strategy.calculate(3_000_000):,.0f} ₽".replace(",", " "))

    print("\n— Сделка с уведомлением подписчиков —")
    deals = DealService(storage, EmailNotifier(), LoyaltyCommission(),
                        publisher=publisher)
    deals.sell("XTA210930Y2765432", "Петров")

    print("\n— Повторная продажа → исключение —")
    try:
        deals.sell("XTA210930Y2765432", "Сидоров")
    except CarAlreadySoldError as e:
        print("  ✗", e)

    print("\n— Прокат —")
    rentals = RentalService(storage, EmailNotifier())
    print("  Стоимость:", rentals.rent("XTA210930Y2765433", "Козлов", 5)["cost"], "₽")
    try:
        rentals.rent("XTA210930Y2765434", "Байкер", 1)
    except TypeError as e:
        print("  ✗ мотоцикл в прокат не выдаётся:", e)
    except DealershipError as e:
        print("  ✗", e)

    print("\n— Decorator + Adapter —")
    car = storage.find_by_vin("XTA210930Y2765433")
    print(" ", WarrantyDecorator(CreditDecorator(car), 3).get_info())
    print(" ", CarAdapter({"vin_code": "XTA210930Y2765499", "maker": "Skoda",
                           "name": "Octavia", "cost": 2_200_000,
                           "production_year": 2021}).get_info())

    print("\n— Отчёты —")
    reports = ReportService()
    print(reports.generate(storage, "АвтоМир"))
    print(reports.generate_sales_report(deals.history))


if __name__ == "__main__":
    main()
