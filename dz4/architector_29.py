"""
Задача 29 (копирование объектов). В автосалоне нужно создавать копии
карточек автомобилей — например, для резервного каталога. При этом у
автомобиля есть вложенный объект Engine, и важно понимать, копируется ли он
вместе с автомобилем или остаётся общим. Реализуйте в классе Car методы
__copy__ и __deepcopy__. Создайте автомобиль с вложенным объектом Engine и
продемонстрируйте разницу между поверхностным (copy.copy) и глубоким
(copy.deepcopy) копированием: при поверхностном — двигатель общий
(shallow.engine is car.engine → True), при глубоком — свой (deep.engine is
car.engine → False). Объясните, когда какой тип копирования использовать и
что делать с циклическими ссылками.
"""

import copy


class Engine:
    def __init__(self, kind, power_hp):
        self.kind = kind
        self.power_hp = power_hp

    def __repr__(self):
        return f"Engine({self.kind}, {self.power_hp} л.с.)"


class Car:
    def __init__(self, brand, model, engine, dealership=None):
        self.brand = brand
        self.model = model
        self.engine = engine
        self.dealership = dealership  # для примера с циклической ссылкой

    def __copy__(self):
        # Поверхностная копия: новый объект Car, но поля указывают
        # на ТЕ ЖЕ объекты, что и у оригинала (двигатель общий).
        print("  (вызван Car.__copy__)")
        new = Car.__new__(Car)              # создаём объект без __init__
        new.__dict__.update(self.__dict__)  # копируем ссылки на значения
        return new

    def __deepcopy__(self, memo):
        # Глубокая копия: рекурсивно копируем и вложенные объекты.
        # memo — словарь «id оригинала → его копия»; защищает от бесконечной
        # рекурсии при циклических ссылках и от повторного копирования.
        print("  (вызван Car.__deepcopy__)")
        new = Car.__new__(Car)
        memo[id(self)] = new  # регистрируем копию ДО копирования полей!
        for key, value in self.__dict__.items():
            setattr(new, key, copy.deepcopy(value, memo))
        return new

    def __repr__(self):
        return f"Car({self.brand} {self.model}, {self.engine})"


car = Car("Toyota", "Camry", Engine("бензиновый", 200))

print("Поверхностная копия:")
shallow = copy.copy(car)
print("  shallow is car:", shallow is car)                 # False — новый автомобиль
print("  shallow.engine is car.engine:", shallow.engine is car.engine)  # True — общий

print("Глубокая копия:")
deep = copy.deepcopy(car)
print("  deep is car:", deep is car)                       # False
print("  deep.engine is car.engine:", deep.engine is car.engine)        # False — свой

print("\nТюнингуем двигатель оригинала: 200 → 250 л.с.")
car.engine.power_hp = 250
print("  оригинал:   ", car)
print("  поверхностная:", shallow, "← изменилась вместе с оригиналом!")
print("  глубокая:   ", deep, "← не изменилась")

# Простые поля у поверхностной копии независимы: присваивание создаёт
# новую ссылку только в копии
shallow.model = "Corolla"
print("  после shallow.model = 'Corolla': оригинал —", car.model)


# ---------- Циклические ссылки ----------
class Dealership:
    def __init__(self, name):
        self.name = name
        self.cars = []


salon = Dealership("АвтоМир")
rio = Car("Kia", "Rio", Engine("бензиновый", 123), dealership=salon)
salon.cars.append(rio)  # цикл: rio → salon → salon.cars → rio

print("\nГлубокая копия объекта с циклической ссылкой:")
rio_copy = copy.deepcopy(rio)
print("  копия ссылается на копию салона:", rio_copy.dealership is not salon)
print("  цикл сохранён внутри копии:", rio_copy.dealership.cars[0] is rio_copy)

# Когда какое копирование использовать:
# - Поверхностное (copy.copy) — быстрое и дешёвое. Подходит, когда вложенные
#   объекты неизменяемые (строки, числа, кортежи) или их действительно нужно
#   разделять (например, у копий карточек один общий салон).
# - Глубокое (copy.deepcopy) — когда копия должна быть полностью
#   независимой: резервный каталог, «черновик» для редактирования, откат
#   изменений. Медленнее и требует больше памяти.
#
# Циклические ссылки (rio → salon → rio):
# наивное рекурсивное копирование ушло бы в бесконечный цикл. deepcopy
# решает это словарём memo: перед копированием полей объект регистрирует
# свою копию в memo, и при повторной встрече того же объекта возвращается
# уже готовая копия. Поэтому в своём __deepcopy__ важно:
#   1) записать копию в memo[id(self)] ДО копирования полей;
#   2) передавать memo во все вложенные вызовы copy.deepcopy(value, memo).
# Ссылки на «внешние» объекты, которые копировать не нужно (общий салон,
# соединение с БД), можно в __deepcopy__ переносить как есть, без deepcopy.
