"""
Демо 1: модели и хранилище.

Запуск:  python examples/demo_basic.py
"""

import _path  # noqa: F401  (настраивает sys.path)

from src.car_dealership.models import Car, Engine, ElectricCar, Motorcycle, Sedan
from src.car_dealership.services import CarStorage


def main() -> None:
    camry = Car("XTA210930Y2765432", "Toyota", "Camry", 3_000_000, 2023, 15_000,
                Engine("бензин", 181, 2.5))
    sedan = Sedan("XTA210930Y2765433", "Kia", "K5", 2_500_000, trunk_volume=510)
    ev = ElectricCar("XTA210930Y2765434", "Tesla", "Model 3", 5_000_000, battery_kwh=75)
    bike = Motorcycle("XTA210930Y2765435", "BMW", "R1250GS", 1_900_000)

    print("— Описания (полиморфизм get_info) —")
    for item in (camry, sedan, ev, bike):
        print(" ", item)

    print("\n— Свойства и методы —")
    print("  Запас хода электромобиля:", ev.range_km, "км")
    print("  Нужно ли ТО Camry:", camry.needs_service)
    print("  Возраст Camry (на 2026):", camry.age(2026), "г.")

    print("\n— Сравнение и сортировка по цене —")
    print(" ", [c.title for c in sorted([camry, sedan, ev, bike])])

    print("\n— Копия с изменением (dataclasses.replace) —")
    cheaper = camry.clone(price=2_700_000, vin="XTA210930Y2765436")
    print(" ", cheaper.price, "| оригинал:", camry.price)

    print("\n— Хранилище ведёт себя как список —")
    storage = CarStorage()
    for item in (camry, sedan, ev, bike):
        storage.add(item)
    print("  len:", len(storage), "| первый:", storage[0].title,
          "| Kia в хранилище:", sedan in storage)
    print("  Марки:", [item.brand for item in storage])


if __name__ == "__main__":
    main()
