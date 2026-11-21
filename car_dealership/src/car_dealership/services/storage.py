"""
Хранилище автомобилей.

Отвечает только за хранение и поиск (SRP, глава 27).
Реализует магические методы, чтобы работать как список
(главы 31, 32) и интерфейс Storage (глава 40).
"""

from typing import Callable, List

from ..interfaces import Storage
from ..exceptions import CarNotFoundError, DuplicateCarError


class CarStorage(Storage):
    """
    Хранилище транспортных средств.

    Хранит объекты в списке. Умеет искать по VIN, по марке
    и по произвольному условию. При поиске несуществующего
    автомобиля выбрасывает CarNotFoundError.
    """

    def __init__(self):
        self._items: list = []

    def add(self, item) -> None:
        """Добавляет объект в хранилище. VIN должен быть уникален."""
        if any(existing.vin == item.vin for existing in self._items):
            raise DuplicateCarError(item.vin)
        self._items.append(item)

    def save(self, item) -> None:
        """Реализация интерфейса Storage: то же, что add()."""
        self.add(item)

    def find_by_vin(self, vin: str):
        """
        Ищет объект по VIN.

        Если объект найден, возвращает его.
        Если не найден, выбрасывает CarNotFoundError.
        """
        for item in self._items:
            if getattr(item, "vin", None) == vin:
                return item
        raise CarNotFoundError(vin)

    def find_by_brand(self, brand: str) -> list:
        """Возвращает все объекты указанной марки (без учёта регистра)."""
        return [i for i in self._items if i.brand.lower() == brand.lower()]

    def filter(self, predicate: Callable) -> list:
        """Возвращает объекты, для которых predicate(item) истинно."""
        return [item for item in self._items if predicate(item)]

    def available(self) -> list:
        """Возвращает объекты, которые ещё не проданы."""
        return self.filter(lambda item: not item.is_sold)

    def total_value(self) -> int:
        """Суммарная стоимость непроданных автомобилей."""
        return sum(item.price for item in self.available())

    def remove(self, item) -> None:
        """Удаляет объект из хранилища."""
        if item in self._items:
            self._items.remove(item)

    def list_all(self) -> List:
        """Возвращает копию списка всех объектов."""
        return list(self._items)

    def __len__(self) -> int:
        """Количество объектов в хранилище."""
        return len(self._items)

    def __iter__(self):
        """Позволяет перебирать объекты в цикле for."""
        return iter(self._items)

    def __contains__(self, item) -> bool:
        """Позволяет использовать оператор in."""
        return item in self._items

    def __getitem__(self, index):
        """Позволяет обращаться по индексу и срезу."""
        return self._items[index]
