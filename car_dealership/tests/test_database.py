"""
Тесты базы данных: менеджер и репозитории.
"""

import sqlite3

import pytest

from src.car_dealership.database import (
    CarRepository, ClientRepository, DatabaseManager, DealRepository,
)
from src.car_dealership.exceptions import DatabaseError, DealershipError
from src.car_dealership.models import (
    Car, Client, ElectricCar, Engine, Manager, Motorcycle, SUV, Sedan,
)
from tests.vins import VIN_1, VIN_2, VIN_3, VIN_4, VIN_5


def test_with_creates_file_and_tables(sample_db_path):
    with DatabaseManager(sample_db_path):
        pass
    con = sqlite3.connect(sample_db_path)
    tables = {r[0] for r in con.execute(
        "SELECT name FROM sqlite_master WHERE type='table'")}
    con.close()
    assert {"cars", "clients", "managers", "deals"} <= tables


def test_connection_closed_after_with(sample_db_path):
    with DatabaseManager(sample_db_path) as db:
        assert db._connection is not None
    assert db._connection is None


def test_connection_closed_on_exception(sample_db_path):
    with pytest.raises(RuntimeError):
        with DatabaseManager(sample_db_path) as db:
            raise RuntimeError("boom")
    assert db._connection is None


def test_creates_missing_directory(tmp_path):
    path = tmp_path / "nested" / "dir" / "x.db"
    with DatabaseManager(str(path)):
        pass
    assert path.exists()


def test_use_without_connection():
    with pytest.raises(DatabaseError):
        DatabaseManager("x.db").find_all_cars()


def test_save_and_find_car(sample_db_path, sample_car):
    with DatabaseManager(sample_db_path) as db:
        car_id = db.save_car(sample_car)
        row = db.find_car(VIN_1)
    assert row["id"] == car_id
    assert row["brand"] == "Toyota" and row["price"] == 3_000_000


def test_find_missing_returns_none(sample_db_path):
    with DatabaseManager(sample_db_path) as db:
        assert db.find_car(VIN_4) is None
        assert db.find_car_id(VIN_4) is None


def test_save_same_vin_updates(sample_db_path, sample_car):
    with DatabaseManager(sample_db_path) as db:
        first = db.save_car(sample_car)
        sample_car.price = 2_800_000
        sample_car.sell()
        second = db.save_car(sample_car)
        assert first == second
        assert len(db.find_all_cars()) == 1
        row = db.find_car(VIN_1)
    assert row["price"] == 2_800_000 and row["is_sold"] == 1


def test_delete_car(sample_db_path, sample_car):
    with DatabaseManager(sample_db_path) as db:
        db.save_car(sample_car)
        assert db.delete_car(VIN_1) is True
        assert db.delete_car(VIN_1) is False


def test_data_survives_reopening(sample_db_path, sample_car):
    with DatabaseManager(sample_db_path) as db:
        db.save_car(sample_car)
    with DatabaseManager(sample_db_path) as db:
        assert db.find_car(VIN_1) is not None


# ─── репозиторий автомобилей ───

def test_repository_roundtrip_each_type(sample_db_path):
    items = [
        Car(VIN_1, "Toyota", "Camry", 3_000_000, 2022, 9000,
            Engine("бензин", 181, 2.5)),
        Sedan(VIN_2, "Kia", "K5", 2_500_000, trunk_volume=510),
        SUV(VIN_3, "Lada", "Niva", 1_200_000, drive="AWD"),
        Motorcycle(VIN_4, "BMW", "R", 1_900_000, engine_cc=1250),
        ElectricCar(VIN_5, "Tesla", "3", 5_000_000, battery_kwh=75),
    ]
    with DatabaseManager(sample_db_path) as db:
        repo = CarRepository(db)
        for item in items:
            repo.save(item)
        loaded = repo.find_all()
    assert loaded == items
    assert [type(i) for i in loaded] == [type(i) for i in items]


def test_repository_restores_flags(sample_db_path, sample_car):
    sample_car.sell()
    sample_car.is_rented = True
    with DatabaseManager(sample_db_path) as db:
        repo = CarRepository(db)
        repo.save(sample_car)
        loaded = repo.find_by_vin(VIN_1)
    assert loaded.is_sold is True and loaded.is_rented is True


def test_repository_find_missing(sample_db_path):
    with DatabaseManager(sample_db_path) as db:
        assert CarRepository(db).find_by_vin(VIN_4) is None


def test_repository_delete(sample_db_path, sample_car):
    with DatabaseManager(sample_db_path) as db:
        repo = CarRepository(db)
        repo.save(sample_car)
        assert repo.delete(VIN_1) is True
        assert repo.find_all() == []


def test_repository_unknown_type_in_db(sample_db_path, sample_car):
    with DatabaseManager(sample_db_path) as db:
        db.save_car(sample_car)
        db._connection.execute("UPDATE cars SET type = 'Spaceship'")
        db._connection.commit()
        with pytest.raises(DatabaseError):
            CarRepository(db).find_all()


# ─── клиенты, менеджеры, сделки ───

def test_client_repository(sample_db_path):
    with DatabaseManager(sample_db_path) as db:
        repo = ClientRepository(db)
        repo.save(Client("Иван", 1_000_000))
        repo.save(Client("Иван", 2_000_000))  # обновит бюджет
        repo.save(Client("Ольга", 500_000))
        clients = repo.find_all()
    assert [(c.name, c.budget) for c in clients] == [
        ("Иван", 2_000_000), ("Ольга", 500_000)]


def test_save_manager(sample_db_path):
    with DatabaseManager(sample_db_path) as db:
        assert db.save_manager(Manager("Ольга", 5)) == 1


def test_deal_repository(sample_db_path, sample_car):
    with DatabaseManager(sample_db_path) as db:
        db.save_car(sample_car)
        repo = DealRepository(db)
        repo.save_deal_for(sample_car, "Петров", 150_000)
        deals = repo.find_all()
    assert len(deals) == 1
    assert deals[0]["buyer"] == "Петров"
    assert deals[0]["vin"] == VIN_1
    assert deals[0]["commission"] == 150_000


def test_deal_for_unknown_car(sample_db_path, sample_car):
    with DatabaseManager(sample_db_path) as db:
        with pytest.raises(DatabaseError):
            DealRepository(db).save_deal_for(sample_car, "x", 0)


def test_foreign_key_protects_cars_with_deals(sample_db_path, sample_car):
    with DatabaseManager(sample_db_path) as db:
        db.save_car(sample_car)
        DealRepository(db).save_deal_for(sample_car, "x", 0)
        with pytest.raises(DatabaseError):
            db.delete_car(VIN_1)
        assert db.find_car(VIN_1) is not None  # после отката запись цела


def test_database_error_is_dealership_error():
    assert issubclass(DatabaseError, DealershipError)
