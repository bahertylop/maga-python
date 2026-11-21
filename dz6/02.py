r"""
**Задача 2 (создание DataFrame, атрибуты, просмотр).** Автосалон хранит 20 автомобилей: `vin`, `model` (Camry, X5, Model 3, Rio, Solaris), `brand` (Toyota, BMW, Tesla, Kia, Hyundai), `price`, `year`. Создайте DataFrame из словаря с сохранением типов. Выведите `shape`, `columns`, `index`, `dtypes`. Выполните просмотр: `head(3)`, `tail(2)`, `sample(3, random_state=42)`, `describe()`, `describe(include="all")`. Ожидаемый вывод: `shape=(20, 5)`; `dtypes` показывает `model=str`, `brand=str`, `price=int64`, `year=int64`; `describe()` возвращает статистику только для `price` и `year`; `describe(include="all")` — для всех столбцов. В комментариях объясните: чем `describe()` для числовых столбцов отличается от `describe(include="all")` (какие дополнительные статистики появляются для строк: `count`, `unique`, `top`, `freq`); что показывает `info()` помимо типов (число не-пустых значений, объём памяти); чем `sample()` предпочтительнее `head()` при первичном осмотре (не смещён к началу файла, если данные отсортированы по бренду); почему `shape` — кортеж, а `size` — число; что произойдёт при `pd.DataFrame({...})`, если все списки разной длины (`ValueError`); как `dtypes` помогает обнаружить проблему с типами после чтения CSV (например, `price` стал `object` из-за пробелов или запятых).
"""
import pandas as pd

models = ["Camry", "X5", "Model 3", "Rio", "Solaris"]
brands = ["Toyota", "BMW", "Tesla", "Kia", "Hyundai"]
df = pd.DataFrame({
    "vin": [f"VIN{i:05d}" for i in range(20)],
    "model": [models[i % 5] for i in range(20)],
    "brand": [brands[i % 5] for i in range(20)],
    "price": [1_000_000 + i * 150_000 for i in range(20)],
    "year": [2005 + i for i in range(20)],
})
print("shape", df.shape, "| columns", list(df.columns), "| index", df.index)
print(df.dtypes)                       # model/brand/vin - str (Pandas 3), price/year - int64
print(df.head(3)); print(df.tail(2)); print(df.sample(3, random_state=42))
print(df.describe())                   # только числовые столбцы: price, year
print(df.describe(include="all"))      # + для строк: count, unique, top, freq
df.info()                              # число не-пустых значений и объём памяти
# describe() для чисел: count/mean/std/min/квартили/max; include="all" добавляет для строк
# count, unique, top (самое частое), freq (его частота). info() показывает ещё и память.
# sample() предпочтительнее head() при первичном осмотре: данные часто отсортированы
# (по бренду/дате), head увидит только начало, sample - случайную выборку.
# shape - кортеж (строки, столбцы), size - число (строки*столбцы).
try:
    pd.DataFrame({"a": [1, 2, 3], "b": [1, 2]})
except ValueError as e:
    print("разная длина ->", e)
# dtypes помогает ловить проблемы после read_csv: если price стал object/str - в данных есть
# пробелы, запятая вместо точки или текст ("1 500 000", "н/д").
