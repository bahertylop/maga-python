"""
Задача 3 (наследование). В автосалоне продаются разные типы транспорта.
Создайте базовый класс Vehicle с методом get_kind(), возвращающим строку
«Транспорт». Унаследуйте от него классы Car и Motorcycle, переопределив в
каждом метод get_kind() так, чтобы он возвращал «Автомобиль» и «Мотоцикл»
соответственно. Создайте по одному объекту каждого класса и выведите их вид,
чтобы убедиться, что каждый класс возвращает своё значение. В комментариях
объясните, что произойдёт, если в наследнике не переопределять метод, и как
вызвать родительскую версию через super().
"""


class Vehicle:
    def get_kind(self):
        return "Транспорт"


class Car(Vehicle):
    def get_kind(self):
        return "Автомобиль"


class Motorcycle(Vehicle):
    def get_kind(self):
        return "Мотоцикл"

    def get_full_kind(self):
        # super() даёт доступ к методам родительского класса.
        # super().get_kind() вызовет версию из Vehicle, а не из Motorcycle.
        return f"{self.get_kind()} ({super().get_kind()})"


# Наследник без переопределения: метод ищется сначала в классе Truck,
# не находится там и берётся из родителя Vehicle. Поэтому вернётся «Транспорт».
class Truck(Vehicle):
    pass


car = Car()
moto = Motorcycle()
truck = Truck()

print("Car:       ", car.get_kind())        # Автомобиль
print("Motorcycle:", moto.get_kind())       # Мотоцикл
print("Truck:     ", truck.get_kind())      # Транспорт — метод не переопределён
print("Через super():", moto.get_full_kind())  # Мотоцикл (Транспорт)
