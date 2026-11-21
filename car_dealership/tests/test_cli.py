"""
Тесты CLI: парсер, обработчики и запуск cli.py.
"""

import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

import cli as cli_module
from src.car_dealership.cli import Commands, create_parser
from tests.vins import VIN_1, VIN_2, VIN_3

ROOT = Path(__file__).resolve().parent.parent


def ns(**kwargs):
    """Быстро собирает объект args для обработчиков."""
    return SimpleNamespace(**kwargs)


def add_args(vin=VIN_1, **kw):
    base = dict(vin=vin, brand="Toyota", model="Camry", price=3_000_000,
                year=2023, mileage=1000, type="car", engine=None, extras=[])
    base.update(kw)
    return ns(**base)


@pytest.fixture
def commands():
    """Commands без БД: всё в памяти."""
    return Commands(db_path=":memory:", autosave=False)


# ─── парсер ───

def test_parser_add_defaults():
    args = create_parser().parse_args(
        ["add", "--vin", VIN_1, "--brand", "A", "--model", "b", "--price", "5"])
    assert args.command == "add"
    assert args.type == "car" and args.year == 2024 and args.mileage == 0
    assert args.extras == [] and args.price == 5


def test_parser_add_extras_repeat():
    args = create_parser().parse_args(
        ["add", "--vin", VIN_1, "--brand", "A", "--model", "b", "--price", "5",
         "--set", "a=1", "--set", "b=2"])
    assert args.extras == ["a=1", "b=2"]


def test_parser_global_db_option():
    args = create_parser().parse_args(["--db", "x.db", "list"])
    assert args.db == "x.db" and args.command == "list"


@pytest.mark.parametrize("argv", [
    ["add", "--vin", VIN_1],
    ["sell", "--vin", VIN_1],
    ["rent", "--vin", VIN_1, "--tenant", "x"],
    ["add", "--vin", VIN_1, "--brand", "A", "--model", "b", "--price", "x"],
    ["add", "--vin", VIN_1, "--brand", "A", "--model", "b", "--price", "1",
     "--type", "rocket"],
    ["unknown"],
])
def test_parser_rejects_bad_input(argv):
    with pytest.raises(SystemExit):
        create_parser().parse_args(argv)


@pytest.mark.parametrize("command", [
    "add", "list", "find", "sell", "rent", "return", "subscribe",
    "report", "save", "load",
])
def test_every_command_has_handler(command):
    assert hasattr(Commands, f"cmd_{command}")


def test_parser_no_command():
    assert create_parser().parse_args([]).command is None


# ─── обработчики ───

def test_cmd_add_and_list(commands, capsys):
    assert commands.cmd_add(add_args()) is True
    assert len(commands.storage) == 1
    commands.cmd_list(ns())
    out = capsys.readouterr().out
    assert "Добавлено" in out and "Всего объектов: 1" in out


def test_cmd_list_empty(commands, capsys):
    commands.cmd_list(ns())
    assert "Хранилище пусто" in capsys.readouterr().out


def test_cmd_add_with_extras_and_engine(commands):
    args = add_args(type="sedan", extras=["trunk_volume=480"],
                    engine="бензин:150:2.0")
    assert commands.cmd_add(args) is True
    item = commands.storage.find_by_vin(VIN_1)
    assert item.trunk_volume == 480
    assert item.engine.power_hp == 150 and item.engine.volume_l == 2.0


@pytest.mark.parametrize("kwargs", [
    dict(vin="bad"),
    dict(price=-5),
    dict(type="sedan", extras=["wheels=4"]),
    dict(extras=["без_равно"]),
    dict(engine="только_вид"),
])
def test_cmd_add_errors_are_reported(commands, capsys, kwargs):
    assert commands.cmd_add(add_args(**kwargs)) is False
    assert "✗ Ошибка" in capsys.readouterr().out
    assert len(commands.storage) == 0


def test_cmd_add_duplicate(commands, capsys):
    commands.cmd_add(add_args())
    assert commands.cmd_add(add_args()) is False
    assert "уже добавлен" in capsys.readouterr().out


def test_cmd_find(commands, capsys):
    commands.cmd_add(add_args())
    assert commands.cmd_find(ns(vin=VIN_1)) is True
    assert commands.cmd_find(ns(vin=VIN_2)) is False
    out = capsys.readouterr().out
    assert "Найдено" in out and "не найден" in out


def test_cmd_sell(commands, capsys):
    commands.cmd_add(add_args())
    assert commands.cmd_sell(ns(vin=VIN_1, buyer="Петров")) is True
    assert "Комиссия: 150 000 ₽" in capsys.readouterr().out
    assert commands.cmd_sell(ns(vin=VIN_1, buyer="Иванов")) is False
    assert "уже продан" in capsys.readouterr().out


def test_cmd_rent_and_return(commands, capsys):
    commands.cmd_add(add_args())
    assert commands.cmd_rent(ns(vin=VIN_1, tenant="Иванов", days=2)) is True
    assert commands.cmd_rent(ns(vin=VIN_1, tenant="Петров", days=1)) is False
    assert commands.cmd_return(ns(vin=VIN_1)) is True
    assert commands.cmd_rent(ns(vin=VIN_1, tenant="Петров", days=1)) is True
    out = capsys.readouterr().out
    assert "сейчас в прокате" in out and "Принято из проката" in out


