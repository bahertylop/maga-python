"""
Парсер аргументов командной строки.

Создаёт объект ArgumentParser с подкомандами.
Каждая подкоманда — отдельная операция автосалона.
"""

import argparse

VEHICLE_KINDS = ["car", "sedan", "suv", "motorcycle", "electric"]


def create_parser() -> argparse.ArgumentParser:
    """
    Создаёт парсер аргументов с десятью подкомандами.

    Возвращает объект ArgumentParser, готовый к разбору
    аргументов из sys.argv.
    """
    parser = argparse.ArgumentParser(
        prog="dealership",
        description="Система учёта автосалона",
    )
    parser.add_argument(
        "--db",
        default=None,
        help="Путь к файлу базы данных (по умолчанию из config.py)",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        help="Доступные команды",
    )

    # ─── add ───
    add_parser = subparsers.add_parser(
        "add", help="Добавить автомобиль или мотоцикл",
    )
    add_parser.add_argument("--vin", required=True, help="VIN (17 символов)")
    add_parser.add_argument("--brand", required=True, help="Марка")
    add_parser.add_argument("--model", required=True, help="Модель")
    add_parser.add_argument(
        "--price", type=int, required=True, help="Цена, ₽",
    )
    add_parser.add_argument(
        "--year", type=int, default=2024, help="Год выпуска",
    )
    add_parser.add_argument(
        "--mileage", type=int, default=0, help="Пробег, км",
    )
    add_parser.add_argument(
        "--type", default="car", choices=VEHICLE_KINDS, help="Тип",
    )
    add_parser.add_argument(
        "--engine",
        default=None,
        help='Двигатель в формате "вид:мощность:объём", например бензин:150:2.0',
    )
    add_parser.add_argument(
        "--set",
        dest="extras",
        action="append",
        default=[],
        metavar="КЛЮЧ=ЗНАЧЕНИЕ",
        help="Дополнительное поле типа: trunk_volume=480, drive=AWD, "
             "battery_kwh=75, engine_cc=900 (можно повторять)",
    )

    # ─── list ───
    subparsers.add_parser("list", help="Показать все объекты")

    # ─── find ───
    find_parser = subparsers.add_parser("find", help="Найти по VIN")
    find_parser.add_argument("--vin", required=True, help="VIN")

    # ─── sell ───
    sell_parser = subparsers.add_parser("sell", help="Продать")
    sell_parser.add_argument("--vin", required=True, help="VIN")
    sell_parser.add_argument("--buyer", required=True, help="Имя покупателя")

    # ─── rent ───
    rent_parser = subparsers.add_parser("rent", help="Выдать в прокат")
    rent_parser.add_argument("--vin", required=True, help="VIN")
    rent_parser.add_argument("--tenant", required=True, help="Имя арендатора")
    rent_parser.add_argument(
        "--days", type=int, required=True, help="Срок проката в сутках",
    )

    # ─── return ───
    return_parser = subparsers.add_parser(
        "return", help="Принять автомобиль из проката",
    )
    return_parser.add_argument("--vin", required=True, help="VIN")

    # ─── subscribe ───
    subscribe_parser = subparsers.add_parser(
        "subscribe", help="Подписать клиента на уведомления",
    )
    subscribe_parser.add_argument("--name", required=True, help="Имя клиента")
    subscribe_parser.add_argument(
        "--budget", type=int, default=0, help="Бюджет клиента, ₽",
    )

    # ─── report ───
    subparsers.add_parser("report", help="Сгенерировать отчёт")

    # ─── save ───
    subparsers.add_parser("save", help="Сохранить в БД")

    # ─── load ───
    subparsers.add_parser("load", help="Загрузить из БД")

    return parser
