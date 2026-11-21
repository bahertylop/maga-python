"""
Сервис отчётов.

Отвечает только за формирование отчётов (SRP, глава 27).
Не хранит данные, не оформляет сделки — только генерирует текст.
"""

from ..utils import CarUtils


class ReportService:
    """
    Формирует отчёты о работе автосалона.

    generate — отчёт по всем объектам хранилища.
    generate_sales_report — отчёт по сделкам.
    generate_stats — сводная статистика склада.
    """

    @staticmethod
    def _status(item) -> str:
        """Статус объекта: продан / в прокате / в продаже."""
        if getattr(item, "is_sold", False):
            return "продан"
        if getattr(item, "is_rented", False):
            return "в прокате"
        return "в продаже"

    def generate(self, storage, dealership_name: str) -> str:
        """
        Формирует общий отчёт по всем объектам.

        Возвращает многострочную строку: название автосалона,
        список объектов с их статусом.
        """
        lines = [f"Автосалон: {dealership_name}"]

        for item in storage.list_all():
            lines.append(f"  - {item.get_info()} [{self._status(item)}]")

        return "\n".join(lines)

    def generate_sales_report(self, deals: list) -> str:
        """
        Формирует отчёт по сделкам.

        Показывает количество сделок и суммарную комиссию.
        """
        if not deals:
            return "Сделок не было"

        total_commission = sum(deal["commission"] for deal in deals)
        total_revenue = sum(deal["item"].price for deal in deals)

        lines = [
            f"Всего сделок: {len(deals)}",
            f"Выручка: {CarUtils.format_price(total_revenue)}",
            f"Суммарная комиссия: {CarUtils.format_price(total_commission)}",
        ]

        for i, deal in enumerate(deals, start=1):
            lines.append(
                f"  {i}. {deal['item'].title} ({deal['item'].vin}) → "
                f"{deal['buyer']} "
                f"(комиссия: {CarUtils.format_price(deal['commission'])})"
            )

        return "\n".join(lines)

    def generate_stats(self, storage) -> str:
        """Сводка: количество по маркам, средняя цена, стоимость склада."""
        items = storage.list_all()
        if not items:
            return "Склад пуст"

        by_brand: dict = {}
        for item in items:
            by_brand[item.brand] = by_brand.get(item.brand, 0) + 1

        average = sum(i.price for i in items) / len(items)
        lines = [
            f"Всего единиц: {len(items)}",
            f"Средняя цена: {CarUtils.format_price(average)}",
            f"Стоимость склада: {CarUtils.format_price(storage.total_value())}",
            "По маркам: " + ", ".join(
                f"{brand} — {n}" for brand, n in sorted(by_brand.items())
            ),
        ]
        return "\n".join(lines)
