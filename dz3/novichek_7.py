"""
Задача 7 (абстрактные методы). Создайте абстрактный класс AutoItem с
абстрактным методом describe(). Этот класс описывает общее понятие
«транспорт в автосалоне», но не может существовать сам по себе — у каждого
конкретного транспорта должно быть своё описание. Унаследуйте от него классы
Car и Motorcycle, каждый из которых обязан реализовать метод describe(),
возвращающий краткое описание транспорта. Проверьте, что объект
абстрактного класса AutoItem создать нельзя (будет ошибка TypeError), а
объекты наследников — можно. Подсказка: используйте from abc import ABC,
abstractmethod. В комментариях объясните, что произойдёт, если наследник
не реализует абстрактный метод.
"""

from abc import ABC, abstractmethod


class AutoItem(ABC):
    @abstractmethod
    def describe(self):
        """Каждый наследник обязан вернуть своё описание."""
        pass


class Car(AutoItem):
    def describe(self):
        return "Автомобиль: 4 колеса, до 5 пассажиров"


class Motorcycle(AutoItem):
    def describe(self):
        return "Мотоцикл: 2 колеса, до 2 пассажиров"


# Наследник, который НЕ реализовал describe().
# Он тоже считается абстрактным, и создать его объект нельзя:
# Python выбросит TypeError при попытке вызвать Bicycle().
class Bicycle(AutoItem):
    pass


# Объект абстрактного класса создать нельзя
try:
    item = AutoItem()
except TypeError as e:
    print("AutoItem():", e)

# Объекты наследников создаются без проблем
for vehicle in (Car(), Motorcycle()):
    print(vehicle.describe())

# Наследник без реализации абстрактного метода
try:
    bike = Bicycle()
except TypeError as e:
    print("Bicycle():", e)
