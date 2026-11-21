"""
Демо 3: полный сценарий с базой данных.

Работает с временным файлом БД и удаляет его в конце.

Запуск:  python examples/demo_full.py
"""

import tempfile
from pathlib import Path

import _path  # noqa: F401

from src.car_dealership.database import (
    CarRepository, ClientRepository, DatabaseManager, DealRepository,
)
from src.car_dealership.models import Client, Engine
from src.car_dealership.patterns import CarFactory
from src.car_dealership.services import (
    CarStorage, DealService, EmailNotifier, PercentCommission, ReportService,
)


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db_path = str(Path(tmp) / "demo.db")

        print("— 1. Создаём склад и продаём машину —")
        storage = CarStorage()
        storage.add(CarFactory.create(
            "sedan", vin="XTA210930Y2765432", brand="Toyota", model="Camry",
            price=3_000_000, trunk_volume=500,
            engine=Engine("бензин", 181, 2.5)))
        storage.add(CarFactory.create(
            "electric", vin="XTA210930Y2765433", brand="Tesla", model="Model 3",
            price=5_000_000, battery_kwh=75))
        deals = DealService(storage, EmailNotifier(), PercentCommission())
        deal = deals.sell("XTA210930Y2765432", "Петров")

        print("\n— 2. Сохраняем всё в SQLite —")
        with DatabaseManager(db_path) as db:
            cars = CarRepository(db)
            for item in storage:
                cars.save(item)
            ClientRepository(db).save(Client("Иванов", 6_000_000))
            DealRepository(db).save_deal_for(
                deal["item"], deal["buyer"], deal["commission"])
            print("  Сохранено автомобилей:", len(cars.find_all()))

        print("\n— 3. Новый «запуск»: читаем из БД —")
        with DatabaseManager(db_path) as db:
            loaded = CarStorage()
            for item in CarRepository(db).find_all():
                loaded.add(item)
            print("  Клиенты:", ClientRepository(db).find_all())
            print("  Сделки:", [(d["vin"], d["buyer"], d["commission"])
                               for d in DealRepository(db).find_all()])

        print("\n— 4. Типы и состояние восстановлены —")
        for item in loaded:
            print(f"  {type(item).__name__:<12} продан={item.is_sold}  {item.title}")

        print("\n— 5. Отчёт по загруженным данным —")
        print(ReportService().generate(loaded, "АвтоМир"))


if __name__ == "__main__":
    main()
