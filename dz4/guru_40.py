"""
Задача 40 (принципы ISP и DIP из SOLID). В автосалоне есть базовый класс
AutoItem, и постепенно в нём накопились методы, которые нужны не всем типам
транспорта: drive() (только для автомобилей), ride() (только для
мотоциклов), load() (только для грузовиков). Это нарушает принцип ISP
(Interface Segregation Principle) — клиент не должен зависеть от методов,
которые он не использует. Разделите интерфейс на несколько маленьких:
Drivable, Ridable, Loadable, и пусть каждый класс реализует только нужные.
Дополнительно проверьте принцип DIP (Dependency Inversion Principle) —
модули высокого уровня не должны зависеть от модулей низкого уровня; оба
должны зависеть от абстракций. Реализуйте класс SalesService, который
зависит не от конкретных классов (Car, Motorcycle), а от абстракции
AutoItem (или от Protocol). Продемонстрируйте, что можно легко добавить
новый тип транспорта (например, ElectricCar, реализующий только Drivable)
без изменения SalesService. Объясните оба принципа, приведите примеры их
нарушения и расскажите, почему DIP помогает тестировать код (легко подменять
зависимости на mock).
"""

from abc import ABC, abstractmethod
from typing import Protocol
from unittest.mock import Mock


# ================= ДО: «толстый» интерфейс (нарушение ISP) =================
class FatAutoItem(ABC):
    @abstractmethod
    def drive(self): ...

    @abstractmethod
    def ride(self): ...

    @abstractmethod
    def load(self, tons): ...


class FatMotorcycle(FatAutoItem):
    # Мотоцикл вынужден реализовывать чужие методы «заглушками»
    def drive(self):
        raise NotImplementedError("мотоцикл не «водят», на нём ездят верхом")

    def ride(self):
        return "Мотоцикл: еду верхом"

    def load(self, tons):
        raise NotImplementedError("мотоцикл не перевозит грузы")


# ================= ПОСЛЕ: маленькие интерфейсы (ISP) =================
class AutoItem(ABC):
    """Общая абстракция для продаж — только то, что есть у ВСЕХ."""

    def __init__(self, name, price):
        self.name = name
        self.price = price


class Drivable(ABC):
    @abstractmethod
    def drive(self): ...


class Ridable(ABC):
    @abstractmethod
    def ride(self): ...


class Loadable(ABC):
    @abstractmethod
    def load(self, tons): ...


class Car(AutoItem, Drivable):
    def drive(self):
        return f"{self.name}: еду за рулём"


class Motorcycle(AutoItem, Ridable):
    def ride(self):
        return f"{self.name}: еду верхом"


class Truck(AutoItem, Drivable, Loadable):
    def __init__(self, name, price, capacity):
        super().__init__(name, price)
        self.capacity = capacity

    def drive(self):
        return f"{self.name}: веду грузовик"

    def load(self, tons):
        if tons > self.capacity:
            return f"{self.name}: перегруз! максимум {self.capacity} т"
        return f"{self.name}: загружено {tons} т"


# ================= DIP: зависимости от абстракций =================
class Notifier(Protocol):
    """Абстракция «кто-то, кто умеет отправлять сообщения»."""

    def send(self, message: str) -> None: ...


class ConsoleNotifier:
    """Деталь низкого уровня. От Protocol наследоваться не обязательно."""

    def send(self, message):
        print(f"  ✉ {message}")


class SalesService:
    """Модуль высокого уровня. Знает только абстракции AutoItem и Notifier,
    ни одного конкретного класса (Car, Truck, ConsoleNotifier) внутри нет."""

    def __init__(self, notifier: Notifier):
        self.notifier = notifier  # зависимость передаётся снаружи (внедрение)
        self.revenue = 0

    def sell(self, item: AutoItem, buyer: str):
        self.revenue += item.price
        self.notifier.send(f"Продажа: {item.name} → {buyer} — {item.price:,} ₽".replace(",", " "))


