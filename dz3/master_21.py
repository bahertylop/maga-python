"""
Задача 21 (__slots__). В автосалоне может храниться огромное количество
автомобилей — десятки тысяч. При таком объёме важна экономия памяти: каждый
объект Car по умолчанию хранит словарь атрибутов, что занимает много места.
Добавьте в класс Car атрибут __slots__ = ("brand", "model", "price").
Убедитесь, что теперь нельзя добавить новый атрибут объекту (например,
car.color = "красный" вызовет AttributeError). Сравните размер объекта с
__slots__ и без него через sys.getsizeof — но учтите, что getsizeof
показывает размер только «оболочки» объекта, не считая содержимое словаря;
для честного сравнения используйте pympler.asizeof или оцените по количеству
полей. Объясните, как __slots__ экономит память, что теряется при его
использовании (наследование, __dict__, @property) и в каких случаях его стоит
применять.
"""

import sys
import tracemalloc


class CarRegular:
    def __init__(self, brand, model, price):
        self.brand = brand
        self.model = model
        self.price = price


class Car:
    __slots__ = ("brand", "model", "price")

    def __init__(self, brand, model, price):
        self.brand = brand
        self.model = model
        self.price = price


regular = CarRegular("Toyota", "Camry", 2500000)
slotted = Car("Toyota", "Camry", 2500000)

# 1. Новый атрибут добавить нельзя
regular.color = "красный"  # обычному объекту — можно
print("Обычный объект, color:", regular.color)
try:
    slotted.color = "красный"
except AttributeError as e:
    print("Объект со __slots__:", e)

# 2. sys.getsizeof — только «оболочка» объекта
print("\nsys.getsizeof (только оболочка):")
print(f"  без __slots__: {sys.getsizeof(regular)} байт "
      f"+ отдельно __dict__: {sys.getsizeof(regular.__dict__)} байт")
print(f"  со __slots__:  {sys.getsizeof(slotted)} байт (__dict__ нет)")

# 3. Честное сравнение
try:
    from pympler import asizeof
    print("\npympler.asizeof (вместе со всем содержимым):")
    print(f"  без __slots__: {asizeof.asizeof(CarRegular('Toyota', 'Camry', 2500000))} байт")
    print(f"  со __slots__:  {asizeof.asizeof(Car('Toyota', 'Camry', 2500000))} байт")
except ImportError:
    # pympler — сторонняя библиотека (pip install pympler). Если её нет,
    # считаем «оболочку + словарь атрибутов» вручную.
    reg_total = sys.getsizeof(regular) + sys.getsizeof(regular.__dict__)
    print("\npympler не установлен, оценка «оболочка + __dict__»:")
    print(f"  без __slots__: {reg_total} байт")
    print(f"  со __slots__:  {sys.getsizeof(slotted)} байт")


# 4. Самое наглядное — память на 100 000 объектов
def measure(cls, n=100_000):
    tracemalloc.start()
    cars = [cls("Toyota", "Camry", i) for i in range(n)]
    current, _ = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    del cars
    return current / 1024 / 1024


mem_regular = measure(CarRegular)
mem_slotted = measure(Car)
print(f"\n100 000 объектов (tracemalloc):")
print(f"  без __slots__: {mem_regular:.1f} МБ")
print(f"  со __slots__:  {mem_slotted:.1f} МБ")
print(f"  экономия: {(1 - mem_slotted / mem_regular) * 100:.0f}%")

# Как __slots__ экономит память:
# Обычный объект хранит атрибуты в отдельном словаре __dict__. Словарь —
# гибкая, но «тяжёлая» структура с запасом места под новые ключи.
# При __slots__ Python не создаёт __dict__, а резервирует в самом объекте
# фиксированные ячейки под перечисленные поля (как в кортеже).
# На один объект выигрыш — десятки байт, на десятки тысяч — мегабайты.
# Плюс доступ к атрибутам немного быстрее.
#
# Что теряется:
# - нельзя добавлять новые атрибуты «на лету» (нет __dict__);
# - наследование: если в наследнике не объявить свои __slots__, у него
#   снова появится __dict__ и экономия пропадёт; при множественном
#   наследовании от двух классов с непустыми __slots__ будет конфликт;
# - @property работает, но нельзя назвать слот так же, как свойство
#   (будет конфликт имён) — значение храните в слоте с другим именем,
#   например "_price";
# - без "__weakref__" в слотах на объект нельзя сделать слабую ссылку;
# - некоторые библиотеки, рассчитывающие на obj.__dict__, перестают работать.
#
# Когда применять: когда объектов очень много (десятки тысяч и больше),
# набор полей заранее известен и не меняется — записи из БД, точки,
# элементы каталога. Для обычных классов это преждевременная оптимизация.
