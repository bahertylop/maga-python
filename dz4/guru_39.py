"""
Задача 39 (паттерн Adapter). В автосалоне появилась внешняя система
аукциона, которая возвращает данные об автомобилях в другом формате —
например, в виде словаря {"make": "Toyota", "model": "Camry", "cost":
2500000}. А весь остальной код автосалона работает с классом Car, у которого
поля brand, model, price. Реализуйте паттерн «Адаптер»: класс CarAdapter,
который принимает словарь и предоставляет интерфейс Car — свойства brand,
model, price и метод info(). Продемонстрируйте, что адаптер можно
использовать там, где ожидается Car — например, передать его в функцию,
которая работает с автомобилем. Объясните, что такое паттерн «Адаптер», зачем
он нужен, чем отличается от Facade и Decorator, и как он помогает
интегрировать несовместимые интерфейсы без изменения существующего кода.
"""


# ---------- Существующий код автосалона (не меняем) ----------
class Car:
    def __init__(self, brand, model, price):
        self.brand = brand
        self.model = model
        self.price = price

    def info(self):
        price_str = f"{self.price:,}".replace(",", " ")
        return f"{self.brand} {self.model}, {price_str} ₽"


def print_price_tag(car):
    """Функция автосалона: работает с любым объектом с интерфейсом Car."""
    print(f"  🏷  {car.info()}")


def total_price(cars):
    return sum(car.price for car in cars)


# ---------- Внешняя система аукциона (её тоже нельзя менять) ----------
class AuctionAPI:
    def get_lots(self):
        return [
            {"make": "Toyota", "model": "Camry", "cost": 2500000},
            {"make": "BMW", "model": "X5", "cost": 7800000},
        ]


# ---------- Адаптер ----------
class CarAdapter(Car):
    """Оборачивает словарь аукциона и выдаёт интерфейс Car.
    Наследование от Car — только ради «паспорта»: isinstance(x, Car) и
    метода info(); данные адаптер берёт из словаря."""

    def __init__(self, auction_data):
        self._data = auction_data  # своих копий полей не храним

    @property
    def brand(self):
        return self._data["make"]       # make → brand

    @property
    def model(self):
        return self._data["model"]      # model → model (совпадает)

    @property
    def price(self):
        return self._data["cost"]       # cost → price

    # info() унаследован от Car и работает через свойства brand/model/price


salon_cars = [Car("Kia", "Rio", 1_800_000)]
auction_cars = [CarAdapter(lot) for lot in AuctionAPI().get_lots()]

print("Ценники (свои машины и машины с аукциона — один и тот же код):")
for car in salon_cars + auction_cars:
    print_price_tag(car)

print(f"Сумма всех цен: {total_price(salon_cars + auction_cars):,} ₽".replace(",", " "))
adapter = auction_cars[0]
print("adapter.brand:", adapter.brand, "| isinstance(adapter, Car):", isinstance(adapter, Car))

# Попытка передать словарь напрямую — несовместимые интерфейсы:
try:
    print_price_tag(AuctionAPI().get_lots()[0])
except AttributeError as e:
    print("Словарь без адаптера:", e)

# Что такое «Адаптер»:
# структурный паттерн, который превращает интерфейс одного объекта в
# интерфейс, ожидаемый клиентом. Как переходник для розетки: вилка и
# розетка не меняются, между ними ставится переходник.
# Здесь «розетка» — интерфейс Car (brand, model, price, info), «вилка» —
# словарь аукциона (make, model, cost), переходник — CarAdapter.
#
# Зачем нужен:
# - подключить внешнюю библиотеку, API, старый модуль, которые нельзя
#   или не хочется менять;
# - не переписывать десятки функций автосалона под новый формат —
#   они продолжают работать с привычным интерфейсом Car;
# - вся «переводческая» логика собрана в одном месте: если аукцион
#   переименует cost в price_rub, поправим только адаптер.
#
# Отличия от похожих паттернов:
# - Adapter МЕНЯЕТ интерфейс: был «словарь с make/cost», стал «Car с
#   brand/price». Функциональность та же.
# - Decorator (задача 38) интерфейс СОХРАНЯЕТ, но ДОБАВЛЯЕТ поведение:
#   был AutoItem — остался AutoItem, только с «премиум-комплектацией».
# - Facade УПРОЩАЕТ: даёт один простой интерфейс к целой сложной
#   подсистеме из многих классов (например, метод buy_car(), который сам
#   проверит кредит, оформит договор, выпишет счёт и поставит на учёт).
#   Адаптер обычно оборачивает один объект, фасад — много.
#
# Как помогает без изменения кода: ни класс Car, ни функции
# print_price_tag и total_price, ни AuctionAPI не изменились —
# добавлен только новый класс-переходник. Это соответствует принципу
# открытости/закрытости (OCP, задача 35).
