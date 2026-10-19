"""
Задача 35 (принципы OCP и LSP из SOLID). В автосалоне появился новый тип
транспорта — электромобиль (ElectricCar). Если добавлять его через изменение
базового класса AutoItem, это нарушит принцип OCP (Open/Closed Principle) —
классы должны быть открыты для расширения, но закрыты для изменения.
Дополнительно нужно проверить принцип LSP (Liskov Substitution Principle) —
объект наследника должен без проблем заменять объект родителя. Реализуйте:
базовый класс AutoItem с методом tax(); наследников Sedan, SUV; функцию
process_item(item: AutoItem), которая работает с любым транспортом через
родительский интерфейс. Добавьте ElectricCar без изменения существующего
кода — это и есть OCP. Затем проверьте, что process_item одинаково хорошо
работает со всеми тремя типами, — это LSP. Объясните оба принципа и
приведите примеры их нарушения (классический пример нарушения LSP: «квадрат —
не прямоугольник», если сеттеры ширины и высоты меняют оба измерения).
"""

from abc import ABC, abstractmethod


# =============== Существующий код (его НЕ трогаем) ===============
class AutoItem(ABC):
    def __init__(self, model):
        self.model = model

    @abstractmethod
    def tax(self) -> int:
        """Налог в рублях. Контракт: целое число >= 0."""

    def describe(self) -> str:
        return f"{type(self).__name__} {self.model}"


class Sedan(AutoItem):
    def tax(self):
        return 5000


class SUV(AutoItem):
    def tax(self):
        return 12000


def process_item(item: AutoItem):
    """Работает только через интерфейс родителя: describe() и tax()."""
    tax = item.tax()
    assert isinstance(tax, int) and tax >= 0, "нарушен контракт tax()"
    print(f"  {item.describe():<38} налог {tax:>6} ₽")
    return tax


# =============== Расширение: новый класс, старый код не изменён ===============
class ElectricCar(AutoItem):
    def __init__(self, model, battery_kwh):
        super().__init__(model)
        self.battery_kwh = battery_kwh

    def tax(self):
        return 0  # льгота — но это всё ещё корректное число >= 0

    def describe(self):
        return f"{super().describe()} ({self.battery_kwh} кВт·ч)"


print("OCP + LSP: process_item работает со всеми типами одинаково")
fleet = [Sedan("Toyota Camry"), SUV("BMW X5"), ElectricCar("Tesla Model 3", 75)]
total = sum(process_item(item) for item in fleet)
print(f"  Итого налогов: {total} ₽")


# =============== Пример нарушения OCP ===============
def tax_bad(kind):
    # Каждый новый тип — правка этой функции (и всех похожих в проекте)
    if kind == "sedan":
        return 5000
    elif kind == "suv":
        return 12000
    elif kind == "electric":  # ← пришлось ИЗМЕНИТЬ готовый код
        return 0
    raise ValueError(kind)


# =============== Пример нарушения LSP: «квадрат — не прямоугольник» ===============
class Rectangle:
    def __init__(self, width, height):
        self._width, self._height = width, height

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        self._width = value

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._height = value

    def area(self):
        return self._width * self._height


class Square(Rectangle):
    def __init__(self, side):
        super().__init__(side, side)

    # Чтобы квадрат оставался квадратом, сеттеры меняют ОБЕ стороны
    @Rectangle.width.setter
    def width(self, value):
        self._width = self._height = value

    @Rectangle.height.setter
    def height(self, value):
        self._width = self._height = value


def resize_parking_spot(rect: Rectangle):
    """Код, написанный для Rectangle: ожидает, что стороны меняются независимо."""
    rect.width = 5
    rect.height = 2
    expected = 10
    ok = rect.area() == expected
    print(f"  {type(rect).__name__:<9} площадь {rect.area():>2}, ожидали {expected} "
          f"→ {'OK' if ok else 'LSP НАРУШЕН'}")


print("\nНарушение LSP:")
resize_parking_spot(Rectangle(1, 1))
resize_parking_spot(Square(1))


# Ещё одно нарушение LSP в духе автосалона:
class BrokenElectricCar(AutoItem):
    def tax(self):
        raise NotImplementedError("для электромобилей налог не считается")


print("\nНаследник, который ломает контракт родителя:")
try:
    process_item(BrokenElectricCar("Some EV"))
except NotImplementedError as e:
    print("  process_item упал:", e)

# OCP (принцип открытости/закрытости):
# модули должны быть ОТКРЫТЫ для расширения (можно добавить новое
# поведение) и ЗАКРЫТЫ для изменения (не нужно править уже работающий,
# протестированный код). Здесь ElectricCar добавлен новым классом-наследником:
# ни AutoItem, ни Sedan, ни SUV, ни process_item не изменились. Новое
# поведение подключается через полиморфизм.
# Нарушение OCP — tax_bad: каждый новый тип транспорта требует лезть
# в готовую функцию и добавлять elif (и так во всех подобных местах).
# Сюда же относится вариант «изменить базовый класс AutoItem», вписав в
# него знание об электромобилях: if self.is_electric: ...
#
# LSP (принцип подстановки Барбары Лисков):
# объект наследника должен подставляться везде, где ожидается родитель,
# без поломок и сюрпризов. Наследник не должен ужесточать требования к
# входным данным, ослаблять гарантии результата и бросать исключения,
# которых родитель не обещал. ElectricCar соблюдает контракт: tax()
# возвращает целое число >= 0, просто равное нулю.
# Нарушения:
# - «квадрат — не прямоугольник»: математически квадрат — частный случай
#   прямоугольника, но ПОВЕДЕНИЕ разное. Код для Rectangle рассчитывает,
#   что width и height меняются независимо; Square при установке ширины
#   меняет и высоту, и площадь получается 4 вместо 10. Выход — не
#   наследовать Square от Rectangle (общий родитель Shape с area()) или
#   сделать фигуры неизменяемыми;
# - BrokenElectricCar: вместо числа бросает исключение, и любой код,
#   работающий с AutoItem, ломается на нём.
# Признак нарушения LSP — проверки вида if isinstance(item, Square): ...
# в коде, который должен работать с базовым типом.