def test_drive(item):
    """Клиент, которому нужен только Drivable."""
    print(" ", item.drive())


# ================= Демонстрация =================
print("ISP: каждый класс реализует только нужные интерфейсы")
camry = Car("Toyota Camry", 2_500_000)
moto = Motorcycle("Yamaha MT-07", 900_000)
kamaz = Truck("КАМАЗ 54901", 9_000_000, capacity=20)
print(" ", moto.ride())
print(" ", kamaz.load(15))
print(" ", kamaz.load(25))

print("\nТест-драйв только для Drivable:")
for item in (camry, kamaz, moto):
    if isinstance(item, Drivable):
        test_drive(item)
    else:
        print(f"  {item.name} — не Drivable, тест-драйв за рулём не проводится")


# Новый тип — без изменения SalesService и остального кода (DIP + OCP)
class ElectricCar(AutoItem, Drivable):
    def drive(self):
        return f"{self.name}: еду бесшумно на электротяге"


tesla = ElectricCar("Tesla Model 3", 4_200_000)
test_drive(tesla)

print("\nDIP: SalesService работает с любым AutoItem")
service = SalesService(ConsoleNotifier())
for item, buyer in ((camry, "Иван"), (moto, "Анна"), (kamaz, "ООО «Груз»"), (tesla, "Олег")):
    service.sell(item, buyer)
print(f"  Выручка: {service.revenue:,} ₽".replace(",", " "))

print("\nDIP и тесты: подменяем уведомления на mock")
fake_notifier = Mock()                     # ничего не отправляет, только запоминает вызовы
test_service = SalesService(fake_notifier)
test_service.sell(camry, "Тестовый покупатель")
assert test_service.revenue == 2_500_000
fake_notifier.send.assert_called_once()
print("  send вызван с:", fake_notifier.send.call_args.args[0])
print("  ✓ тест прошёл, ни одного реального письма не отправлено")

print("\nНарушение ISP — заглушки ломаются при вызове:")
try:
    FatMotorcycle().load(1)
except NotImplementedError as e:
    print("  FatMotorcycle.load():", e)

# ISP (принцип разделения интерфейсов):
# клиент не должен зависеть от методов, которые он не использует. Лучше
# много маленьких специализированных интерфейсов, чем один «толстый».
# Нарушение — FatAutoItem: мотоцикл обязан реализовать drive() и load(),
# поэтому пишет заглушки с NotImplementedError. Это ложь в интерфейсе:
# по типу кажется, что мотоцикл умеет грузить, а при вызове — падение
# (это заодно и нарушение LSP). Любое изменение load() затрагивает все
# классы, даже те, кому он не нужен.
# После разделения: Motorcycle реализует только Ridable, Truck — Drivable
# и Loadable, а функция test_drive зависит только от Drivable.
#
# DIP (принцип инверсии зависимостей):
# 1) модули высокого уровня (бизнес-логика продаж) не должны зависеть от
#    модулей низкого уровня (конкретные машины, отправка e-mail/SMS);
#    оба зависят от абстракций (AutoItem, Notifier);
# 2) абстракции не должны зависеть от деталей — наоборот.
# Нарушение выглядело бы так:
#     class SalesService:
#         def __init__(self):
#             self.notifier = EmailSender("smtp.mail.ru")   # жёстко создаём
#         def sell(self, car: Car): ...                        # только Car
# Тогда сменить почту на Telegram или продать мотоцикл можно, только
# переписав SalesService.
#
# Почему DIP помогает тестировать:
# зависимость приходит снаружи (через конструктор), поэтому в тесте
# вместо настоящего отправителя можно передать mock — объект-заглушку,
# который ничего не отправляет, но запоминает, как его вызвали. Тест
# работает быстро, без сети и почтового сервера, и проверяет именно
# логику SalesService. При жёстком EmailSender() внутри класса каждый
# тест слал бы настоящие письма.
