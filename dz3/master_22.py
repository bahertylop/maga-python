"""
Задача 22 (дескрипторы). Свойство @property — это удобно, но что если таких
свойств с одинаковой проверкой нужно много? Лучше вынести логику в отдельный
класс-дескриптор. Реализуйте собственный дескриптор
RangeDescriptor(min_value, max_value), который хранит значение в
instance.__dict__ (иначе все объекты делили бы одно значение) и проверяет,
что оно в диапазоне, выбрасывая ValueError при нарушении. Используйте этот
дескриптор в классе Car для полей price (например, диапазон
100 000–100 000 000) и year (диапазон 1950–2100), продемонстрировав, что один
и тот же дескриптор переиспользуется в разных полях. Объясните, как
дескрипторы работают «под капотом» @property, зачем нужен метод __set_name__
и в чём преимущество дескриптора перед @property, если одинаковая проверка
повторяется в десяти полях.
"""


class RangeDescriptor:
    def __init__(self, min_value, max_value):
        self.min_value = min_value
        self.max_value = max_value
        self.name = None

    def __set_name__(self, owner, name):
        # Вызывается автоматически при создании класса Car.
        # owner — класс Car, name — имя поля ("price" или "year").
        # Без этого дескриптор не знал бы, под каким ключом хранить значение.
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self  # обращение через класс: Car.price
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{self.name}: ожидается число, получено {value!r}")
        if not self.min_value <= value <= self.max_value:
            raise ValueError(
                f"{self.name}: значение {value} вне диапазона "
                f"{self.min_value}–{self.max_value}"
            )
        # Храним в словаре ОБЪЕКТА, а не в самом дескрипторе.
        # Дескриптор один на весь класс; если бы писали self.value = value,
        # все автомобили делили бы одну цену.
        instance.__dict__[self.name] = value


class Car:
    price = RangeDescriptor(100_000, 100_000_000)  # один класс-дескриптор —
    year = RangeDescriptor(1950, 2100)             # два разных поля

    def __init__(self, brand, model, price, year):
        self.brand = brand
        self.model = model
        self.price = price  # срабатывает RangeDescriptor.__set__
        self.year = year

    def __repr__(self):
        return f"Car({self.brand!r}, {self.model!r}, price={self.price}, year={self.year})"


camry = Car("Toyota", "Camry", 2_500_000, 2023)
rio = Car("Kia", "Rio", 1_800_000, 2021)
print(camry)
print(rio)  # у каждого объекта свои значения — хранятся в своём __dict__
print("camry.__dict__:", camry.__dict__)

tests = [
    ("price", 50_000),
    ("price", 200_000_000),
    ("year", 1900),
    ("year", "2020"),
    ("price", 3_000_000),
]
for field, value in tests:
    try:
        setattr(camry, field, value)
        print(f"camry.{field} = {value!r} → успех")
    except ValueError as e:
        print(f"camry.{field} = {value!r} → ошибка: {e}")

print("Итог:", camry)

# Как дескрипторы работают «под капотом» @property:
# Дескриптор — это объект с методами __get__ / __set__ / __delete__,
# который лежит в атрибуте КЛАССА. Когда пишем car.price, Python находит
# price в классе, видит, что это дескриптор, и вызывает
# price.__get__(car, Car); при car.price = x — price.__set__(car, x).
# @property — это просто встроенный дескриптор: property(fget, fset)
# хранит наши функции и вызывает их из своих __get__ и __set__.
# Тем же механизмом сделаны методы, @classmethod и @staticmethod.
#
# Зачем __set_name__: дескриптор создаётся раньше, чем узнаёт, в какой
# атрибут его положили. Python после создания класса вызывает
# __set_name__(Car, "price"), и дескриптор запоминает своё имя — его не
# нужно дублировать вручную: price = RangeDescriptor("price", ...).
#
# Преимущество перед @property при десяти одинаковых полях:
# с @property пришлось бы написать 10 геттеров и 10 сеттеров с одной и
# той же проверкой — 20 почти одинаковых функций. Дескриптор пишется
# один раз, а каждое поле объявляется одной строкой. Логику проверки
# легко менять в одном месте и переиспользовать в других классах.
