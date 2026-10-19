"""
Задача 37 (__new__ vs __init__). В автосалоне есть класс Car, и нужно понять,
в каком порядке Python создаёт объект. Реализуйте в классе Car оба метода —
__new__ и __init__ — и добавьте в каждый отладочный вывод (print), чтобы
увидеть порядок вызова. Продемонстрируйте, что __new__ вызывается до __init__
и отвечает за создание объекта, а __init__ — за его инициализацию.
Дополнительно реализуйте __new__, который возвращает уже существующий объект
(например, для кэширования автомобилей по марке и модели): два вызова
Car("Toyota", "Camry", 2500000) должны вернуть один и тот же объект.
Объясните разницу между __new__ и __init__, зачем вообще нужен __new__ и
почему «__new__ + кэш» легко приводит к странному поведению.
"""


# ---------- Часть 1: порядок вызова ----------
class Car:
    def __new__(cls, brand, model, price):
        print(f"  1) __new__: создаю пустой объект класса {cls.__name__}")
        instance = super().__new__(cls)  # object.__new__ выделяет память
        print(f"     объект создан, id={id(instance)}, полей пока нет: {instance.__dict__}")
        return instance  # этот объект Python передаст в __init__ как self

    def __init__(self, brand, model, price):
        print(f"  2) __init__: заполняю объект id={id(self)}")
        self.brand = brand
        self.model = model
        self.price = price


print("Создаём Car('Toyota', 'Camry', 2500000):")
car = Car("Toyota", "Camry", 2500000)
print("  готово:", car.__dict__)


# ---------- Часть 2: __new__ с кэшем ----------
class CachedCar:
    _cache = {}

    def __new__(cls, brand, model, price):
        key = (brand, model)
        if key in cls._cache:
            print(f"  __new__: {brand} {model} уже есть в кэше — возвращаю его")
            return cls._cache[key]
        print(f"  __new__: создаю новый {brand} {model}")
        instance = super().__new__(cls)
        cls._cache[key] = instance
        return instance

    def __init__(self, brand, model, price):
        # Подвох: __init__ вызывается ВСЕГДА, если __new__ вернул объект
        # этого класса — даже если объект взят из кэша.
        print(f"  __init__: price = {price}")
        self.brand = brand
        self.model = model
        self.price = price


print("\nДва вызова с одинаковыми данными:")
c1 = CachedCar("Toyota", "Camry", 2500000)
c2 = CachedCar("Toyota", "Camry", 2500000)
print("  c1 is c2:", c1 is c2)  # True — один и тот же объект

print("\nСтранное поведение: третий вызов с ДРУГОЙ ценой:")
c3 = CachedCar("Toyota", "Camry", 1)
print("  c1.price =", c1.price, "← цена «старого» автомобиля молча изменилась!")
print("  c1 is c3:", c1 is c3)


# ---------- Как обойти: не перезаписывать уже готовый объект ----------
class SafeCachedCar:
    _cache = {}

    def __new__(cls, brand, model, price):
        key = (brand, model)
        if key not in cls._cache:
            cls._cache[key] = super().__new__(cls)
        return cls._cache[key]

    def __init__(self, brand, model, price):
        if getattr(self, "_initialized", False):
            return  # объект из кэша — не трогаем его поля
        self.brand, self.model, self.price = brand, model, price
        self._initialized = True


s1 = SafeCachedCar("Kia", "Rio", 1800000)
s2 = SafeCachedCar("Kia", "Rio", 1)
print("\nЗащищённый вариант: s1 is s2:", s1 is s2, "| s1.price =", s1.price)


# ---------- Где __new__ действительно нужен: неизменяемые типы ----------
class Price(int):
    """Цена — наследник неизменяемого int. Значение задаётся только в __new__:
    к моменту __init__ число уже создано и изменить его нельзя."""

    def __new__(cls, value):
        rounded = round(value / 1000) * 1000  # округляем до тысяч
        return super().__new__(cls, rounded)


print("Price(2_499_700) =", Price(2_499_700), "| это int:", isinstance(Price(1), int))

# Разница между __new__ и __init__:
# - __new__(cls, ...) — СТАТИЧЕСКИЙ по сути метод класса, вызывается первым.
#   Он СОЗДАЁТ объект (выделяет память) и возвращает его. Может вернуть
#   новый объект, уже существующий объект или даже объект другого класса.
# - __init__(self, ...) — вызывается вторым, получает уже готовый объект и
#   ИНИЦИАЛИЗИРУЕТ его: заполняет поля. Ничего не возвращает (только None).
# Car(...) по сути делает:
#     obj = Car.__new__(Car, ...)
#     if isinstance(obj, Car):
#         obj.__init__(...)
#
# Зачем нужен __new__ (в обычном коде он почти не нужен):
# - наследование от неизменяемых типов (int, str, tuple, frozenset):
#   их значение можно задать только при создании (пример Price);
# - контроль создания объектов: Singleton (задача 24), кэширование и
#   повторное использование объектов (пул, «приспособленец»/Flyweight);
# - метаклассы и фабрики, которые решают, объект какого класса вернуть.
#
# Почему «__new__ + кэш» ведёт к странному поведению:
# 1) __init__ вызывается при каждом Car(...), даже если __new__ вернул
#    старый объект из кэша, — и молча перезаписывает его поля
#    (c1.price стала 1). Все, кто держал ссылку на этот объект, получили
#    неожиданно изменённые данные;
# 2) кэш хранит объекты вечно (утечка памяти) — нужен weakref;
# 3) код выглядит как создание нового объекта, а возвращает старый —
#    это неочевидно читающему; изменение одной «копии» меняет «все».
# Поэтому кэширование чаще делают явно: фабричным методом
# Car.get_or_create(...) или словарём снаружи класса.
