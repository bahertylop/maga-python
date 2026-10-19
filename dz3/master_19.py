"""
Задача 19 (множественное наследование и MRO). В автосалоне работает человек,
который одновременно и продавец, и покупатель — например, менеджер, который
сам покупает машину со скидкой. Создайте два класса-роли: Buyer (покупатель)
и Employee (сотрудник). У каждого родителя есть метод get_role(),
возвращающий свою роль. Затем создайте класс BuyerEmployee, который
наследуется от обоих. Продемонстрируйте порядок разрешения методов через
BuyerEmployee.__mro__ и объясните, какой метод get_role() будет вызван и
почему. Расскажите, что такое MRO (Method Resolution Order), как Python ищет
методы при множественном наследовании и что такое «проблема ромба»
(diamond problem).
"""


class Person:
    """Общий предок — нужен, чтобы показать «ромб»."""

    def get_role(self):
        return "Человек"


class Buyer(Person):
    def get_role(self):
        return "Покупатель"


class Employee(Person):
    def get_role(self):
        return "Сотрудник"


class BuyerEmployee(Buyer, Employee):
    pass


class EmployeeBuyer(Employee, Buyer):  # тот же набор родителей, другой порядок
    pass


manager = BuyerEmployee()
print("BuyerEmployee().get_role():", manager.get_role())  # Покупатель
print("EmployeeBuyer().get_role():", EmployeeBuyer().get_role())  # Сотрудник

print("\nMRO класса BuyerEmployee:")
for i, cls in enumerate(BuyerEmployee.__mro__, 1):
    print(f"  {i}. {cls.__name__}")


# Как получить роли сразу от всех родителей — через super().
# super() идёт не к «родителю», а к СЛЕДУЮЩЕМУ классу в MRO.
class PersonC:
    def get_roles(self):
        return ["Человек"]


class BuyerC(PersonC):
    def get_roles(self):
        return ["Покупатель"] + super().get_roles()


class EmployeeC(PersonC):
    def get_roles(self):
        return ["Сотрудник"] + super().get_roles()


class BuyerEmployeeC(BuyerC, EmployeeC):
    pass


print("\nВсе роли через цепочку super():", BuyerEmployeeC().get_roles())

# Какой get_role() будет вызван и почему:
# Python ищет метод по списку MRO слева направо: BuyerEmployee → Buyer →
# Employee → Person → object. В BuyerEmployee метода нет, в Buyer — есть,
# поэтому вызывается Buyer.get_role() → «Покупатель». Решает порядок
# родителей в объявлении class BuyerEmployee(Buyer, Employee).
#
# MRO (Method Resolution Order) — порядок, в котором Python просматривает
# классы при поиске метода или атрибута. Он вычисляется алгоритмом
# C3-линеаризации и соблюдает два правила:
#   1) потомок всегда проверяется раньше своих родителей;
#   2) родители проверяются в том порядке, в котором перечислены.
# Если эти правила противоречат друг другу, Python не даст создать класс
# (TypeError: Cannot create a consistent method resolution order).
#
# «Проблема ромба»: Buyer и Employee наследуются от общего Person, а
# BuyerEmployee — от обоих. Получается ромб:
#           Person
#          /      \
#      Buyer    Employee
#          \      /
#        BuyerEmployee
# Вопросы: чью версию метода брать и не вызовется ли Person дважды?
# C3-линеаризация отвечает: Person в MRO стоит один раз и после ОБОИХ
# наследников. Поэтому цепочка super() проходит каждый класс ровно один раз:
# ['Покупатель', 'Сотрудник', 'Человек'].
