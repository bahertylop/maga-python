"""
Тесты интерфейсов, исключений и утилит.
"""

import logging

import pytest

from src.car_dealership.exceptions import (
    CarAlreadyRentedError, CarAlreadySoldError, CarNotFoundError,
    DatabaseError, DealershipError, DuplicateCarError,
    InvalidMileageError, InvalidPriceError, InvalidVinError,
)
from src.car_dealership.interfaces import (
    Describable, Infoable, LoggableMixin, Notifier, Rentable, Sellable,
    Serviceable, Storage, TimestampMixin,
)
from src.car_dealership.utils import (
    CarUtils, DealershipLogger, RangeDescriptor, setup_logging,
)
from tests.vins import VIN_1


# ─── интерфейсы ───

@pytest.mark.parametrize("abstract", [
    Infoable, Sellable, Rentable, Serviceable, Notifier, Storage,
])
def test_interfaces_are_abstract(abstract):
    with pytest.raises(TypeError):
        abstract()


def test_loggable_mixin_prints_class_name(capsys):
    class Thing(LoggableMixin):
        pass

    Thing().log("привет")
    out = capsys.readouterr().out
    assert "Thing: привет" in out and out.startswith("[")


def test_timestamp_mixin():
    class Thing(TimestampMixin):
        pass

    thing = Thing()
    thing.set_created()
    assert thing.created_at is not None


def test_describable_protocol_is_structural():
    class Duck:
        def describe(self):
            return "кря"

    def use(obj: Describable) -> str:
        return obj.describe()

    assert use(Duck()) == "кря"


# ─── исключения ───

@pytest.mark.parametrize("error", [
    CarNotFoundError(VIN_1), CarAlreadySoldError(VIN_1),
    CarAlreadyRentedError(VIN_1), DuplicateCarError(VIN_1),
    InvalidVinError("x"), InvalidPriceError(-1),
    InvalidMileageError(-5), DatabaseError("x"),
])
def test_all_errors_inherit_base(error):
    assert isinstance(error, DealershipError)


def test_error_messages_contain_data():
    assert VIN_1 in str(CarNotFoundError(VIN_1))
    assert "Ошибка БД" in str(DatabaseError("плохо"))
    assert "-1" in str(InvalidPriceError(-1))


def test_catch_all_with_base_class():
    with pytest.raises(DealershipError):
        raise CarAlreadySoldError(VIN_1)


def test_invalid_mileage_helpers():
    low, high = InvalidMileageError(-1), InvalidMileageError(5_000_000)
    assert low.is_too_small() and not low.is_too_large()
    assert high.is_too_large() and not high.is_too_small()


# ─── дескриптор ───

class Box:
    size = RangeDescriptor(1, 10)

    def __init__(self, size):
        self.size = size


def test_descriptor_valid_value():
    assert Box(5).size == 5


@pytest.mark.parametrize("bad", [0, 11, -1])
def test_descriptor_out_of_range(bad):
    with pytest.raises(ValueError):
        Box(bad)


@pytest.mark.parametrize("bad", ["5", None, True])
def test_descriptor_wrong_type(bad):
    with pytest.raises(TypeError):
        Box(bad)


def test_descriptor_class_access_returns_descriptor():
    assert isinstance(Box.size, RangeDescriptor)


# ─── CarUtils ───

@pytest.mark.parametrize("vin, ok", [
    (VIN_1, True), ("XTA210930Y276543", False), (VIN_1 + "1", False),
    ("XTA210930Y27654OI", False), ("xta210930y2765432", False),
    (None, False), (123, False),
])
def test_is_valid_vin(vin, ok):
    assert CarUtils.is_valid_vin(vin) is ok


@pytest.mark.parametrize("price, ok", [
    (1, True), (0.5, True), (0, False), (-1, False), ("1", False), (True, False),
])
def test_is_valid_price(price, ok):
    assert CarUtils.is_valid_price(price) is ok


@pytest.mark.parametrize("year, ok", [
    (2024, True), (1950, True), (1949, False), (2101, False), (2024.5, False),
])
def test_is_valid_year(year, ok):
    assert CarUtils.is_valid_year(year) is ok


@pytest.mark.parametrize("mileage, ok", [
    (0, True), (1_000_000, True), (-1, False), (1_000_001, False), (1.5, False),
])
def test_is_valid_mileage(mileage, ok):
    assert CarUtils.is_valid_mileage(mileage) is ok


def test_formatters():
    assert CarUtils.format_price(3_000_000) == "3 000 000 ₽"
    assert CarUtils.format_price(1234.5) == "1 234 ₽" or CarUtils.format_price(1234.5) == "1 235 ₽"
    assert CarUtils.format_mileage(15000) == "15 000 км"


def test_static_methods_need_no_instance():
    assert CarUtils.is_valid_price(10) is True


# ─── логирование ───

def test_setup_logging_does_not_duplicate_handlers():
    logger = setup_logging(logging.DEBUG)
    count = len(logger.handlers)
    setup_logging(logging.DEBUG)
    assert len(logger.handlers) == count
    assert logger.level == logging.DEBUG


def test_dealership_logger_writes(caplog):
    setup_logging()
    log = DealershipLogger("test")
    log.logger.propagate = True
    with caplog.at_level(logging.INFO, logger="car_dealership"):
        log.info("сообщение")
        log.warning("внимание")
        log.error("ошибка")
    texts = [r.getMessage() for r in caplog.records]
    assert texts == ["сообщение", "внимание", "ошибка"]
