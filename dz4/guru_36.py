"""
Задача 36 (объект как функция: __call__). В автосалоне есть служебный объект
CreditCalculator, который должен уметь рассчитывать ежемесячный платёж по
кредиту. Удобно, чтобы его можно было вызывать как функцию:
calculator(2500000, 5), а не calculator.calculate(2500000, 5). Реализуйте в
классе CreditCalculator магический метод __call__(self, price, years),
который возвращает примерный ежемесячный платёж (например,
price / (years * 12)). Продемонстрируйте, что объект можно вызывать как
функцию: calc = CreditCalculator(); calc(2500000, 5). Дополнительно покажите,
что такой объект можно передать туда, где ожидается функция-колбэк.
Объясните, зачем нужен __call__, чем он полезен (функторы, декораторы-классы,
колбэки с состоянием) и как он связан с понятием «функтор» в других языках.
"""

import functools


def rub(value):
    return f"{value:,.0f} ₽".replace(",", " ")


class CreditCalculator:
    def __init__(self, annual_rate=0.0):
        # Состояние объекта: ставка и счётчик расчётов.
        # Обычная функция такого «памятного» состояния не имеет.
        self.annual_rate = annual_rate
        self.calls = 0

    def __call__(self, price, years):
        self.calls += 1
        months = years * 12
        if self.annual_rate == 0:
            return price / months  # простой вариант из условия
        # Аннуитетный платёж — если задана процентная ставка
        r = self.annual_rate / 12
        return price * r / (1 - (1 + r) ** -months)


calc = CreditCalculator()
print("calc(2500000, 5) =", rub(calc(2_500_000, 5)))   # объект вызывается как функция
print("callable(calc):", callable(calc))

bank_calc = CreditCalculator(annual_rate=0.18)  # другой «экземпляр функции» с другой ставкой
print("Банк 18% годовых, 5 лет:", rub(bank_calc(2_500_000, 5)))


# ---------- Объект как колбэк ----------
def show_offers(cars, payment_func, years=5):
    """Ожидает «функцию» payment_func(price, years) — ей подойдёт и наш объект."""
    for name, price in cars:
        print(f"  {name:<14} {rub(price):>12} → {rub(payment_func(price, years))}/мес")


cars = [("Toyota Camry", 2_500_000), ("Kia Rio", 1_800_000), ("BMW X5", 9_000_000)]

print("\nКолбэк — обычная функция (lambda):")
show_offers(cars, lambda price, years: price / (years * 12))

print("Колбэк — объект с __call__ (18% годовых):")
show_offers(cars, bank_calc)
print("Сколько раз считал bank_calc:", bank_calc.calls)  # состояние сохранилось

print("\nВ map():", [rub(p) for p in map(calc, [1_000_000, 2_000_000], [5, 5])])


# ---------- Декоратор-класс на основе __call__ ----------
class CountCalls:
    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func = func
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        return self.func(*args, **kwargs)


@CountCalls
def get_price(model):
    return {"Camry": 2_500_000}.get(model, 0)


get_price("Camry")
get_price("Rio")
print(f"\nДекоратор-класс: {get_price.__name__}() вызвана {get_price.count} раза")

# Зачем нужен __call__:
# он делает объект «вызываемым»: calc(a, b) превращается в calc.__call__(a, b).
# Получается функция, у которой есть СОСТОЯНИЕ — поля объекта.
# Чем полезен:
# - функторы — «функции с настройками»: один класс, но разные объекты
#   с разной ставкой (calc, bank_calc), каждый со своей памятью;
# - колбэки с состоянием — объект можно отдать в map, sorted(key=...),
#   обработчик кнопки, планировщик; он посчитает вызовы, накопит данные,
#   закэширует результат — без глобальных переменных;
# - декораторы-классы (CountCalls) — хранят обёрнутую функцию и счётчики
#   в полях, а не во вложенных замыканиях;
# - в библиотеках: слои нейросетей PyTorch вызываются как layer(x),
#   валидаторы, стратегии, middleware в веб-фреймворках.
#
# Связь с «функтором» в других языках:
# в C++ функтором (function object) называют объект класса с перегруженным
# оператором (), который вызывается как функция и хранит состояние —
# __call__ в Python делает ровно то же. В Java похожую роль играют объекты,
# реализующие функциональный интерфейс (Function, Comparator).
# (В функциональном программировании «функтор» означает другое — тип,
# поддерживающий map, — это не то же самое.)
