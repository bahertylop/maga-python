"""
Задача 32 (индексация объекта: __getitem__ и __setitem__). На выставочной
площадке автомобили должны быть доступны по индексу — как элементы списка:
showroom[0] возвращает первый автомобиль, showroom[1] = car заменяет второй.
Реализуйте в классе Showroom магические методы __getitem__ и __setitem__.
Продемонстрируйте, что теперь работают: showroom[0] — получение автомобиля
по индексу, showroom[1] = new_car — замена автомобиля, срезы showroom[0:2] —
получение подсписка, for car in showroom — итерация (за счёт __getitem__,
даже без __iter__). Дополнительно реализуйте __delitem__ (удаление по
индексу) и __contains__ (проверка car in showroom). Объясните, как
__getitem__ делает объект «похожим» на список или словарь и почему важно,
чтобы он выбрасывал именно IndexError, а не какое-то своё исключение.
"""


class Showroom:
    def __init__(self, name, cars):
        self.name = name
        self._cars = list(cars)

    def __getitem__(self, index):
        # index может быть числом (showroom[0]) или срезом (showroom[0:2]).
        if isinstance(index, slice):
            # Срез возвращаем новой площадкой — как list[0:2] возвращает list
            return Showroom(f"{self.name} (срез)", self._cars[index])
        # list сам выбросит IndexError при выходе за границы — это и нужно
        return self._cars[index]

    def __setitem__(self, index, car):
        self._cars[index] = car

    def __delitem__(self, index):
        del self._cars[index]

    def __contains__(self, car):
        return car in self._cars

    def __len__(self):
        return len(self._cars)

    def __repr__(self):
        return f"Showroom({self.name!r}, {self._cars})"

    # __iter__ специально НЕ определён — итерация работает через __getitem__


showroom = Showroom("Север", ["Toyota Camry", "Kia Rio", "BMW X5", "Lada Vesta"])
print(showroom)

print("showroom[0]  =", showroom[0])
print("showroom[-1] =", showroom[-1])  # отрицательные индексы тоже работают

showroom[1] = "Haval Jolion"
print("После showroom[1] = 'Haval Jolion':", showroom)

print("showroom[0:2]  =", showroom[0:2])
print("showroom[::2]  =", showroom[::2])

print("Итерация без __iter__:")
for car in showroom:
    print("  ", car)

del showroom[0]
print("После del showroom[0]:", showroom)

print("'BMW X5' in showroom:", "BMW X5" in showroom)
print("'Toyota Camry' in showroom:", "Toyota Camry" in showroom)
print("list(showroom):", list(showroom), "| len:", len(showroom))

try:
    showroom[100]
except IndexError as e:
    print("showroom[100] → IndexError:", e)


# ---------- Почему важно именно IndexError ----------
class BadShowroom:
    def __init__(self, cars):
        self._cars = list(cars)

    def __getitem__(self, index):
        if index >= len(self._cars):
            raise ValueError("нет такого места")  # «своё» исключение
        return self._cars[index]


print("\nBadShowroom с ValueError вместо IndexError:")
try:
    for car in BadShowroom(["Toyota Camry", "Kia Rio"]):
        print("  ", car)
except ValueError as e:
    print("   цикл for упал после последнего элемента:", e)

# Как __getitem__ делает объект похожим на список или словарь:
# Python превращает синтаксис квадратных скобок в вызовы методов:
#   showroom[i]         → showroom.__getitem__(i)
#   showroom[i] = car   → showroom.__setitem__(i, car)
#   del showroom[i]     → showroom.__delitem__(i)
#   showroom[0:2]       → showroom.__getitem__(slice(0, 2, None))
#   car in showroom     → showroom.__contains__(car)
# Ключом может быть что угодно: число (как у списка), строка (как у
# словаря — например, showroom["VIN123"]), кортеж. Так объект получает
# привычный синтаксис встроенных коллекций.
#
# Почему важен именно IndexError:
# если у класса нет __iter__, цикл for использует «старый протокол»:
# вызывает __getitem__(0), __getitem__(1), ... пока не получит IndexError —
# это сигнал «элементы закончились». Своё исключение (ValueError) for не
# распознаёт и падает с ошибкой. Точно так же list(), in и распаковка
# рассчитывают на IndexError. Аналогично, объекты «как словарь» должны
# бросать KeyError — на это рассчитаны dict.get-подобные обёртки и код,
# который ловит except KeyError. Соблюдая стандартный протокол исключений,
# мы делаем объект совместимым со всем остальным Python.
