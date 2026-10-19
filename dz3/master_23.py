"""
Задача 23 (метаклассы). В автосалоне должен быть только один каталог
автомобилей — если создать второй, данные могут разойтись. Создайте
метакласс SingletonMeta, который гарантирует, что у класса Dealership будет
только один экземпляр. Проверьте, что Dealership() дважды возвращает один и
тот же объект (сравните через is). Объясните, что такое метакласс, как он
связан с классом (класс — это экземпляр метакласса) и зачем вообще нужны
метаклассы, несмотря на их редкость в повседневной работе — в 95% проектов
их не пишут, но понимать их важно для чтения чужого кода и фреймворков
вроде Django.
"""


class SingletonMeta(type):
    """Метакласс: хранит единственный экземпляр для каждого своего класса."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        # Dealership() — это вызов КЛАССА, то есть SingletonMeta.__call__.
        # Обычно он создаёт новый объект (__new__ + __init__).
        # Мы создаём объект только один раз, а дальше возвращаем готовый.
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Dealership(metaclass=SingletonMeta):
    def __init__(self, name="АвтоМир"):
        print(f"  (вызван __init__, создаётся каталог «{name}»)")
        self.name = name
        self.cars = []

    def add_car(self, car):
        self.cars.append(car)


print("Первый вызов Dealership():")
d1 = Dealership()
print("Второй вызов Dealership('Другой салон'):")
d2 = Dealership("Другой салон")  # __init__ повторно НЕ вызывается

print("d1 is d2:", d1 is d2)  # True — один и тот же объект
print("id:", id(d1), id(d2))

d1.add_car("Toyota Camry")
print("Каталог через d2:", d2.cars, "— название:", d2.name)

# Класс — это экземпляр метакласса:
print("\ntype(d1)          =", type(d1).__name__)          # Dealership
print("type(Dealership)  =", type(Dealership).__name__)  # SingletonMeta
print("type(SingletonMeta) =", type(SingletonMeta).__name__)  # type
print("type(int), type(str) =", type(int).__name__, type(str).__name__)  # type type

# Класс можно создать и без слова class — напрямую через метакласс type:
Motorcycle = type("Motorcycle", (), {"wheels": 2})
print("Класс, созданный через type():", Motorcycle.__name__, "колёс:", Motorcycle.wheels)

# Что такое метакласс:
# В Python всё — объекты, в том числе классы. Объекты создаются классами,
# а классы создаются метаклассами. Метакласс — это «класс классов».
#   объект d1   — экземпляр класса Dealership;
#   Dealership  — экземпляр метакласса SingletonMeta;
#   SingletonMeta наследует type — стандартный метакласс всех классов.
# Метакласс управляет тем, как класс СОЗДАЁТСЯ (__new__, __init__ метакласса)
# и как ведёт себя при ВЫЗОВЕ (__call__ — здесь и живёт Singleton).
#
# Зачем нужны, если их редко пишут:
# - фреймворки: в Django модели описываются как
#   class Car(models.Model): price = models.IntegerField(), а метакласс
#   при создании класса собирает поля и превращает их в таблицу БД;
#   так же работают SQLAlchemy, ABCMeta (абстрактные классы из задачи 7),
#   Enum;
# - автоматическая регистрация классов, проверка структуры классов,
#   добавление методов всем наследникам.
# Сами в обычном коде их пишут редко: чаще хватает декораторов классов
# или __init_subclass__. Но без понимания метаклассов «магия» фреймворков
# выглядит непрозрачной.
