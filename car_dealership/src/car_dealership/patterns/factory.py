"""
Фабрика транспортных средств.

Паттерн Factory (глава 25). Скрывает логику создания
объектов за единым интерфейсом. Добавление нового типа
не требует изменения существующего кода (OCP, глава 35).
"""

from ..models import Car, Sedan, SUV, Motorcycle, ElectricCar


class CarFactory:
    """
    Фабрика для создания транспортных средств.

    Хранит словарь типов. Создаёт объект по строковому
    идентификатору. Позволяет регистрировать новые типы
    через декоратор.
    """

    _registry = {
        "car": Car,
        "sedan": Sedan,
        "suv": SUV,
        "motorcycle": Motorcycle,
        "electric": ElectricCar,
    }

    @classmethod
    def create(cls, kind: str, **kwargs):
        """
        Создаёт объект указанного типа.

        Если тип неизвестен, выбрасывает ValueError
        с перечислением доступных типов.
        """
        if kind not in cls._registry:
            raise ValueError(
                f"Неизвестный тип: {kind!r}. "
                f"Доступные: {list(cls._registry.keys())}"
            )
        return cls._registry[kind](**kwargs)

    @classmethod
    def register(cls, kind: str):
        """
        Декоратор для регистрации нового типа.

        Использование:
            @CarFactory.register("pickup")
            class Pickup(Car): ...
        """
        def decorator(klass):
            cls._registry[kind] = klass
            return klass
        return decorator

    @classmethod
    def list_kinds(cls) -> list:
        """Возвращает список зарегистрированных типов."""
        return list(cls._registry.keys())