def test_cmd_rent_motorcycle_error(commands, capsys):
    commands.cmd_add(add_args(vin=VIN_3, type="motorcycle"))
    assert commands.cmd_rent(ns(vin=VIN_3, tenant="x", days=1)) is False
    assert "не выдаётся в прокат" in capsys.readouterr().out


def test_cmd_subscribe_and_notify_on_sale(commands, capsys):
    commands.cmd_subscribe(ns(name="Иван", budget=4_000_000))
    commands.cmd_add(add_args())
    commands.cmd_sell(ns(vin=VIN_1, buyer="Петров"))
    assert commands.notifier.count() == 1
    assert "Иван: Продан Toyota Camry" in commands.clients[0].notifications[0]


def test_cmd_report(commands, capsys):
    commands.cmd_add(add_args())
    commands.cmd_sell(ns(vin=VIN_1, buyer="Петров"))
    capsys.readouterr()
    commands.cmd_report(ns())
    out = capsys.readouterr().out
    assert "Автосалон: АвтоМир" in out and "Всего сделок: 1" in out


def test_cmd_save_empty(commands, capsys):
    assert commands.cmd_save(ns()) is True
    assert "Нечего сохранять" in capsys.readouterr().out


def test_save_then_load_in_new_session(sample_db_path, capsys):
    first = Commands(db_path=sample_db_path)
    first.cmd_add(add_args())
    first.cmd_add(add_args(vin=VIN_2, type="electric",
                           extras=["battery_kwh=80"]))
    first.cmd_sell(ns(vin=VIN_1, buyer="Петров"))
    first.cmd_save(ns())

    second = Commands(db_path=sample_db_path)
    assert second.cmd_load(ns()) is True
    assert len(second.storage) == 2
    assert second.storage.find_by_vin(VIN_1).is_sold is True
    assert second.storage.find_by_vin(VIN_2).battery_kwh == 80
    assert second.cmd_load(ns()) is True          # повторная загрузка
    assert len(second.storage) == 2               # дубликатов нет
    assert "Загружено новых объектов: 0" in capsys.readouterr().out


def test_load_from_missing_db_is_empty(sample_db_path, capsys):
    commands = Commands(db_path=sample_db_path)
    assert commands.cmd_load(ns()) is True
    assert len(commands.storage) == 0


def test_autosave_persists_between_sessions(sample_db_path):
    one = Commands(db_path=sample_db_path, autosave=True)
    one.cmd_add(add_args())
    one.cmd_subscribe(ns(name="Иван", budget=1))
    one.cmd_rent(ns(vin=VIN_1, tenant="x", days=1))

    two = Commands(db_path=sample_db_path, autosave=True)
    assert len(two.storage) == 1
    assert two.storage.find_by_vin(VIN_1).is_rented is True
    assert [c.name for c in two.clients] == ["Иван"]
    assert two.notifier.count() == 1

    two.cmd_return(ns(vin=VIN_1))
    two.cmd_sell(ns(vin=VIN_1, buyer="Петров"))
    three = Commands(db_path=sample_db_path, autosave=True)
    assert three.storage.find_by_vin(VIN_1).is_sold is True


def test_autosave_report_uses_saved_deals(sample_db_path, capsys):
    Commands(db_path=sample_db_path, autosave=True).cmd_add(add_args())
    sell = Commands(db_path=sample_db_path, autosave=True)
    sell.cmd_sell(ns(vin=VIN_1, buyer="Петров"))
    capsys.readouterr()
    fresh = Commands(db_path=sample_db_path, autosave=True)
    fresh.cmd_report(ns())
    assert "Всего сделок: 1" in capsys.readouterr().out


# ─── cli.py как программа ───

def test_main_function_exit_codes(sample_db_path, capsys):
    base = ["--db", sample_db_path]
    add = ["add", "--vin", VIN_1, "--brand", "A", "--model", "b", "--price", "10"]
    assert cli_module.main(base + add) == 0
    assert cli_module.main(base + add) == 1          # дубликат
    assert cli_module.main(base + ["list"]) == 0
    assert cli_module.main([]) == 0                  # справка


def test_cli_py_end_to_end(sample_db_path):
    def run(*argv):
        return subprocess.run(
            [sys.executable, str(ROOT / "cli.py"), "--db", sample_db_path, *argv],
            capture_output=True, text=True, encoding="utf-8", cwd=ROOT,
        )

    assert run("add", "--vin", VIN_1, "--brand", "Kia", "--model", "Rio",
               "--price", "1000000").returncode == 0
    listing = run("list")
    assert listing.returncode == 0 and "Kia Rio" in listing.stdout
    bad = run("sell", "--vin", VIN_2, "--buyer", "x")
    assert bad.returncode == 1 and "не найден" in bad.stdout
    assert run("sell", "--vin", VIN_1, "--buyer", "Иванов").returncode == 0
    assert "Всего сделок: 1" in run("report").stdout
