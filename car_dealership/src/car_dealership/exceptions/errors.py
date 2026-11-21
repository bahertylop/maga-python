"""
Собственные исключения проекта.

Все исключения наследуются от DealershipError. Это позволяет
ловить как конкретную ошибку, так и все ошибки автосалона сразу.
"""


class DealershipError(Exception):
    """
    Базовое исключение автосалона.

    Все остальные ошибки проекта наследуются от него.
    Ловить DealershipError — значит ловить все свои ошибки.
    """


class CarNotFoundError(DealershipError):
    """Автомобиль с указанным VIN не найден."""

    def __init__(self, vin):
        self.vin = vin
        super().__init__(f"Автомобиль с VIN {vin!r} не найден")


class CarAlreadySoldError(DealershipError):
    """Автомобиль уже продан."""

    def __init__(self, vin):
        self.vin = vin
        super().__init__(f"Автомобиль {vin!r} уже продан")


class CarAlreadyRentedError(DealershipError):
    """Автомобиль сейчас находится в прокате."""

    def __init__(self, vin):
        self.vin = vin
        super().__init__(f"Автомобиль {vin!r} сейчас в прокате")


class DuplicateCarError(DealershipError):
    """Автомобиль с таким VIN уже есть в хранилище."""

    def __init__(self, vin):
        self.vin = vin
        super().__init__(f"Автомобиль с VIN {vin!r} уже добавлен")


class InvalidVinError(DealershipError):
    """VIN не соответствует формату (17 символов, без I, O, Q)."""

    def __init__(self, vin):
        self.vin = vin
        super().__init__(
            f"Некорректный VIN {vin!r}: нужно 17 латинских букв и цифр "
            f"(буквы I, O, Q не используются)"
        )


class InvalidPriceError(DealershipError):
    """Цена должна быть положительным числом."""

    def __init__(self, price):
        self.price = price
        super().__init__(f"Некорректная цена: {price!r}")


class InvalidMileageError(DealershipError):
    """Некорректный пробег — вне допустимого диапазона."""

    def __init__(self, mileage, min_mileage=0, max_mileage=1_000_000):
        self.mileage = mileage
        self.min_mileage = min_mileage
        self.max_mileage = max_mileage
        super().__init__(
            f"Пробег {mileage} км вне диапазона "
            f"[{min_mileage}, {max_mileage}]"
        )

    def is_too_small(self) -> bool:
        """Проверяет, меньше ли пробег минимального."""
        return self.mileage < self.min_mileage

    def is_too_large(self) -> bool:
        """Проверяет, больше ли пробег максимального."""
        return self.mileage > self.max_mileage


class DatabaseError(DealershipError):
    """Ошибка при работе с базой данных."""

    def __init__(self, message):
        self.message = message
        super().__init__(f"Ошибка БД: {message}")
