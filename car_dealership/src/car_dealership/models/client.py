"""
Клиент и менеджер.

Демонстрируют:
- утиную типизацию (глава 30): у обоих есть describe()
- Observer (глава 26): у Client есть update()
"""

from ..utils import CarUtils


class Client:
    """Клиент автосалона. Подписывается на уведомления."""

    def __init__(self, name: str, budget: int = 0):
        self.name = name
        self.budget = budget
        self.notifications: list = []

    def describe(self) -> str:
        """Описание клиента."""
        return f"Клиент {self.name}, бюджет {CarUtils.format_price(self.budget)}"

    def can_afford(self, price) -> bool:
        """Хватает ли бюджета на покупку."""
        return self.budget >= price

    def update(self, event) -> None:
        """Реакция на уведомление (Observer, глава 26)."""
        message = f"{self.name}: {event}"
        self.notifications.append(message)
        print(f"  → {message}")

    def __repr__(self) -> str:
        return f"Client({self.name!r}, {self.budget})"


class Manager:
    """Менеджер по продажам."""

    def __init__(self, name: str, experience: int):
        self.name = name
        self.experience = experience

    def describe(self) -> str:
        """Описание менеджера."""
        return f"Менеджер {self.name}, стаж {self.experience} лет"

    @property
    def bonus_rate(self) -> float:
        """Бонус к комиссии: 1% за каждые 2 года стажа, не больше 5%."""
        return min(0.05, (self.experience // 2) * 0.01)

    def __repr__(self) -> str:
        return f"Manager({self.name!r}, {self.experience})"
