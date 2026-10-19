"""
Задача 31 (итерация по объекту: __iter__ и __next__). В автосалоне есть
выставочная площадка Showroom, и хочется перебирать автомобили на ней в цикле
for — так же удобно, как список. Сейчас for car in showroom: не работает.
Реализуйте в классе Showroom магические методы __iter__ и __next__ так, чтобы
по площадке можно было итерироваться несколько раз подряд (это важно:
__iter__ должен возвращать отдельный объект-итератор или генератор, а не
self, иначе повторная итерация сломается). Создайте площадку с несколькими
автомобилями и переберите их в цикле for дважды подряд. Объясните, чем
отличается итератор от итерируемого объекта, зачем нужны оба метода и
почему list(showroom) должен возвращать список всех автомобилей.
"""


class ShowroomIterator:
    """Итератор: помнит текущую позицию и умеет выдавать следующий элемент."""

    def __init__(self, cars):
        self._cars = cars
        self._index = 0

    def __iter__(self):
        # Итератор сам тоже итерируемый: возвращает себя.
        # Так его можно передать прямо в for.
        return self

    def __next__(self):
        if self._index >= len(self._cars):
            raise StopIteration  # сигнал циклу for: элементы закончились
        car = self._cars[self._index]
        self._index += 1
        return car


class Showroom:
    """Итерируемый объект: хранит данные и по запросу выдаёт НОВЫЙ итератор."""

    def __init__(self, name, cars):
        self.name = name
        self._cars = list(cars)

    def __iter__(self):
        # Каждый вызов — новый итератор со своим счётчиком с нуля.
        # Поэтому можно перебирать площадку сколько угодно раз.
        return ShowroomIterator(self._cars)


# ---------- Неправильный вариант: __iter__ возвращает self ----------
class BrokenShowroom:
    def __init__(self, cars):
        self._cars = list(cars)
        self._index = 0

    def __iter__(self):
        return self  # счётчик общий и не сбрасывается

    def __next__(self):
        if self._index >= len(self._cars):
            raise StopIteration
        car = self._cars[self._index]
        self._index += 1
        return car


cars = ["Toyota Camry", "Kia Rio", "BMW X5"]
showroom = Showroom("Север", cars)

print("Первый проход:")
for car in showroom:
    print("  ", car)
print("Второй проход:")
for car in showroom:
    print("  ", car)

print("list(showroom):", list(showroom))
print("'Kia Rio' in showroom:", "Kia Rio" in showroom)  # in тоже работает через __iter__

# Как for устроен внутри
it = iter(showroom)   # showroom.__iter__()
print("\nРучной перебор через next():", next(it), "|", next(it), "|", next(it))
try:
    next(it)
except StopIteration:
    print("StopIteration — элементы закончились")

broken = BrokenShowroom(cars)
print("\nBrokenShowroom, первый проход:", list(broken))
print("BrokenShowroom, второй проход:", list(broken), "← пусто, итератор «исчерпан»")


# Короткий вариант: __iter__ как генератор — Python сам создаёт итератор
class ShowroomGen:
    def __init__(self, cars):
        self._cars = list(cars)

    def __iter__(self):
        for car in self._cars:
            yield car  # каждый вызов __iter__ — новый генератор


g = ShowroomGen(cars)
print("\nГенераторный вариант, дважды:", list(g), list(g))

# Итерируемый объект (iterable) vs итератор (iterator):
# - Итерируемый объект — «коллекция», которую можно перебрать. У него есть
#   __iter__, который возвращает итератор. Примеры: list, str, dict, Showroom.
#   Его можно перебирать многократно.
# - Итератор — «курсор» по коллекции: помнит, где остановился, и по __next__
#   выдаёт следующий элемент, а в конце бросает StopIteration. Он одноразовый:
#   дошёл до конца — всё. У итератора есть и __iter__ (возвращает self),
#   и __next__.
#
# Зачем оба метода: for car in showroom превращается в
#     it = iter(showroom)        # __iter__ — получить итератор
#     while True:
#         try: car = next(it)    # __next__ — взять следующий элемент
#         except StopIteration: break
# __iter__ отвечает за «начать перебор заново», __next__ — за «дай следующий».
# Если склеить их в одном объекте (BrokenShowroom), позиция общая на все
# переборы, и второй for получит пустоту.
#
# Почему list(showroom) должен вернуть все автомобили: list(), tuple(),
# set(), sum(), sorted(), in, распаковка a, b, c = showroom — всё это
# работает через тот же протокол итерации. Реализовав __iter__, мы
# получаем всю эту функциональность «бесплатно», а объект ведёт себя как
# обычная коллекция Python.
