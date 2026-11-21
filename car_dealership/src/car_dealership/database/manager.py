"""
Управление базой данных SQLite.

Класс DatabaseManager открывает соединение, создаёт таблицы,
выполняет запросы и закрывает соединение. Реализует
контекстный менеджер (глава 33), поэтому работает с with.
"""

import json
import sqlite3
from pathlib import Path

from ..exceptions import DatabaseError

# Поля автомобиля, у которых есть собственные столбцы в таблице cars.
# Всё остальное (двигатель, объём багажника, привод...) хранится в
# столбце extra в виде JSON — так одна таблица обслуживает все типы.
CAR_COLUMNS = (
    "vin", "brand", "model", "year", "price", "mileage",
    "is_sold", "is_rented", "type",
)


class DatabaseManager:
    """
    Управление соединением с базой данных.

    Открывает соединение, создаёт таблицы, выполняет запросы.
    Используется как контекстный менеджер:

        with DatabaseManager("dealership.db") as db:
            db.save_car(car)
    """

    def __init__(self, db_path: str = "data/dealership.db"):
        self.db_path = db_path
        self._connection = None

    def connect(self) -> None:
        """Открывает соединение с базой данных."""
        try:
            if self.db_path != ":memory:":
                Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            self._connection = sqlite3.connect(self.db_path)
            self._connection.row_factory = sqlite3.Row
            self._connection.execute("PRAGMA foreign_keys = ON")
        except (sqlite3.Error, OSError) as e:
            raise DatabaseError(f"Не удалось открыть БД: {e}")

    def close(self) -> None:
        """Закрывает соединение."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def create_tables(self) -> None:
        """Создаёт таблицы из SQL-схемы."""
        schema_path = Path(__file__).parent / "schema.sql"
        with open(schema_path, encoding="utf-8") as f:
            schema = f.read()

        try:
            self._connection.executescript(schema)
            self._connection.commit()
        except sqlite3.Error as e:
            raise DatabaseError(f"Не удалось создать таблицы: {e}")

    def _run(self, sql: str, params: tuple = (), error: str = "Ошибка БД"):
        """Выполняет запрос и фиксирует изменения; ошибки превращает в DatabaseError."""
        if self._connection is None:
            raise DatabaseError("Соединение не открыто")
        try:
            cursor = self._connection.execute(sql, params)
            self._connection.commit()
            return cursor
        except sqlite3.Error as e:
            self._connection.rollback()
            raise DatabaseError(f"{error}: {e}")

    # ─── автомобили ───

    def save_car(self, car) -> int:
        """
        Сохраняет транспортное средство.

        Возвращает id записи. Если VIN уже есть,
        обновляет существующую запись.
        """
        data = car.to_dict()
        core = {key: data[key] for key in CAR_COLUMNS}
        extra = {k: v for k, v in data.items() if k not in CAR_COLUMNS}
        self._run(
            """
            INSERT INTO cars
                (vin, brand, model, year, price, mileage,
                 is_sold, is_rented, type, extra)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(vin) DO UPDATE SET
                brand = excluded.brand,
                model = excluded.model,
                year = excluded.year,
                price = excluded.price,
                mileage = excluded.mileage,
                is_sold = excluded.is_sold,
                is_rented = excluded.is_rented,
                type = excluded.type,
                extra = excluded.extra
            """,
            (
                core["vin"], core["brand"], core["model"], core["year"],
                core["price"], core["mileage"], int(core["is_sold"]),
                int(core["is_rented"]), core["type"],
                json.dumps(extra, ensure_ascii=False),
            ),
            "Не удалось сохранить автомобиль",
        )
        return self.find_car_id(core["vin"])

    def find_car(self, vin: str):
        """Находит автомобиль по VIN. Возвращает строку или None."""
        return self._run(
            "SELECT * FROM cars WHERE vin = ?", (vin,), "Ошибка поиска"
        ).fetchone()

    def find_car_id(self, vin: str):
        """Возвращает id автомобиля по VIN или None."""
        row = self.find_car(vin)
        return None if row is None else row["id"]

    def find_all_cars(self) -> list:
        """Возвращает все автомобили."""
        return self._run(
            "SELECT * FROM cars ORDER BY id", error="Ошибка чтения"
        ).fetchall()

    def delete_car(self, vin: str) -> bool:
        """Удаляет автомобиль по VIN. Возвращает True, если удалено."""
        cursor = self._run(
            "DELETE FROM cars WHERE vin = ?", (vin,), "Ошибка удаления"
        )
        return cursor.rowcount > 0

    # ─── клиенты и менеджеры ───

    def save_client(self, client) -> int:
        """Сохраняет клиента (если имя уже есть — обновляет бюджет)."""
        self._run(
            """
            INSERT INTO clients (name, budget) VALUES (?, ?)
            ON CONFLICT(name) DO UPDATE SET budget = excluded.budget
            """,
            (client.name, client.budget),
            "Не удалось сохранить клиента",
        )
        return self._run(
            "SELECT id FROM clients WHERE name = ?", (client.name,)
        ).fetchone()["id"]

    def find_all_clients(self) -> list:
        """Возвращает всех клиентов."""
        return self._run(
            "SELECT * FROM clients ORDER BY id", error="Ошибка чтения"
        ).fetchall()

    def save_manager(self, manager) -> int:
        """Сохраняет менеджера."""
        cursor = self._run(
            "INSERT INTO managers (name, experience) VALUES (?, ?)",
            (manager.name, manager.experience),
            "Не удалось сохранить менеджера",
        )
        return cursor.lastrowid

    # ─── сделки ───

    def save_deal(self, deal: dict) -> int:
        """
        Сохраняет сделку.

        deal — словарь с полями car_id, client_id, manager_id,
        buyer, commission, date.
        """
        cursor = self._run(
            """
            INSERT INTO deals
                (car_id, client_id, manager_id, buyer, commission, date)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                deal["car_id"],
                deal.get("client_id"),
                deal.get("manager_id"),
                deal.get("buyer"),
                deal.get("commission", 0),
                deal["date"],
            ),
            "Не удалось сохранить сделку",
        )
        return cursor.lastrowid

    def find_all_deals(self) -> list:
        """Возвращает сделки вместе с VIN проданного автомобиля."""
        return self._run(
            """
            SELECT deals.*, cars.vin AS vin
            FROM deals JOIN cars ON cars.id = deals.car_id
            ORDER BY deals.id
            """,
            error="Ошибка чтения",
        ).fetchall()

    # ─── контекстный менеджер ───

    def __enter__(self):
        """Открывает соединение при входе в with."""
        self.connect()
        self.create_tables()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Закрывает соединение при выходе из with."""
        self.close()
        return False
