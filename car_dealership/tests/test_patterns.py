"""
Тесты паттернов: Factory, Singleton, Decorator, Adapter.
"""

import pytest

from src.car_dealership.interfaces import Infoable
from src.car_dealership.models import (
    Car, Sedan, SUV, Motorcycle, ElectricCar,
)
from src.car_dealership.patterns import (
    CarAdapter, CarFactory, CreditDecorator, DealershipRegistry,
    ItemDecorator, SingletonMeta, WarrantyDecorator, WinterTiresDecorator,
)
from tests.vins import VIN_1, VIN_2, VIN_3


# ─── Factory ───

@pytest.mark.parametrize("kind, klass", [
    ("car", Car), ("sedan", Sedan), ("suv", SUV),
    ("motorcycle", Motorcycle), ("electric", ElectricCar),
])
def test_factory_creates_each_kind(kind, klass):
    item = CarFactory.create(kind, vin=VIN_1, brand="A", model="a", price=1)
    assert type(item) is klass


def test_factory_passes_extra_fields():
    ev = CarFactory.create("electric", vin=VIN_1, brand="T", model="3",
                           price=1, battery_kwh=99)
    assert ev.battery_kwh == 99


def test_factory_unknown_kind():
    with pytest.raises(ValueError) as err:
        CarFactory.create("rocket", vin=VIN_1, brand="A", model="a", price=1)
    assert "rocket" in str(err.value) and "sedan" in str(err.value)


def test_factory_list_kinds():
    assert set(CarFactory.list_kinds()) >= {
        "car", "sedan", "suv", "motorcycle", "electric"}


def test_factory_register_decorator():
    @CarFactory.register("pickup_test")
    class Pickup(Car):
        pass

    try:
        item = CarFactory.create("pickup_test", vin=VIN_1, brand="A",
                                 model="a", price=1)
        assert isinstance(item, Pickup)
        assert "pickup_test" in CarFactory.list_kinds()
    finally:
        CarFactory._registry.pop("pickup_test")


def test_cli_kinds_match_factory():
    """Список типов в парсере совпадает с реестром фабрики."""
    from src.car_dealership.cli.parser import VEHICLE_KINDS
    assert set(VEHICLE_KINDS) == set(CarFactory.list_kinds())


# ─── Singleton ───

def test_singleton_returns_same_instance():
    assert DealershipRegistry() is DealershipRegistry()


def test_singleton_shares_state():
    DealershipRegistry().add_branch("Тверь")
    assert "Тверь" in DealershipRegistry().branches
    DealershipRegistry().branches.remove("Тверь")


def test_singleton_meta_on_custom_class():
    class Config(metaclass=SingletonMeta):
        def __init__(self):
            self.value = 1

    first = Config()
    first.value = 42
    assert Config().value == 42


def test_singleton_per_class():
    class A(metaclass=SingletonMeta):
        pass

    class B(metaclass=SingletonMeta):
        pass

    assert A() is not B()


# ─── Decorator ───

@pytest.fixture
def car():
    return Car(VIN_1, "Toyota", "Camry", 3_000_000)


def test_decorator_delegates(car):
    assert ItemDecorator(car).get_info() == car.get_info()


def test_decorators_add_labels(car):
    assert WarrantyDecorator(car, 5).get_info().endswith("(гарантия 5 г.)")
    assert CreditDecorator(car).get_info().endswith("(кредит возможен)")
    assert WinterTiresDecorator(car).get_info().endswith("(зимняя резина в подарок)")


def test_decorators_chain(car):
    info = WarrantyDecorator(CreditDecorator(car)).get_info()
    assert car.get_info() in info
    assert info.index("кредит") < info.index("гарантия")


def test_decorator_does_not_change_original(car):
    before = car.get_info()
    WarrantyDecorator(car).get_info()
    assert car.get_info() == before


def test_decorator_is_infoable(car):
    assert isinstance(CreditDecorator(car), Infoable)


# ─── Adapter ───

def test_adapter_external_keys():
    adapter = CarAdapter({
        "vin_code": VIN_2, "maker": "Skoda", "name": "Octavia",
        "cost": 2_000_000, "production_year": 2021,
    })
    assert adapter.vin == VIN_2
    assert adapter.brand == "Skoda"
    assert adapter.model == "Octavia"
    assert adapter.price == 2_000_000
    assert adapter.year == 2021


def test_adapter_internal_keys():
    adapter = CarAdapter({"vin": VIN_2, "brand": "Kia", "model": "Rio",
                          "price": 1_000_000, "year": 2020})
    assert adapter.brand == "Kia" and adapter.year == 2020


def test_adapter_prefers_external_keys():
    adapter = CarAdapter({"maker": "Ext", "brand": "Int"})
    assert adapter.brand == "Ext"


def test_adapter_get_info_and_missing_price():
    adapter = CarAdapter({"vin": VIN_3, "brand": "A", "model": "b", "year": 2000})
    assert "VIN " + VIN_3 in adapter.get_info()
    assert adapter.price == 0


def test_adapter_is_infoable():
    assert isinstance(CarAdapter({}), Infoable)
