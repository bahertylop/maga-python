"""
Двигатель.

Используется в композиции с классом Car: автомобиль содержит
объект Engine как часть себя. Без автомобиля двигатель в нашей
системе не существует.
"""

from ..utils import RangeDescriptor


class Engine:
    """
    Двигатель автомобиля.

    Мощность и объём проверяются дескрипторами: при попытке записать
    значение вне диапазона выбрасывается ValueError.
    """

    power_hp = RangeDescriptor(1, 2000)
    volume_l = RangeDescriptor(0, 10)

    def __init__(self, kind: str = "бензин", power_hp: int = 150,
                 volume_l: float = 2.0):
        self.kind = kind
        self.power_hp = power_hp
        self.volume_l = volume_l

    def show(self) -> str:
        """Возвращает строковое описание двигателя."""
        if self.kind == "электро":
            return f"электро {self.power_hp} л.с."
        return f"{self.kind} {self.volume_l} л, {self.power_hp} л.с."

    def to_dict(self) -> dict:
        """Преобразует двигатель в словарь (для хранения в БД)."""
        return {
            "kind": self.kind,
            "power_hp": self.power_hp,
            "volume_l": self.volume_l,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Engine":
        """Создаёт двигатель из словаря."""
        return cls(data["kind"], data["power_hp"], data["volume_l"])

    def __eq__(self, other) -> bool:
        if not isinstance(other, Engine):
            return NotImplemented
        return self.to_dict() == other.to_dict()

    __hash__ = None  # объект изменяемый, хэшировать его нельзя

    def __repr__(self) -> str:
        return (
            f"Engine({self.kind!r}, {self.power_hp}, {self.volume_l})"
        )
