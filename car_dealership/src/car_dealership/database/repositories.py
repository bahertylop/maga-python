"""
Репозитории для работы с сущностями.

Репозиторий — это слой между бизнес-логикой и базой данных.
Он скрывает SQL и предоставляет удобный интерфейс для работы
с объектами домена (SRP, глава 27).
"""

import json
from datetime import date

from ..models import Client, VEHICLE_TYPES
from ..exceptions import DatabaseError


def row_to_vehicle(row):
    """Восстанавливает объект нужного класса из строки таблицы cars."""
    data = {key: row[key] for key in row.keys() if key not in ("id", "extra")}
    data.update(json.loads(row["extra"] or "{}"))
    klass = VEHICLE_TYPES.get(row["type"])
    if klass is None:
        raise DatabaseError(f"Неизвестный тип в базе: {row['type']!r}")
    return klass.from_dict(data)


class CarRepository:
    """
    Репозиторий автомобилей.

    Сохраняет, ищет и удаляет транспортные средства через
    DatabaseManager. Возвращает объекты правильных классов
    (Car, Sedan, SUV, Motorcycle, ElectricCar).
    """

    def __init__(self, manager):
        self.manager = manager

    def save(self, car) -> int:
        """Сохраняет автомобиль в базу."""
        return self.manager.save_car(car)

    def find_by_vin(self, vin: str):
        """Возвращает объект или None."""
        row = self.manager.find_car(vin)
        return None if row is None else row_to_vehicle(row)

    def find_all(self) -> list:
        """Возвращает список всех автомобилей."""
        return [row_to_vehicle(row) for row in self.manager.find_all_cars()]

    def delete(self, vin: str) -> bool:
        """Удаляет автомобиль по VIN."""
        return self.manager.delete_car(vin)


class ClientRepository:
    """
    Репозиторий клиентов.

    Сохраняет и загружает клиентов.
    """

    def __init__(self, manager):
        self.manager = manager

    def save(self, client) -> int:
        """Сохраняет клиента."""
        return self.manager.save_client(client)

    def find_all(self) -> list:
        """Возвращает всех клиентов как объекты Client."""
        return [
            Client(row["name"], row["budget"])
            for row in self.manager.find_all_clients()
        ]


class DealRepository:
    """
    Репозиторий сделок.

    Сохраняет и загружает сделки.
    """

    def __init__(self, manager):
        self.manager = manager

    def save(self, deal: dict) -> int:
        """Сохраняет сделку (словарь для DatabaseManager.save_deal)."""
        return self.manager.save_deal(deal)

    def save_deal_for(self, car, buyer: str, commission: float) -> int:
        """Сохраняет сделку по объекту автомобиля (автомобиль должен быть в БД)."""
        car_id = self.manager.find_car_id(car.vin)
        if car_id is None:
            raise DatabaseError(f"Автомобиль {car.vin} не найден в БД")
        return self.save({
            "car_id": car_id,
            "buyer": buyer,
            "commission": commission,
            "date": date.today().isoformat(),
        })

    def find_all(self) -> list:
        """Возвращает сделки как список словарей."""
        return [dict(row) for row in self.manager.find_all_deals()]
