"""
Тесты моделей.

Проверяют создание объектов, работу методов,
классовый счётчик, сериализацию, валидацию.
"""

import pytest

from src.car_dealership.exceptions import (
    InvalidMileageError, InvalidPriceError, InvalidVinError,
)
from src.car_dealership.interfaces import Rentable, Sellable, Serviceable
from src.car_dealership.models import (
    Car, Sedan, SUV, Motorcycle, ElectricCar, Engine, Client, Manager,
    VehicleItem,
)
from tests.vins import VIN_1, VIN_2, VIN_3


# ─── Car ───

def test_car_creation(sample_car):
    """Автомобиль создаётся с правильными полями."""
    assert sample_car.vin == VIN_1
    assert sample_car.brand == "Toyota"
    assert sample_car.price == 3_000_000
    assert sample_car.year == 2023
    assert sample_car.is_sold is False
    assert sample_car.is_rented is False


def test_car_get_info(sample_car):
    """Метод get_info содержит марку, VIN и цену."""
    info = sample_car.get_info()
    assert "Toyota Camry" in info
    assert VIN_1 in info
    assert "3 000 000 ₽" in info


def test_car_str_equals_get_info(sample_car):
    """__str__ возвращает то же, что get_info."""
    assert str(sample_car) == sample_car.get_info()


def test_car_title(sample_car):
    """Свойство title — «марка модель»."""
    assert sample_car.title == "Toyota Camry"


def test_car_is_new():
    """Новый автомобиль — с нулевым пробегом."""
    assert Car(VIN_1, "Kia", "Rio", 1_000_000).is_new is True
    assert Car(VIN_2, "Kia", "Rio", 1_000_000, mileage=10).is_new is False


def test_car_sell(sample_car):
    """Метод sell помечает автомобиль проданным."""
    assert sample_car.sell() == "Продано"
    assert sample_car.is_sold is True


def test_car_sell_twice(sample_car):
    """Повторная продажа возвращает «Уже продан»."""
    sample_car.sell()
    assert sample_car.sell() == "Уже продан"


def test_car_rent(sample_car):
    """Метод rent возвращает строку-подтверждение."""
    assert sample_car.rent() == "Выдан в прокат"


def test_car_service_and_needs_service(sample_car):
    """ТО нужно при пробеге от 15 000 км."""
    assert sample_car.needs_service is True
    assert "ТО выполнено" in sample_car.service()
    assert Car(VIN_2, "Kia", "Rio", 1_000_000, mileage=100).needs_service is False


def test_car_age(sample_car):
    """Возраст считается от указанного года и не бывает отрицательным."""
    assert sample_car.age(2026) == 3
    assert sample_car.age(2000) == 0


def test_car_count():
    """Классовый счётчик увеличивается при создании."""
    VehicleItem.count = 0
    Car(VIN_1, "A", "a", 1)
    Car(VIN_2, "B", "b", 1)
    Motorcycle(VIN_3, "C", "c", 1)
    assert VehicleItem.count == 3


def test_car_to_dict(sample_car):
    """to_dict возвращает словарь с нужными ключами."""
    data = sample_car.to_dict()
    assert data["type"] == "Car"
    assert data["vin"] == VIN_1
    assert data["is_sold"] is False
    assert data["engine"] is None


def test_car_roundtrip_with_engine():
    """to_dict -> from_dict восстанавливает равный объект, включая двигатель."""
    car = Car(VIN_1, "Toyota", "Camry", 3_000_000, 2022, 5000,
              Engine("бензин", 181, 2.5))
    restored = Car.from_dict(car.to_dict())
    assert restored == car
    assert restored.engine.power_hp == 181


def test_from_dict_restores_flags():
    """Флаги is_sold / is_rented восстанавливаются из словаря."""
    data = Car(VIN_1, "A", "a", 1).to_dict()
    data.update(is_sold=True, is_rented=True)
    car = Car.from_dict(data)
    assert car.is_sold is True and car.is_rented is True


def test_car_clone_changes_fields(sample_car):
    """clone создаёт копию с изменёнными полями, оригинал не меняется."""
    twin = sample_car.clone(price=1_000_000)
    assert twin.price == 1_000_000
    assert sample_car.price == 3_000_000
    assert twin is not sample_car


def test_cars_sort_by_price():
    """sorted() работает благодаря __lt__ по цене."""
    cheap = Car(VIN_1, "A", "a", 100)
    mid = Car(VIN_2, "B", "b", 200)
    rich = Car(VIN_3, "C", "c", 300)
    assert sorted([rich, cheap, mid]) == [cheap, mid, rich]


def test_car_implements_interfaces(sample_car):
    """Car — это Sellable, Rentable и Serviceable."""
    assert isinstance(sample_car, Sellable)
    assert isinstance(sample_car, Rentable)
    assert isinstance(sample_car, Serviceable)


# ─── валидация ───

@pytest.mark.parametrize("bad_vin", ["", "123", "XTA210930Y27654OI", "x" * 17, None])
def test_invalid_vin(bad_vin):
    """Некорректный VIN отвергается."""
    with pytest.raises(InvalidVinError):
        Car(bad_vin, "A", "a", 1)


