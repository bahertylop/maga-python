"""
Задача 17 (собственные исключения). В автосалоне возможна ситуация, когда
покупатель просит автомобиль, которого нет в наличии. Стандартные исключения
тут не подходят — нужно своё, говорящее. Создайте собственное исключение
CarNotFoundError(Exception) и используйте его в классе Dealership
(автосалон). Метод find_car(brand, model) должен возвращать автомобиль, если
он есть, и выбрасывать CarNotFoundError с понятным сообщением (например, с
указанием марки и модели), если автомобиля нет. Продемонстрируйте обработку
исключения через try/except и объясните, зачем создавать собственные
исключения вместо использования стандартных — как это помогает ловить
именно свои ошибки и отделять их от чужих.
"""


class CarNotFoundError(Exception):
    """Автомобиль с указанной маркой и моделью отсутствует в салоне."""

    def __init__(self, brand, model):
        self.brand = brand
        self.model = model
        super().__init__(f"Автомобиль {brand} {model} отсутствует в наличии")


class Car:
    def __init__(self, brand, model, price):
        self.brand = brand
        self.model = model
        self.price = price

    def __str__(self):
        return f"{self.brand} {self.model} — {self.price:,} ₽".replace(",", " ")


class Dealership:
    def __init__(self, name):
        self.name = name
        self.cars = []

    def add_car(self, car):
        self.cars.append(car)

    def find_car(self, brand, model):
        for car in self.cars:
            if car.brand.lower() == brand.lower() and car.model.lower() == model.lower():
                return car
        raise CarNotFoundError(brand, model)


salon = Dealership("АвтоМир")
salon.add_car(Car("Toyota", "Camry", 2500000))
salon.add_car(Car("Kia", "Rio", 1800000))

for brand, model in [("Toyota", "Camry"), ("BMW", "X5")]:
    try:
        car = salon.find_car(brand, model)
        print("Найден:", car)
    except CarNotFoundError as e:
        print("Ошибка:", e)
        # У своего исключения есть свои поля — их можно использовать дальше
        print(f"  → предложим клиенту оформить предзаказ на {e.brand} {e.model}")

# Зачем свои исключения вместо стандартных:
# 1. Говорящее имя. CarNotFoundError сразу объясняет, что случилось,
#    в отличие от безликого ValueError или KeyError.
# 2. Точная обработка. except CarNotFoundError ловит ТОЛЬКО нашу ситуацию
#    «машины нет». Если в коде случится настоящая ошибка (опечатка, KeyError,
#    TypeError), она не будет случайно «проглочена» и не замаскируется
#    под «машины нет» — мы её увидим.
# 3. Дополнительные данные. В исключение можно положить поля (brand, model)
#    и использовать их в обработчике.
# 4. Иерархия. Можно сделать базовый DealershipError и наследовать от него
#    все ошибки салона — тогда их можно ловить все сразу одним except.
