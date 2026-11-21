-- Схема базы данных автосалона.

CREATE TABLE IF NOT EXISTS cars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vin TEXT UNIQUE NOT NULL,
    brand TEXT NOT NULL,
    model TEXT NOT NULL,
    year INTEGER NOT NULL,
    price INTEGER NOT NULL,
    mileage INTEGER DEFAULT 0,
    is_sold INTEGER DEFAULT 0,
    is_rented INTEGER DEFAULT 0,
    type TEXT NOT NULL,
    extra TEXT DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    budget INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS managers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    experience INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS deals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    car_id INTEGER NOT NULL,
    client_id INTEGER,
    manager_id INTEGER,
    buyer TEXT,
    commission REAL DEFAULT 0,
    date TEXT NOT NULL,
    FOREIGN KEY (car_id) REFERENCES cars(id),
    FOREIGN KEY (client_id) REFERENCES clients(id),
    FOREIGN KEY (manager_id) REFERENCES managers(id)
);
