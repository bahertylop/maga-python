"""
Тесты сервисов.

Проверяют хранилище, комиссии, уведомления, сделки, прокат, отчёты.
"""

import pytest

from src.car_dealership.exceptions import (
    CarAlreadyRentedError, CarAlreadySoldError, CarNotFoundError,
    DealershipError, DuplicateCarError,
)
from src.car_dealership.interfaces import Notifier, Storage
from src.car_dealership.models import Car, Client, Motorcycle
from src.car_dealership.services import (
    CarStorage, DealService, EmailNotifier, FixedCommission,
    LoyaltyCommission, NotificationService, PercentCommission,
    RentalService, ReportService, SmsNotifier,
)
from tests.vins import VIN_1, VIN_2, VIN_3, VIN_4


class SpyNotifier(Notifier):
    """Тестовый уведомитель: запоминает сообщения вместо печати."""

    def __init__(self):
        self.messages = []

    def send(self, message: str) -> None:
        self.messages.append(message)


@pytest.fixture
def filled_storage(sample_storage, sample_car, sample_motorcycle):
    """Хранилище с автомобилем и мотоциклом."""
    sample_storage.add(sample_car)
    sample_storage.add(sample_motorcycle)
    return sample_storage


# ─── CarStorage ───

def test_storage_is_storage_interface(sample_storage):
    assert isinstance(sample_storage, Storage)


def test_storage_add_and_len(sample_storage, sample_car):
    sample_storage.add(sample_car)
    assert len(sample_storage) == 1


def test_storage_save_is_add(sample_storage, sample_car):
    sample_storage.save(sample_car)
    assert sample_car in sample_storage


def test_storage_duplicate_vin(sample_storage, sample_car):
    sample_storage.add(sample_car)
    with pytest.raises(DuplicateCarError):
        sample_storage.add(Car(VIN_1, "Other", "x", 1))


def test_storage_find_by_vin(filled_storage, sample_car):
    assert filled_storage.find_by_vin(VIN_1) is sample_car


def test_storage_find_missing(sample_storage):
    with pytest.raises(CarNotFoundError) as err:
        sample_storage.find_by_vin(VIN_4)
    assert err.value.vin == VIN_4
    assert isinstance(err.value, DealershipError)


def test_storage_find_by_brand_ignores_case(filled_storage, sample_car):
    assert filled_storage.find_by_brand("toyota") == [sample_car]
    assert filled_storage.find_by_brand("Lada") == []


def test_storage_filter(filled_storage, sample_motorcycle):
    cheap = filled_storage.filter(lambda i: i.price < 2_000_000)
    assert cheap == [sample_motorcycle]


def test_storage_available_and_total_value(filled_storage, sample_car):
    assert filled_storage.total_value() == 3_000_000 + 1_900_000
    sample_car.sell()
    assert filled_storage.available() == [filled_storage[1]]
    assert filled_storage.total_value() == 1_900_000


def test_storage_remove(filled_storage, sample_car):
    filled_storage.remove(sample_car)
    assert len(filled_storage) == 1
    filled_storage.remove(sample_car)  # повторное удаление безвредно
    assert len(filled_storage) == 1


def test_storage_magic_methods(filled_storage, sample_car):
    assert len(filled_storage) == 2
    assert sample_car in filled_storage
    assert filled_storage[0] is sample_car
    assert len(filled_storage[0:2]) == 2
    assert [i.brand for i in filled_storage] == ["Toyota", "BMW"]


def test_storage_list_all_returns_copy(filled_storage):
    items = filled_storage.list_all()
    items.clear()
    assert len(filled_storage) == 2


# ─── стратегии комиссии ───

def test_fixed_commission():
    assert FixedCommission().calculate(10_000_000) == 30_000
    assert FixedCommission(5).calculate(1) == 5


def test_percent_commission():
    assert PercentCommission().calculate(1_000_000) == pytest.approx(50_000)
    assert PercentCommission(0.1).calculate(1_000_000) == pytest.approx(100_000)


def test_loyalty_commission_is_cheaper():
    price = 2_000_000
    assert LoyaltyCommission().calculate(price) < PercentCommission().calculate(price)
    assert isinstance(LoyaltyCommission(), PercentCommission)


def test_commission_strategy_is_callable():
    assert PercentCommission(0.1)(1000) == pytest.approx(100)


# ─── уведомления ───

def test_notification_subscribe_and_notify():
    service = NotificationService()
    a, b = Client("А"), Client("Б")
    service.subscribe(a)
    service.subscribe(b)
    service.notify("акция")
    assert a.notifications == ["А: акция"]
    assert b.notifications == ["Б: акция"]


def test_notification_no_duplicates():
    service = NotificationService()
    client = Client("А")
    service.subscribe(client)
    service.subscribe(client)
    assert service.count() == 1


def test_notification_unsubscribe():
    service = NotificationService()
    client = Client("А")
    service.subscribe(client)
    service.unsubscribe(client)
    service.unsubscribe(client)  # повторная отписка безвредна
    service.notify("x")
    assert client.notifications == []
    assert service.count() == 0


def test_notification_duck_typing():
    """Подписчиком может быть любой объект с update()."""
    class Dummy:
        got = None

        def update(self, event):
            self.got = event

    dummy = Dummy()
    service = NotificationService()
    service.subscribe(dummy)
    service.notify("ping")
    assert dummy.got == "ping"


def test_notifier_implementations(capsys):
    EmailNotifier().send("привет")
    SmsNotifier().send("привет")
    out = capsys.readouterr().out
    assert "[Email] привет" in out and "[SMS] привет" in out