@pytest.mark.parametrize("bad_price", [0, -5, "100", None, True])
def test_invalid_price(bad_price):
    """Цена должна быть положительным числом."""
    with pytest.raises(InvalidPriceError):
        Car(VIN_1, "A", "a", bad_price)


def test_invalid_mileage():
    """Отрицательный и слишком большой пробег отвергаются."""
    with pytest.raises(InvalidMileageError) as err:
        Car(VIN_1, "A", "a", 1, mileage=-1)
    assert err.value.is_too_small()
    with pytest.raises(InvalidMileageError) as err:
        Car(VIN_1, "A", "a", 1, mileage=2_000_000)
    assert err.value.is_too_large()


def test_invalid_year():
    """Год вне диапазона — ValueError."""
    with pytest.raises(ValueError):
        Car(VIN_1, "A", "a", 1, year=1800)


# ─── наследники ───

def test_sedan_info_and_insurance():
    """Седан переопределяет описание и страховку."""
    sedan = Sedan(VIN_1, "Kia", "K5", 2_500_000, trunk_volume=510)
    assert sedan.get_info().startswith("Седан Kia K5")
    assert "510 л" in sedan.get_info()
    assert sedan.insurance_cost() == 40_000


def test_suv_info_and_insurance():
    """Внедорожник показывает тип привода."""
    suv = SUV(VIN_1, "Lada", "Niva", 1_200_000, drive="AWD")
    assert "привод AWD" in suv.get_info()
    assert suv.insurance_cost() == 65_000


def test_electric_car_extends_parent_info():
    """ElectricCar дополняет описание родителя через super()."""
    ev = ElectricCar(VIN_1, "Tesla", "3", 5_000_000, battery_kwh=75)
    assert ev.get_info().startswith(Car.get_info(ev))
    assert "батарея 75 кВт·ч" in ev.get_info()
    assert ev.range_km == 450


def test_electric_service_interval_is_doubled():
    """У электромобиля ТО реже."""
    ev = ElectricCar(VIN_1, "Tesla", "3", 5_000_000, mileage=20_000)
    assert ev.needs_service is False
    assert Car.needs_service.fget(ev) is True


def test_polymorphism_insurance():
    """Один вызов insurance_cost() ведёт себя по-разному у разных классов."""
    items = [
        Car(VIN_1, "A", "a", 1), Sedan(VIN_2, "B", "b", 1),
        SUV(VIN_3, "C", "c", 1),
    ]
    assert [i.insurance_cost() for i in items] == [45_000, 40_000, 65_000]


def test_motorcycle_sellable_not_rentable(sample_motorcycle):
    """Мотоцикл продаётся, но не Rentable."""
    assert isinstance(sample_motorcycle, Sellable)
    assert not isinstance(sample_motorcycle, Rentable)
    assert sample_motorcycle.sell() == "Мотоцикл продан"
    assert sample_motorcycle.sell() == "Уже продан"


def test_vehicle_item_is_abstract():
    """VehicleItem нельзя создать напрямую."""
    with pytest.raises(TypeError):
        VehicleItem(VIN_1, "A", "a", 1)


def test_describe_duck_typing(sample_car):
    """Describe работает у автомобилей, клиентов и менеджеров."""
    for obj in (sample_car, Client("Иван", 1), Manager("Ольга", 5)):
        assert isinstance(obj.describe(), str)


# ─── Engine ───

def test_engine_show():
    """Описание двигателя зависит от вида."""
    assert "2.5 л" in Engine("бензин", 181, 2.5).show()
    assert Engine("электро", 300, 0).show() == "электро 300 л.с."


def test_engine_descriptor_validation():
    """Дескриптор не даёт записать мощность вне диапазона."""
    with pytest.raises(ValueError):
        Engine("бензин", 5000, 2.0)
    with pytest.raises(TypeError):
        Engine("бензин", "много", 2.0)


def test_engine_descriptor_is_per_instance():
    """Значения дескриптора хранятся отдельно у каждого объекта."""
    a, b = Engine(power_hp=100), Engine(power_hp=200)
    assert (a.power_hp, b.power_hp) == (100, 200)


# ─── Client / Manager ───

def test_client_update_collects_notifications(capsys):
    """Client.update сохраняет и печатает уведомление."""
    client = Client("Иван", 5_000_000)
    client.update("новое поступление")
    assert client.notifications == ["Иван: новое поступление"]
    assert "новое поступление" in capsys.readouterr().out


def test_client_can_afford():
    """Клиент может купить, если бюджет не меньше цены."""
    client = Client("Иван", 3_000_000)
    assert client.can_afford(3_000_000) is True
    assert client.can_afford(3_000_001) is False


def test_manager_bonus_rate():
    """Бонус растёт со стажем и ограничен 5%."""
    assert Manager("А", 1).bonus_rate == 0
    assert Manager("Б", 4).bonus_rate == pytest.approx(0.02)
    assert Manager("В", 40).bonus_rate == pytest.approx(0.05)
