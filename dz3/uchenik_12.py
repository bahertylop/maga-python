"""
Задача 12 (магические методы __eq__ и __hash__). В автосалоне может
оказаться несколько экземпляров одной и той же модели — например, разные
комплектации одного авто. Нужно, чтобы программа понимала, что это «один и
тот же автомобиль», и не дублировала его в каталоге. Реализуйте в классе Car
магический метод __eq__, чтобы два автомобиля считались равными, если
совпадают их марка и модель. Дополнительно реализуйте __hash__, чтобы
автомобили можно было хранить во множестве set и использовать как ключи в
словаре. Проверьте, что два одинаковых автомобиля попадают в множество как
один элемент, а разные — как два. Объясните в комментариях, почему при
переопределении __eq__ нужно также переопределять __hash__ — что
произойдёт, если этого не сделать.
"""


class Car:
    def __init__(self, brand, model, trim=""):
        self.brand = brand
        self.model = model
        self.trim = trim  # комплектация — на равенство не влияет

    def __eq__(self, other):
        if not isinstance(other, Car):
            return NotImplemented  # сравнение с «чужим» типом Python обработает сам
        return (self.brand, self.model) == (other.brand, other.model)

    def __hash__(self):
        # Хеш строится по тем же полям, что и сравнение в __eq__.
        return hash((self.brand, self.model))

    def __repr__(self):
        return f"Car({self.brand!r}, {self.model!r}, {self.trim!r})"


camry_base = Car("Toyota", "Camry", "Стандарт")
camry_lux = Car("Toyota", "Camry", "Люкс")
rio = Car("Kia", "Rio", "Комфорт")

print("camry_base == camry_lux:", camry_base == camry_lux)  # True
print("camry_base == rio:      ", camry_base == rio)        # False

catalog = {camry_base, camry_lux, rio}
print("Автомобилей в каталоге:", len(catalog))  # 2 — две Camry считаются одной
print(catalog)

prices = {camry_base: 2500000}
print("Цена по ключу camry_lux:", prices[camry_lux])  # ключ найден — объекты равны


# Почему вместе с __eq__ нужно переопределять __hash__:
# set и dict сначала ищут элемент по хешу («в какую ячейку смотреть»),
# а уже потом сравнивают через __eq__. Правило: если a == b, то обязательно
# hash(a) == hash(b). Иначе равные объекты попадут в разные ячейки,
# и множество будет хранить «дубликаты».
#
# Что будет, если не сделать: в Python 3 класс, где определён __eq__,
# но не определён __hash__, автоматически получает __hash__ = None.
# Такие объекты становятся нехешируемыми — их нельзя положить в set
# или использовать ключом словаря (TypeError: unhashable type).
class CarOnlyEq:
    def __init__(self, brand, model):
        self.brand = brand
        self.model = model

    def __eq__(self, other):
        return (self.brand, self.model) == (other.brand, other.model)


try:
    {CarOnlyEq("Toyota", "Camry")}
except TypeError as e:
    print("Без __hash__:", e)
