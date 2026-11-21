r"""
**Задача 3 (подбор dtype, nullable-типы, переполнение).** Автосалон хранит три вида данных: год выпуска автомобиля (1990–2025), пробег в километрах (0–500000), расход топлива (3.0–25.0 л/100 км). Создайте DataFrame из 100 строк. Понизьте типы: `year` → `uint8` (осторожно: 2025 не влезет — обсудите), `mileage` → `uint32`, `fuel_consumption` → `float32` через `astype()`. Проверьте переполнение: `np.uint8(200) + np.uint8(100)`. Создайте `pd.Series([100, 200, None], dtype="Int64")` и сравните с `dtype="int64"`. Ожидаемый вывод: `np.uint8(200) + np.uint8(100) = 44`; `Int64`-Series сохраняет `None` как `pd.NA`, а `int64`-Series не может его создать; `memory_usage(deep=True)` после понижения типов сокращается примерно на 50%. В комментариях объясните: чем `Int64` отличается от `int64`; зачем нужен `pd.NA`; как переполнение `uint8` проявляется без ошибки (тихий wrap-around); почему для года выпуска `uint8` не подходит (максимум 255, а 2025 > 255), лучше `uint16`; в каких случаях `float32` недостаточно точен (расход топлива — да, но при усреднении тысяч замеров может накапливаться погрешность); как `astype("category")` дополнительно сокращает память для низкокардинальных строк (бренды, города, типы кузова).
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(3)
df = pd.DataFrame({"year": rng.integers(1990, 2026, 100), "mileage": rng.integers(0, 500_001, 100),
                   "fuel_consumption": rng.uniform(3.0, 25.0, 100).round(1)})
before = df.memory_usage(deep=True).sum()
print("max year:", df["year"].max(), "- в uint8 (0..255) НЕ влезает")
try:
    print("year -> uint8:", df["year"].astype("uint8").head(3).tolist(), "(тихий wrap-around!)")
except Exception as e:
    print("year -> uint8 ошибка:", type(e).__name__, e)
small = df.astype({"year": "uint16", "mileage": "uint32", "fuel_consumption": "float32"})
after = small.memory_usage(deep=True).sum()
print(f"память: {before} -> {after} байт ({1 - after / before:.0%} экономии)")

with np.errstate(over="ignore"):
    print("uint8(200) + uint8(100) =", np.uint8(200) + np.uint8(100), "(300 mod 256 = 44, без ошибки)")
s_na = pd.Series([100, 200, None], dtype="Int64")
print(s_na.tolist(), s_na.dtype)
try:
    pd.Series([100, 200, None], dtype="int64")
except (TypeError, ValueError) as e:
    print("int64 + None ->", type(e).__name__)
# Int64 (заглавная I) - nullable-тип Pandas: хранит целые + маску пропусков (pd.NA); int64 - NumPy, пропуск
# в нём невозможен (при None Pandas превращает столбец во float64 с NaN). pd.NA - единый маркер
# «значение отсутствует» для всех nullable-типов (Int64, string, boolean).
# Переполнение uint8 не даёт ошибки: арифметика C-подобная, результат берётся по модулю 256.
# Для года uint8 не подходит (макс. 255), хватает uint16 (до 65535).
# float32 даёт ~7 значащих цифр: для расхода топлива ок, но при усреднении миллионов замеров
# накапливается погрешность - агрегируйте в float64.
df["brand"] = rng.choice(["Toyota", "BMW", "Kia"], 100)
print("str vs category:", df["brand"].memory_usage(deep=True), "->", df["brand"].astype("category").memory_usage(deep=True))
