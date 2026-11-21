"""
Сервис уведомлений.

Демонстрирует:
- Observer (глава 26) — управление подписчиками
- DIP (глава 40) — зависимость от абстракции Notifier
"""

from ..interfaces import Notifier


class NotificationService:
    """
    Управляет подписчиками и уведомляет их.

    Издатель в паттерне Observer. Не знает конкретных классов
    подписчиков: важно только, что у них есть метод update().
    """

    def __init__(self):
        self._subscribers: list = []

    def subscribe(self, observer) -> None:
        """Подписывает наблюдателя."""
        if observer not in self._subscribers:
            self._subscribers.append(observer)

    def unsubscribe(self, observer) -> None:
        """Отписывает наблюдателя."""
        if observer in self._subscribers:
            self._subscribers.remove(observer)

    def notify(self, event) -> None:
        """
        Уведомляет всех подписчиков.

        Итерируется по копии списка — это защита от изменения
        списка во время обхода.
        """
        for observer in list(self._subscribers):
            observer.update(event)

    def count(self) -> int:
        """Количество подписчиков."""
        return len(self._subscribers)


class EmailNotifier(Notifier):
    """Уведомитель через электронную почту."""

    def send(self, message: str) -> None:
        """Отправляет сообщение (печатает)."""
        print(f"[Email] {message}")


class SmsNotifier(Notifier):
    """Уведомитель через SMS."""

    def send(self, message: str) -> None:
        """Отправляет сообщение (печатает)."""
        print(f"[SMS] {message}")
