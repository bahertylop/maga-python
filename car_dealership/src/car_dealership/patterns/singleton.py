"""
Метакласс для паттерна Singleton.

Паттерн Singleton (глава 24). Гарантирует, что у класса
будет только один экземпляр. Метакласс перехватывает
создание объекта через __call__ (глава 23).
"""


class SingletonMeta(type):
    """
    Метакласс, превращающий класс в Singleton.

    Хранит словарь экземпляров по классам. При создании
    объекта проверяет, есть ли уже экземпляр данного класса.
    Если есть — возвращает его. Если нет — создаёт новый.
    """

    _instances: dict = {}

    def __call__(cls, *args, **kwargs):
        """Перехватывает создание объекта."""
        if cls not in SingletonMeta._instances:
            SingletonMeta._instances[cls] = super().__call__(*args, **kwargs)
        return SingletonMeta._instances[cls]


class DealershipRegistry(metaclass=SingletonMeta):
    """
    Единый реестр автосалона (пример использования Singleton).

    Сколько бы раз ни вызвали DealershipRegistry(), вернётся
    один и тот же объект.
    """

    def __init__(self):
        self.name = "АвтоМир"
        self.branches: list = []

    def add_branch(self, city: str) -> None:
        """Добавляет филиал."""
        if city not in self.branches:
            self.branches.append(city)
