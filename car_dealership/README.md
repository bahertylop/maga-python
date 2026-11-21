# Автосалон

Учебный проект по объектно-ориентированному программированию на Python.
Показывает, как все ключевые темы ООП работают вместе в одном приложении:
учёт автомобилей и мотоциклов, сделки, прокат, уведомления клиентов,
отчёты, хранение в SQLite и интерфейс командной строки.

## Что внутри

- **Модели** — автомобиль, седан, внедорожник, электромобиль, мотоцикл, двигатель, клиент, менеджер.
- **Сервисы** — хранилище, сделки, прокат, уведомления, отчёты, стратегии комиссии.
- **Паттерны** — Factory, Singleton, Observer, Decorator, Adapter, Strategy.
- **База данных** — SQLite: данные сохраняются между запусками.
- **CLI** — командная строка (10 команд).
- **Тесты** — pytest, 200+ тестов.

## Установка

Нужен Python 3.9 или новее. Внешняя зависимость только `pytest` (для тестов).

```bash
pip install -r requirements.txt
```

## Запуск

### Полное демо

```bash
python main.py
```

### Демо по частям

```bash
python examples/demo_basic.py      # модели и хранилище
python examples/demo_services.py   # сервисы и паттерны
python examples/demo_full.py       # сценарий с базой данных
```

### CLI

Состояние хранится в `data/dealership.db`, поэтому команды можно
запускать по очереди. Другой файл базы: `python cli.py --db my.db ...`

```bash
# Добавить седан (VIN — 17 символов, без букв I, O, Q)
python cli.py add --vin XTA210930Y2765432 --brand Toyota --model Camry --price 3000000 --type sedan --set trunk_volume=500

# Электромобиль с двигателем «вид:мощность:объём»
python cli.py add --vin XTA210930Y2765433 --brand Tesla --model "Model 3" --price 5000000 --type electric --engine электро:300:0 --set battery_kwh=75

python cli.py list
python cli.py find --vin XTA210930Y2765432
python cli.py subscribe --name Иванов --budget 4000000
python cli.py sell --vin XTA210930Y2765432 --buyer Петров
python cli.py rent --vin XTA210930Y2765433 --tenant Сидоров --days 3
python cli.py return --vin XTA210930Y2765433
python cli.py report
python cli.py save      # принудительно записать всё в БД
python cli.py load      # дозагрузить из БД (дубликаты по VIN пропускаются)
```

Типы (`--type`): `car`, `sedan`, `suv`, `motorcycle`, `electric`.
Дополнительные поля типов (`--set КЛЮЧ=ЗНАЧЕНИЕ`): `trunk_volume` (седан),
`drive` (внедорожник), `battery_kwh` (электромобиль), `engine_cc` (мотоцикл).

При ошибке команда печатает `✗ Ошибка: ...` и завершается с кодом 1.

### Тесты

```bash
pytest tests/ -v
```

## Структура проекта

```
car_dealership/
│
├── src/car_dealership/
│   ├── interfaces/     — абстракции (ABC, Protocol) и миксины
│   ├── exceptions/     — собственные исключения
│   ├── utils/          — дескриптор, валидаторы, логирование
│   ├── models/         — доменные объекты
│   ├── services/       — бизнес-логика
│   ├── patterns/       — паттерны проектирования
│   ├── database/       — SQLite: схема, менеджер, репозитории
│   └── cli/            — парсер и обработчики команд
│
├── tests/              — тесты
├── examples/           — демо-скрипты
├── data/               — файл базы данных (создаётся сам)
│
├── config.py           — настройки
├── main.py             — полное демо
├── cli.py              — точка входа CLI
├── README.md
├── requirements.txt
└── setup.py
```

## Архитектура

Проект разделён на слои, каждый зависит только от нижележащих:

1. **Интерфейсы** — контракты (`Infoable`, `Sellable`, `Rentable`, `Serviceable`, `Notifier`, `Storage`).
2. **Исключения** — `DealershipError` и его наследники.
3. **Утилиты** — `RangeDescriptor`, `CarUtils`, логирование.
4. **Модели** — данные и простые методы.
5. **Сервисы** — `CarStorage`, `DealService`, `RentalService`, `NotificationService`, `ReportService`, стратегии комиссии.
6. **Паттерны** — `CarFactory`, `SingletonMeta`, декораторы, `CarAdapter`.
7. **База данных** — `DatabaseManager` и репозитории.
8. **CLI** — фасад над сервисами.

### Иерархия моделей

```
VehicleItem (абстрактный dataclass: vin, brand, model, price, year, mileage)
├── Car (+ engine: Engine)        — Sellable, Rentable, Serviceable
│   ├── Sedan (+ trunk_volume)
│   ├── SUV (+ drive)
│   └── ElectricCar (+ battery_kwh)
└── Motorcycle (+ engine_cc)      — только Sellable
```

## Что демонстрирует проект

| Главы | Тема | Где |
|-------|------|-----|
| 1–2 | Классы, инкапсуляция | Модели, `Engine` |
| 3–4 | Наследование, полиморфизм | `Sedan`, `SUV`, `insurance_cost()` |
| 5–7 | Модификаторы, static, abstract | `interfaces`, `CarUtils` |
| 8 | Композиция | `Car` и `Engine` |
| 9–10 | Override, расширение через super() | `ElectricCar.get_info()` |
| 11–13 | Магические методы | `__str__`, `__lt__`, `__len__`, `__iter__` |
| 14–16 | property, classmethod, счётчик | `title`, `needs_service`, `from_dict`, `VehicleItem.count` |
| 17 | Исключения | `exceptions` |
| 18 | Агрегация, ассоциация | `CarStorage`, `Client` |
| 19–20 | MRO, dataclass, миксины | модели, `LoggableMixin` |
| 21–22 | Дескрипторы | `RangeDescriptor` в `Engine` |
| 23–24 | Метаклассы, Singleton | `SingletonMeta`, `DealershipRegistry` |
| 25 | Factory | `CarFactory` |
| 26 | Observer | `NotificationService`, `Client.update` |
| 27 | SRP | отдельные сервисы и репозитории |
| 28 | Композиция vs наследование | `Car` + `Engine` против `ElectricCar` |
| 29 | Копирование | `Car.clone()` |
| 30 | Утиная типизация | `describe()` |
| 31–33 | Итерация, индексация, with | `CarStorage`, `DatabaseManager` |
| 34–35 | Strategy, OCP, LSP | `commission.py`, `CarFactory.register` |
| 36–37 | `__call__`, `__new__` | `CommissionStrategy.__call__`, `SingletonMeta` |
| 38–39 | Decorator, Adapter | `patterns/decorator.py`, `adapter.py` |
| 40 | ISP, DIP | `interfaces/protocols.py`, `DealService(storage, notifier)` |
