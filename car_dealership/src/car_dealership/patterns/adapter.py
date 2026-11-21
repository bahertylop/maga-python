"""
Адаптер для внешней системы учёта.

Паттерн Adapter (глава 39). Приводит словарь внешней
системы (например, от дилера) к интерфейсу Car: свойства
vin, brand, model, price, year и метод get_info().
"""

from ..interfaces import Infoable
from ..utils import CarUtils


class CarAdapter(Infoable):
    """
    Адаптер внешних данных к интерфейсу Car.

    Принимает словарь. Предоставляет свойства vin, brand, model,
    price, year. Поддерживает два набора ключей: внешний
    (vin_code, maker, name, cost, production_year) и внутренний
    (vin, brand, model, price, year).
    """

    def __init__(self, data: dict):
        self._data = data

    def _get(self, *keys, default=None):
        """Возвращает первое найденное и непустое значение по ключам."""
        for key in keys:
            if self._data.get(key) is not None:
                return self._data[key]
        return default

    @property
    def vin(self):
        """VIN: из vin_code или vin."""
        return self._get("vin_code", "vin")

    @property
    def brand(self):
        """Марка: из maker или brand."""
        return self._get("maker", "brand")

    @property
    def model(self):
        """Модель: из name или model."""
        return self._get("name", "model")

    @property
    def price(self):
        """Цена: из cost или price."""
        return self._get("cost", "price", default=0)

    @property
    def year(self):
        """Год выпуска: из production_year или year."""
        return self._get("production_year", "year")

    def get_info(self) -> str:
        """Описание в том же стиле, что у Car."""
        return (
            f"{self.brand} {self.model} ({self.year}), VIN {self.vin}: "
            f"{CarUtils.format_price(self.price)}"
        )
