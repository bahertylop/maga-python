"""
Задача 25 (паттерн Factory). Автосалон регулярно пополняется разными типами
транспорта — автомобилями, мотоциклами, грузовиками. Создавать их напрямую
через конструкторы неудобно: код разрастается, легко ошибиться. Создайте
класс VehicleFactory с методом create(kind, **kwargs), который по строке
"car", "motorcycle" или "truck" создаёт соответствующий объект и возвращает
его. Неизвестный тип должен вызывать ValueError. Продемонстрируйте работу
фабрики: создайте по одному транспортному средству каждого типа через
фабрику. Объясните, почему фабрика удобнее прямого вызова конструкторов и
как этот паттерн связан с принципом Open/Closed (см. задачу 35).
"""


class Car:
    def __init__(self, brand, model, seats=5):
        self.brand, self.model, self.seats = brand, model, seats

    def __repr__(self):
        return f"Car({self.brand} {self.model}, мест: {self.seats})"


class Motorcycle:
    def __init__(self, brand, model, engine_cc):
        self.brand, self.model, self.engine_cc = brand, model, engine_cc

    def __repr__(self):
        return f"Motorcycle({self.brand} {self.model}, {self.engine_cc} см³)"


class Truck:
    def __init__(self, brand, model, capacity_t):
        self.brand, self.model, self.capacity_t = brand, model, capacity_t

    def __repr__(self):
        return f"Truck({self.brand} {self.model}, грузоподъёмность {self.capacity_t} т)"


class VehicleFactory:
    # Реестр «строка → класс». Новый тип добавляется одной строкой
    # или через register(), без переписывания метода create().
    _registry = {
        "car": Car,
        "motorcycle": Motorcycle,
        "truck": Truck,
    }

    @classmethod
    def register(cls, kind, vehicle_cls):
        cls._registry[kind.lower()] = vehicle_cls

    @classmethod
    def create(cls, kind, **kwargs):
        vehicle_cls = cls._registry.get(kind.lower())
        if vehicle_cls is None:
            raise ValueError(
                f"Неизвестный тип транспорта: {kind!r}. "
                f"Доступные: {', '.join(cls._registry)}"
            )
        return vehicle_cls(**kwargs)


print(VehicleFactory.create("car", brand="Toyota", model="Camry"))
print(VehicleFactory.create("motorcycle", brand="Yamaha", model="MT-07", engine_cc=689))
print(VehicleFactory.create("truck", brand="КАМАЗ", model="54901", capacity_t=20))

try:
    VehicleFactory.create("boat", brand="Yamaha", model="242X")
except ValueError as e:
    print("Ошибка:", e)


# Расширение без изменения фабрики (Open/Closed):
class Bus:
    def __init__(self, brand, model, seats):
        self.brand, self.model, self.seats = brand, model, seats

    def __repr__(self):
        return f"Bus({self.brand} {self.model}, мест: {self.seats})"


VehicleFactory.register("bus", Bus)
print(VehicleFactory.create("bus", brand="ПАЗ", model="Vector Next", seats=45))

# Удобно, когда тип приходит строкой — из файла, формы, БД:
orders = [("car", {"brand": "Kia", "model": "Rio"}),
          ("truck", {"brand": "Volvo", "model": "FH", "capacity_t": 25})]
print("Из списка заказов:", [VehicleFactory.create(k, **p) for k, p in orders])

# Почему фабрика удобнее прямых конструкторов:
# - создание объектов собрано в одном месте: остальной код не знает
#   о конкретных классах и не импортирует их;
# - тип выбирается по данным во время выполнения (строка из файла/формы)
#   без цепочек if kind == "car": ... elif kind == "truck": ...;
# - проверка ошибок (неизвестный тип) тоже в одном месте;
# - если конструктор класса изменится или класс заменят другим,
#   правка нужна только в фабрике.
#
# Связь с Open/Closed (задача 35): код должен быть открыт для расширения,
# но закрыт для изменения. Благодаря реестру новый тип (Bus) добавлен
# через register(), а метод create() не изменился ни на строчку.
# С цепочкой if/elif пришлось бы каждый раз править саму фабрику.