# ─── DealService ───

def test_deal_sell(filled_storage, sample_car):
    spy = SpyNotifier()
    service = DealService(filled_storage, spy, PercentCommission())
    deal = service.sell(VIN_1, "Петров")
    assert sample_car.is_sold is True
    assert deal["buyer"] == "Петров"
    assert deal["commission"] == pytest.approx(150_000)
    assert "Петров" in spy.messages[0]
    assert service.history == [deal]


def test_deal_without_commission(filled_storage):
    service = DealService(filled_storage, SpyNotifier())
    assert service.sell(VIN_1, "Петров")["commission"] == 0


def test_deal_sell_twice(filled_storage):
    service = DealService(filled_storage, SpyNotifier())
    service.sell(VIN_1, "Петров")
    with pytest.raises(CarAlreadySoldError):
        service.sell(VIN_1, "Сидоров")


def test_deal_missing_car(sample_storage):
    with pytest.raises(CarNotFoundError):
        DealService(sample_storage, SpyNotifier()).sell(VIN_4, "x")


def test_deal_cannot_sell_rented(filled_storage):
    notifier = SpyNotifier()
    RentalService(filled_storage, notifier).rent(VIN_1, "Иванов", 2)
    with pytest.raises(CarAlreadyRentedError):
        DealService(filled_storage, notifier).sell(VIN_1, "Петров")


def test_deal_publishes_to_subscribers(filled_storage):
    publisher = NotificationService()
    client = Client("Иван")
    publisher.subscribe(client)
    DealService(filled_storage, SpyNotifier(), publisher=publisher).sell(VIN_1, "П")
    assert "Продан Toyota Camry" in client.notifications[0]


def test_deal_motorcycle_sellable(filled_storage, sample_motorcycle):
    DealService(filled_storage, SpyNotifier()).sell(VIN_3, "Байкер")
    assert sample_motorcycle.is_sold is True


def test_deal_not_sellable_object(sample_storage):
    class Showpiece:
        vin = VIN_4
        is_sold = False
        is_rented = False

    sample_storage._items.append(Showpiece())
    with pytest.raises(TypeError):
        DealService(sample_storage, SpyNotifier()).sell(VIN_4, "x")


# ─── RentalService ───

def test_rental_rent(filled_storage, sample_car):
    spy = SpyNotifier()
    result = RentalService(filled_storage, spy).rent(VIN_1, "Иванов", 3)
    assert sample_car.is_rented is True
    assert result["days"] == 3
    assert result["cost"] == round(3_000_000 * RentalService.DAILY_RATE * 3)
    assert "Иванов" in spy.messages[0]


def test_rental_twice(filled_storage):
    service = RentalService(filled_storage, SpyNotifier())
    service.rent(VIN_1, "Иванов", 3)
    with pytest.raises(CarAlreadyRentedError):
        service.rent(VIN_1, "Петров", 1)


def test_rental_motorcycle_not_rentable(filled_storage):
    with pytest.raises(TypeError):
        RentalService(filled_storage, SpyNotifier()).rent(VIN_3, "x", 1)


def test_rental_sold_car(filled_storage):
    DealService(filled_storage, SpyNotifier()).sell(VIN_1, "П")
    with pytest.raises(CarAlreadySoldError):
        RentalService(filled_storage, SpyNotifier()).rent(VIN_1, "x", 1)


@pytest.mark.parametrize("days", [0, -3])
def test_rental_invalid_days(filled_storage, days):
    with pytest.raises(ValueError):
        RentalService(filled_storage, SpyNotifier()).rent(VIN_1, "x", days)


def test_rental_return(filled_storage, sample_car):
    service = RentalService(filled_storage, SpyNotifier())
    service.rent(VIN_1, "Иванов", 2)
    service.return_item(VIN_1)
    assert sample_car.is_rented is False
    service.rent(VIN_1, "Петров", 1)  # снова можно


# ─── ReportService ───

def test_report_generate(filled_storage):
    text = ReportService().generate(filled_storage, "АвтоМир")
    assert text.startswith("Автосалон: АвтоМир")
    assert "[в продаже]" in text


def test_report_statuses(filled_storage):
    DealService(filled_storage, SpyNotifier()).sell(VIN_1, "П")
    filled_storage[1].is_rented = True
    text = ReportService().generate(filled_storage, "АвтоМир")
    assert "[продан]" in text and "[в прокате]" in text


def test_report_sales_empty():
    assert ReportService().generate_sales_report([]) == "Сделок не было"


def test_report_sales(filled_storage):
    service = DealService(filled_storage, SpyNotifier(), PercentCommission())
    service.sell(VIN_1, "Петров")
    service.sell(VIN_3, "Байкер")
    text = ReportService().generate_sales_report(service.history)
    assert "Всего сделок: 2" in text
    assert "Выручка: 4 900 000 ₽" in text
    assert "Суммарная комиссия: 245 000 ₽" in text
    assert "Петров" in text


def test_report_stats(filled_storage):
    text = ReportService().generate_stats(filled_storage)
    assert "Всего единиц: 2" in text
    assert "Средняя цена: 2 450 000 ₽" in text
    assert "BMW — 1, Toyota — 1" in text


def test_report_stats_empty(sample_storage):
    assert ReportService().generate_stats(sample_storage) == "Склад пуст"


def test_services_are_independent(filled_storage):
    """SRP: сервисы можно создавать и использовать независимо."""
    storage = filled_storage
    assert ReportService().generate(storage, "A")
    assert RentalService(storage, SpyNotifier()).storage is storage
