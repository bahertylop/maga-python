"""
Задача 27 (принцип SOLID — SRP). Класс Dealership со временем разросся: он и
хранит автомобили, и оформляет сделки, и отправляет уведомления, и ведёт
отчёты. Это нарушает принцип единственной ответственности (SRP) — у класса
должна быть одна причина для изменения. Разбейте класс Dealership на
несколько классов: CarStorage (хранение автомобилей и поиск по
марке/модели), SaleService (оформление сделок, ведение учёта),
NotificationService (уведомления). Продемонстрируйте работу собранных
сервисов на сценарии «покупатель оформил покупку». Объясните, почему это
лучше одного большого класса, как понять, что у класса «одна причина для
изменения», и приведите примеры «классов-богов» из реальной жизни.
"""

from dataclasses import dataclass
from datetime import date


@dataclass
class Car:
    brand: str
    model: str
    price: int


# ---------- ДО: «класс-бог» (для сравнения) ----------
class GodDealership:
    """Всё в одном: хранение, продажи, уведомления, отчёты.
    Причины для изменения: новая БД, новые правила скидок, переход
    с e-mail на Telegram, новый формат отчёта — четыре разные причины."""

    def __init__(self):
        self.cars, self.sales = [], []

    def add_car(self, car): ...
    def find_car(self, brand, model): ...
    def sell(self, brand, model, buyer): ...
    def send_email(self, to, text): ...
    def make_report(self): ...


# ---------- ПОСЛЕ: у каждого класса одна ответственность ----------
class CarStorage:
    """Только хранение и поиск автомобилей."""

    def __init__(self):
        self._cars = []

    def add(self, car):
        self._cars.append(car)

    def find(self, brand, model):
        for car in self._cars:
            if (car.brand.lower(), car.model.lower()) == (brand.lower(), model.lower()):
                return car
        return None

    def remove(self, car):
        self._cars.remove(car)

    def __len__(self):
        return len(self._cars)


class NotificationService:
    """Только отправка уведомлений. Сменить канал (e-mail → Telegram) —
    значит поменять только этот класс."""

    def send(self, recipient, message):
        print(f"  ✉ Уведомление для {recipient}: {message}")


class SaleService:
    """Только оформление сделок и учёт продаж.
    Хранилище и уведомления получает снаружи — не создаёт их сам."""

    def __init__(self, storage, notifier):
        self.storage = storage
        self.notifier = notifier
        self.sales = []

    def sell(self, brand, model, buyer):
        car = self.storage.find(brand, model)
        if car is None:
            self.notifier.send(buyer, f"к сожалению, {brand} {model} нет в наличии")
            return None
        self.storage.remove(car)
        sale = {"date": date.today(), "car": car, "buyer": buyer}
        self.sales.append(sale)
        self.notifier.send(buyer, f"покупка {car.brand} {car.model} оформлена")
        self.notifier.send("менеджер", f"{buyer} купил {car.brand} {car.model}")
        return sale

    def total_revenue(self):
        return sum(s["car"].price for s in self.sales)


# ---------- Сборка и сценарий ----------
storage = CarStorage()
for car in (Car("Toyota", "Camry", 2_500_000), Car("Kia", "Rio", 1_800_000)):
    storage.add(car)

sales = SaleService(storage, NotificationService())

print("Сценарий: покупатель оформил покупку")
print("Машин в наличии до покупки:", len(storage))
sales.sell("Toyota", "Camry", "Иван Петров")
print("Машин в наличии после покупки:", len(storage))

print("\nПопытка купить отсутствующую машину:")
sales.sell("BMW", "X5", "Анна Смирнова")

print(f"\nВыручка: {sales.total_revenue():,} ₽".replace(",", " "))

# Почему это лучше одного большого класса:
# - изменения локальны: переход на Telegram затрагивает только
#   NotificationService и не может сломать учёт продаж;
# - классы маленькие, их легко читать и тестировать по отдельности
#   (в тесте SaleService можно подсунуть фейковый notifier, который
#   ничего не отправляет);
# - части можно переиспользовать: NotificationService пригодится и для
#   записи на техобслуживание;
# - над разными классами могут работать разные разработчики без
#   конфликтов в одном огромном файле.
#
# Как понять, что у класса «одна причина для изменения»:
# - спросите: «кто (какой отдел, какая роль) может попросить изменить этот
#   класс?» — если ответов несколько (бухгалтерия, маркетинг, админ БД),
#   ответственностей тоже несколько;
# - попробуйте описать класс одним предложением без союза «и»;
# - методы класса используют разные группы полей, которые между собой
#   не пересекаются, — признак, что класс можно разрезать;
# - в имени есть Manager, Helper, Utils, Processor — частый сигнал «свалки».
#
# «Классы-боги» в реальной жизни:
# - класс Application / MainWindow на тысячи строк, где и интерфейс,
#   и бизнес-логика, и работа с БД;
# - User, который хранит данные, проверяет пароль, отправляет письма
#   и генерирует PDF-отчёты;
# - Utils / Helpers — сборник несвязанных функций на все случаи жизни;
# - в жизни вне кода: «сотрудник-универсал», который и продаёт, и ведёт
#   бухгалтерию, и ремонтирует машины — уйдёт в отпуск, и всё встанет.
