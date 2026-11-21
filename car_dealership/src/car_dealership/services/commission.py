"""
Стратегии расчёта комиссии.

Паттерн Strategy (глава 34). Позволяет менять способ
расчёта комиссии без изменения сервиса сделок.
"""

from abc import ABC, abstractmethod


class CommissionStrategy(ABC):
    """
    Абстрактная стратегия расчёта комиссии.

    Наследники обязаны реализовать calculate.
    """

    @abstractmethod
    def calculate(self, price: int) -> float:
        """Рассчитывает комиссию от цены."""
        ...

    def __call__(self, price: int) -> float:
        """Стратегию можно вызывать как функцию (глава 36)."""
        return self.calculate(price)


class FixedCommission(CommissionStrategy):
    """Фиксированная комиссия."""

    def __init__(self, amount: int = 30_000):
        self.amount = amount

    def calculate(self, price: int) -> float:
        """Возвращает фиксированную сумму."""
        return self.amount


class PercentCommission(CommissionStrategy):
    """Процентная комиссия."""

    def __init__(self, rate: float = 0.05):
        self.rate = rate

    def calculate(self, price: int) -> float:
        """Возвращает процент от цены."""
        return price * self.rate


class LoyaltyCommission(PercentCommission):
    """
    Льготная комиссия для постоянных клиентов.

    Наследует логику процентной комиссии,
    но с уменьшенной ставкой.
    """

    def __init__(self):
        super().__init__(rate=0.025)
