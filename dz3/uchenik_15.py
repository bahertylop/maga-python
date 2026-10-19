"""
Задача 15 (классовый метод @classmethod). В автосалон часто поступают данные
об автомобилях в виде строк — например, из файла или базы данных:
"Toyota;Camry;2500000". Добавьте в класс Car классовый метод
from_string(cls, data), который создаёт объект автомобиля из такой строки,
разбивая её по точке с запятой. Продемонстрируйте создание автомобиля через
этот метод и вывод результата. Объясните разницу между @classmethod,
@staticmethod и обычным методом: обычный метод получает первым аргументом
экземпляр (self) и работает с конкретным объектом, @classmethod получает сам
класс (cls) и часто используется как альтернативный конструктор,
@staticmethod не получает ни self, ни cls и представляет собой просто
утилиту. Расскажите, когда какой использовать.
"""


class Car:
    def __init__(self, brand, model, price):
        self.brand = brand
        self.model = model
        self.price = price

    # Обычный метод: получает self — конкретный автомобиль
    def info(self):
        price_str = f"{self.price:,}".replace(",", " ")
        return f"{self.brand} {self.model} — {price_str} ₽"

    # Классовый метод: получает cls — сам класс. Альтернативный конструктор.
    @classmethod
    def from_string(cls, data):
        brand, model, price = cls.parse(data)
        return cls(brand, model, price)  # cls(...) вместо Car(...) — см. ниже

    # Статический метод: ни self, ни cls. Просто утилита разбора строки.
    @staticmethod
    def parse(data):
        brand, model, price = (part.strip() for part in data.split(";"))
        return brand, model, int(price)


class ElectricCar(Car):
    pass


car = Car.from_string("Toyota;Camry;2500000")
print(type(car).__name__, "→", car.info())

# Благодаря cls метод корректно работает и в наследниках:
# создаётся объект именно ElectricCar, а не Car.
tesla = ElectricCar.from_string("Tesla; Model 3; 4200000")
print(type(tesla).__name__, "→", tesla.info())

print("Утилита parse:", Car.parse("Kia;Rio;1800000"))

# Когда что использовать:
# - Обычный метод (self) — когда нужны данные конкретного объекта:
#   вывести информацию об автомобиле, изменить его цену.
# - @classmethod (cls) — когда нужен сам класс: альтернативные конструкторы
#   (from_string, from_dict, from_json), работа с классовыми атрибутами
#   (например, общим счётчиком). Из-за cls корректно работает в наследниках.
# - @staticmethod — когда функция по смыслу относится к классу, но не
#   использует ни объект, ни класс: проверки, преобразования, утилиты.
