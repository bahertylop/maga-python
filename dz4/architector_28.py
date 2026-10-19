"""
Задача 28 (композиция vs наследование). Электромобили (ElectricCar) похожи на
обычные автомобили, но имеют дополнительные поля — ёмкость батареи, запас
хода. Реализуйте одну и ту же задачу двумя способами: через наследование
(ElectricCar(Car) — переопределяет конструктор и добавляет свои поля) и через
композицию (ElectricCar содержит объект Car внутри себя как поле self.car).
Сравните плюсы и минусы каждого подхода: наследование даёт переиспользование
кода, но создаёт жёсткую связь; композиция гибче, но требует больше кода.
Объясните, когда что выбирать, и приведите примеры из реальных проектов и
стандартной библиотеки Python.
"""


class Car:
    def __init__(self, brand, model, price):
        self.brand = brand
        self.model = model
        self.price = price

    def info(self):
        price_str = f"{self.price:,}".replace(",", " ")
        return f"{self.brand} {self.model}, {price_str} ₽"

    def tax(self):
        return 5000


# ===================== Способ 1: наследование =====================
class ElectricCarInh(Car):
    def __init__(self, brand, model, price, battery_kwh, range_km):
        super().__init__(brand, model, price)  # переиспользуем конструктор родителя
        self.battery_kwh = battery_kwh
        self.range_km = range_km

    def info(self):
        return f"{super().info()}, батарея {self.battery_kwh} кВт·ч, запас хода {self.range_km} км"

    # tax() наследуется автоматически — писать не нужно.
    # Но наследуется и то, что электромобилю может не подходить:
    # если в Car появится метод refuel() («заправить бензином»),
    # он «приедет» и в ElectricCarInh.


# ===================== Способ 2: композиция =====================
class Battery:
    def __init__(self, capacity_kwh, range_km):
        self.capacity_kwh = capacity_kwh
        self.range_km = range_km

    def info(self):
        return f"батарея {self.capacity_kwh} кВт·ч, запас хода {self.range_km} км"


class ElectricCarComp:
    def __init__(self, brand, model, price, battery_kwh, range_km):
        self.car = Car(brand, model, price)          # «содержит» автомобиль
        self.battery = Battery(battery_kwh, range_km)  # и батарею

    # Нужное поведение явно делегируем вложенному объекту — больше кода
    def info(self):
        return f"{self.car.info()}, {self.battery.info()}"

    def tax(self):
        return 0  # льгота для электромобилей — решаем сами, что «пробрасывать»

    @property
    def brand(self):
        return self.car.brand

    def replace_battery(self, new_battery):
        # Гибкость композиции: часть можно заменить во время работы
        self.battery = new_battery


tesla_inh = ElectricCarInh("Tesla", "Model 3", 4_200_000, 75, 500)
tesla_comp = ElectricCarComp("Tesla", "Model 3", 4_200_000, 75, 500)

print("Наследование:")
print("  ", tesla_inh.info())
print("   налог:", tesla_inh.tax())
print("   isinstance(..., Car):", isinstance(tesla_inh, Car))  # True — «является» Car

print("Композиция:")
print("  ", tesla_comp.info())
print("   налог:", tesla_comp.tax())
print("   isinstance(..., Car):", isinstance(tesla_comp, Car))  # False — «содержит» Car
tesla_comp.replace_battery(Battery(100, 650))
print("   после замены батареи:", tesla_comp.info())

# Сравнение:
# Наследование («является»: ElectricCar — это Car)
#   + мало кода: конструктор и методы родителя переиспользуются;
#   + объект подходит везде, где ожидается Car (полиморфизм, isinstance);
#   − жёсткая связь: изменения в Car автоматически влияют на наследника,
#     в том числе нежелательные (метод refuel());
#   − наследник получает ВСЁ от родителя, нельзя взять только часть;
#   − иерархия фиксируется при написании кода и плохо меняется;
#     глубокие цепочки наследования трудно читать.
# Композиция («имеет»: ElectricCar имеет Car и Battery)
#   + гибкость: части можно заменять, комбинировать и подменять в тестах;
#   + слабая связь: наружу видно только то, что мы явно делегировали;
#   + не нужно притворяться тем, чем объект не является;
#   − больше кода: методы, которые нужны снаружи, приходится
#     пробрасывать вручную (info, brand);
#   − объект не проходит проверки isinstance(x, Car).
#
# Когда что выбирать:
# - наследование — когда отношение действительно «является» и
#   поведение родителя подходит наследнику целиком (Sedan — это Car;
#   свои исключения — наследники Exception);
# - композиция — когда отношение «имеет» или «использует» (у машины есть
#   двигатель, батарея), когда части нужно менять или комбинировать.
# Известное правило: «предпочитайте композицию наследованию», а
# наследование используйте там, где оно очевидно уместно.
#
# Примеры:
# - стандартная библиотека, наследование: иерархия исключений
#   (KeyError → LookupError → Exception), collections.OrderedDict(dict),
#   классы из socketserver, наследование от threading.Thread;
# - стандартная библиотека, композиция: io.TextIOWrapper содержит
#   бинарный буфер, logging.Logger содержит список Handler'ов,
#   queue.Queue внутри хранит deque и блокировки;
# - фреймворки: в Django модели наследуются от models.Model, но поля
#   модели — это композиция (CharField, ForeignKey); в играх компоненты
#   (движение, здоровье, оружие) собираются композицией вместо огромных
#   иерархий персонажей.
