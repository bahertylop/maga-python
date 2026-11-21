"""
Точка входа проекта.

Запуск:

    python main.py

Демонстрирует работу всех ключевых возможностей:
фабрику, хранилище, уведомления, сделки, прокат, отчёты,
декораторы, адаптер, синглтон, исключения.
"""

import sys

from config import DEALERSHIP_NAME
from src.car_dealership.exceptions import CarNotFoundError, DealershipError
from src.car_dealership.models import Client, VehicleItem
from src.car_dealership.patterns import (
    CarAdapter,
    CarFactory,
    CreditDecorator,
    DealershipRegistry,
    WarrantyDecorator,
    WinterTiresDecorator,
)
from src.car_dealership.services import (
    CarStorage,
    DealService,
    EmailNotifier,
    FixedCommission,
    LoyaltyCommission,
    NotificationService,
    PercentCommission,
    RentalService,
    ReportService,
)

# На Windows вывод в файл/IDE может идти в cp1251 и не знать символов ₽ ✓ →.
# Просим стандартный вывод работать в UTF-8 (в консоли это уже так).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

VIN_CAMRY = "XTA210930Y2765432"
VIN_TIGUAN = "XTA210930Y2765433"
VIN_TESLA = "XTA210930Y2765434"
VIN_BMW = "XTA210930Y2765435"


def section(title: str) -> None:
    """Печатает заголовок раздела."""
    print()
    print("=" * 60)
    print(title)
    print("=" * 60)


def main() -> None:
    """Основная демонстрация проекта."""

    section("1. Фабрика создаёт объекты")

    sedan = CarFactory.create(
        "sedan", vin=VIN_CAMRY, brand="Toyota", model="Camry",
        price=3_000_000, year=2023, mileage=15_000, trunk_volume=500,
    )
    suv = CarFactory.create(
        "suv", vin=VIN_TIGUAN, brand="Volkswagen", model="Tiguan",
        price=3_500_000, year=2024, drive="AWD",
    )
    tesla = CarFactory.create(
        "electric", vin=VIN_TESLA, brand="Tesla", model="Model 3",
        price=5_000_000, battery_kwh=75,
    )
    bike = CarFactory.create(
        "motorcycle", vin=VIN_BMW, brand="BMW", model="R1250GS",
        price=1_900_000, engine_cc=1254,
    )
    items = [sedan, suv, tesla, bike]
    for item in items:
        print(f"  {item.get_info()}")

    section("2. Хранилище")

    storage = CarStorage()
    for item in items:
        storage.add(item)
    print(f"  Добавлено объектов: {len(storage)}")
    print(f"  Найдено по VIN: {storage.find_by_vin(VIN_CAMRY).title}")
    print(f"  Дешевле 3.2 млн: {[i.title for i in storage.filter(lambda i: i.price < 3_200_000)]}")

    section("3. Уведомления (Observer)")

    publisher = NotificationService()
    client = Client("Иванов", 10_000_000)
    publisher.subscribe(client)
    print(f"  Подписчиков: {publisher.count()}")

    section("4. Продажа (Strategy)")

    deals = DealService(storage, EmailNotifier(), PercentCommission(),
                        publisher=publisher)
    result = deals.sell(VIN_CAMRY, "Петров")
    print(f"  Покупатель: {result['buyer']}")
    print(f"  Комиссия: {result['commission']:,.0f} ₽".replace(",", " "))

    section("5. Прокат")

    rentals = RentalService(storage, EmailNotifier())
    rent = rentals.rent(VIN_TESLA, "Сидоров", 3)
    print(f"  Стоимость проката: {rent['cost']:,} ₽".replace(",", " "))

    section("6. Отчёты")

    reports = ReportService()
    print(reports.generate(storage, DEALERSHIP_NAME))
    print()
    print(reports.generate_stats(storage))
    print()
    print(reports.generate_sales_report(deals.history))

    section("7. Декораторы")

    decorated = WarrantyDecorator(CreditDecorator(WinterTiresDecorator(suv)), 5)
    print(f"  {decorated.get_info()}")

    section("8. Адаптер")

    external = CarAdapter({
        "vin_code": "XTA210930Y2765499", "maker": "Skoda", "name": "Octavia",
        "cost": 2_200_000, "production_year": 2021,
    })
    print(f"  {external.get_info()}")

    section("9. Собственные исключения")

    try:
        storage.find_by_vin("XTA210930Y2765000")
    except CarNotFoundError as e:
        print(f"  Поймано: {e}")
    try:
        deals.sell(VIN_CAMRY, "Ещё один покупатель")
    except DealershipError as e:
        print(f"  Поймано (общий базовый класс): {e}")

    section("10. Классовый счётчик и Singleton")

    print(f"  Создано транспортных средств: {VehicleItem.count}")
    print(f"  Реестр один и тот же: {DealershipRegistry() is DealershipRegistry()}")

    section("11. Полиморфизм: страховка")

    for item in items:
        print(f"  {item.title:<18} {item.insurance_cost():>7,} ₽/год".replace(",", " "))

    section("12. Стратегии комиссии")

    price = 3_000_000
    for strategy in (FixedCommission(), PercentCommission(), LoyaltyCommission()):
        print(f"  {strategy.__class__.__name__:<18} "
              f"{strategy.calculate(price):>10,.0f} ₽".replace(",", " "))

    section("ГОТОВО")


if __name__ == "__main__":
    main()
