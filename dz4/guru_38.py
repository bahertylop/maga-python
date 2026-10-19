"""
Задача 38 (паттерн Decorator). В автосалоне есть базовый класс AutoItem с
методом get_info(). Нужно добавлять к автомобилю дополнительную информацию —
например, «премиум-комплектация», «зимний пакет», «гарантия 5 лет». При этом
нельзя менять сам класс AutoItem. Реализуйте паттерн «Декоратор»: класс
ItemDecorator, который содержит объект AutoItem внутри себя и имеет тот же
метод get_info(), но добавляет к результату дополнительный текст. Создайте
декораторы PremiumDecorator и WinterPackageDecorator, которые можно
комбинировать: PremiumDecorator(WinterPackageDecorator(car)).
Продемонстрируйте работу, а также покажите, что смена порядка декораторов
меняет порядок меток в выводе. Объясните, чем паттерн «Декоратор» отличается
от наследования и почему он удобнее, когда нужно много комбинаций украшений
(иначе пришлось бы создавать 2^n подклассов).
"""


def rub(value):
    return f"{value:,} ₽".replace(",", " ")


class AutoItem:
    """Базовый класс — его не меняем."""

    def __init__(self, name, price):
        self.name = name
        self.price = price

    def get_info(self):
        return self.name

    def get_price(self):
        return self.price


class ItemDecorator(AutoItem):
    """Базовый декоратор: тот же интерфейс, что у AutoItem,
    но всю работу делегирует обёрнутому объекту."""

    label = ""
    extra_price = 0

    def __init__(self, item):
        # Не вызываем AutoItem.__init__: своих данных у декоратора нет,
        # он только хранит ссылку на обёрнутый объект.
        self._item = item

    def get_info(self):
        return f"{self._item.get_info()} + {self.label}"

    def get_price(self):
        return self._item.get_price() + self.extra_price


class PremiumDecorator(ItemDecorator):
    label = "премиум-комплектация"
    extra_price = 400_000


class WinterPackageDecorator(ItemDecorator):
    label = "зимний пакет"
    extra_price = 60_000


class WarrantyDecorator(ItemDecorator):
    label = "гарантия 5 лет"
    extra_price = 90_000


def show(item):
    print(f"  {item.get_info()}\n    цена: {rub(item.get_price())}")


car = AutoItem("Toyota Camry", 2_500_000)

print("Без декораторов:")
show(car)

print("PremiumDecorator(WinterPackageDecorator(car)):")
show(PremiumDecorator(WinterPackageDecorator(car)))

print("WinterPackageDecorator(PremiumDecorator(car)) — порядок меток другой:")
show(WinterPackageDecorator(PremiumDecorator(car)))

print("Все три опции:")
full = WarrantyDecorator(PremiumDecorator(WinterPackageDecorator(car)))
show(full)

print("Исходный car не изменился:", car.get_info(), "|", rub(car.get_price()))
print("Декоратор подходит везде, где ждут AutoItem:", isinstance(full, AutoItem))

# Как это выглядело бы через наследование:
#   class PremiumCar(Car), class WinterCar(Car), class WarrantyCar(Car),
#   class PremiumWinterCar(Car), class PremiumWarrantyCar(Car),
#   class WinterWarrantyCar(Car), class PremiumWinterWarrantyCar(Car)...
# Для n опций нужно 2^n классов (каждая опция есть или нет):
for n in (3, 5, 10):
    print(f"  опций: {n:>2} → подклассов при наследовании: {2 ** n:>4}, декораторов: {n}")

# Чем «Декоратор» отличается от наследования:
# - наследование добавляет поведение СТАТИЧЕСКИ, на этапе написания кода:
#   набор возможностей зашит в класс навсегда;
# - декоратор добавляет поведение ДИНАМИЧЕСКИ, во время работы программы:
#   объект «оборачивается» в другой объект с тем же интерфейсом. Обёртки
#   можно вкладывать друг в друга в любом порядке и количестве, а исходный
#   объект остаётся нетронутым;
# - декоратор основан на композиции (хранит self._item) и делегировании,
#   а от AutoItem наследуется только ради общего интерфейса — чтобы
#   украшенный объект подходил везде, где ожидается AutoItem.
#
# Почему удобнее при множестве комбинаций: каждая опция — один маленький
# класс. Новая опция — +1 класс, а не удвоение количества классов. Любая
# комбинация собирается «на лету»: PremiumDecorator(WarrantyDecorator(car)).
#
# Обратите внимание: паттерн «Декоратор» и синтаксис @decorator в Python —
# родственные идеи (обернуть и расширить, не меняя исходное), но
# @decorator оборачивает функции и классы, а паттерн — объекты.
