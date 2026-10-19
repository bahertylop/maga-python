"""
Задача 34 (паттерн Strategy + super()). В автосалоне есть разные способы
расчёта скидки: фиксированная (100 000 ₽), процентная (5% от цены) и
«трейд-ин» (для покупателей, сдающих старый автомобиль — 10% от цены).
Реализуйте паттерн «Стратегия»: базовый класс DiscountStrategy с методом
calculate(price), и три наследника — FixedDiscount, PercentDiscount,
TradeInDiscount. Каждый наследник переопределяет calculate. Дополнительно
используйте super() в классе TradeInDiscount, чтобы вызвать реализацию
PercentDiscount и увеличить процент скидки (или переиспользовать код
родителя). Продемонстрируйте работу всех трёх стратегий через единый
интерфейс. Объясните, что такое паттерн «Стратегия», зачем он нужен, как он
убирает длинные цепочки if/elif и как super() помогает переиспользовать код
родителя.
"""

from abc import ABC, abstractmethod


def rub(value):
    return f"{value:,.0f} ₽".replace(",", " ")


class DiscountStrategy(ABC):
    """Общий интерфейс всех стратегий скидки."""

    name = "Без названия"

    @abstractmethod
    def calculate(self, price):
        """Возвращает размер скидки в рублях."""


class NoDiscount(DiscountStrategy):
    name = "Без скидки"

    def calculate(self, price):
        return 0


class FixedDiscount(DiscountStrategy):
    name = "Фиксированная"

    def __init__(self, amount=100_000):
        self.amount = amount

    def calculate(self, price):
        return min(self.amount, price)  # скидка не больше цены


class PercentDiscount(DiscountStrategy):
    name = "Процентная"

    def __init__(self, percent=5):
        self.percent = percent

    def calculate(self, price):
        return price * self.percent / 100


class TradeInDiscount(PercentDiscount):
    name = "Трейд-ин"

    def __init__(self, old_car=None):
        # super() вызывает конструктор PercentDiscount — повышенный процент 10%
        super().__init__(percent=10)
        self.old_car = old_car

    def calculate(self, price):
        # Переиспользуем формулу процента из PercentDiscount через super(),
        # а не копируем её.
        return super().calculate(price)


class Order:
    """Контекст: использует стратегию, не зная, какая она именно."""

    def __init__(self, car, price, strategy=None):
        self.car = car
        self.price = price
        self.strategy = strategy or NoDiscount()

    def set_strategy(self, strategy):
        self.strategy = strategy  # стратегию можно сменить на лету

    def total(self):
        return self.price - self.strategy.calculate(self.price)

    def show(self):
        discount = self.strategy.calculate(self.price)
        print(f"{self.strategy.name:<14} | скидка {rub(discount):>11} | "
              f"к оплате {rub(self.total()):>12}")


order = Order("Toyota Camry", 2_500_000)
print(f"Автомобиль: {order.car}, цена {rub(order.price)}\n")

for strategy in (NoDiscount(), FixedDiscount(), PercentDiscount(),
                 TradeInDiscount(old_car="Kia Rio 2015")):
    order.set_strategy(strategy)
    order.show()

print("\nMRO TradeInDiscount:", [c.__name__ for c in TradeInDiscount.__mro__])


# ---------- Как было бы без паттерна ----------
def total_without_strategy(price, kind):
    if kind == "fixed":
        return price - 100_000
    elif kind == "percent":
        return price - price * 5 / 100
    elif kind == "tradein":
        return price - price * 10 / 100
    # ... новый вид скидки — новая ветка elif в этой функции
    return price


print("\nБез стратегии (if/elif):", rub(total_without_strategy(2_500_000, "tradein")))

# Что такое «Стратегия»:
# поведенческий паттерн: семейство взаимозаменяемых алгоритмов (здесь —
# способов расчёта скидки) выносится в отдельные классы с общим
# интерфейсом (calculate). Объект-контекст (Order) хранит ссылку на
# стратегию и просто вызывает её метод, не зная, какая это стратегия.
#
# Зачем нужен:
# - алгоритм можно выбрать или сменить во время работы (set_strategy) —
#   например, по карте лояльности или по акции дня;
# - каждую стратегию легко тестировать отдельно;
# - новый вид скидки (студенческая, корпоративная) добавляется новым
#   классом, без изменения Order и существующих скидок (принцип OCP).
#
# Как убирает if/elif: в функции total_without_strategy выбор алгоритма —
# цепочка условий, которая растёт с каждым новым видом скидки, и её надо
# править в каждом месте, где выбирается скидка. Со стратегией выбор
# происходит один раз — при создании объекта, а дальше работает
# полиморфизм: self.strategy.calculate(price) сам вызовет нужную версию.
#
# Как помогает super(): TradeInDiscount не дублирует формулу процента.
# super().__init__(percent=10) настраивает родителя с другим процентом,
# а super().calculate(price) использует его расчёт. Если формулу в
# PercentDiscount поправят (например, добавят округление до 1000 ₽),
# трейд-ин получит исправление автоматически.
