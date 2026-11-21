
"""
**Задача 7 (память: memory_usage, Parquet, категории).** Создайте DataFrame из 1 000 000 строк: `sale_id` (int64), `rating` (float64), `mileage` (int64). Выведите `memory_usage(deep=True)` в МБ. Понизьте типы через `pd.to_numeric(..., downcast=...)`: `sale_id` → `int32`, `rating` → `float32`, `mileage` → `uint32`. Сравните память. Добавьте `city` (Москва/СПб/Казань/Екатеринбург) из 4 значений — сравните `memory_usage(deep=True)` для `str` и `category`. Сохраните оба варианта в CSV и Parquet. Ожидаемый вывод: исходно ≈15.26 МБ, после понижения ≈4.77 МБ; `category` для `city` экономит ≈96% памяти относительно `str`; Parquet в 2–5 раз меньше CSV и в 3–10 раз быстрее. В комментариях объясните: во сколько раз `uint32` экономнее `float64` (в 2 раза); в каких случаях `category` хуже `str` (высокая кардинальность — много уникальных VIN или моделей); почему `memory_usage(deep=True)` строкового столбца превышает `nbytes` (учитывает объекты Python-строк); как `downcast` выбирает тип (минимальный, вмещающий все значения); почему Parquet сохраняет `category` и `datetime`, а CSV — нет (Parquet хранит метаданные и типы).
"""
import time
import numpy as np
import pandas as pd
from pathlib import Path

HERE = Path(__file__).parent
rng = np.random.default_rng(7)
n = 1_000_000
df = pd.DataFrame({"sale_id": np.arange(n), "rating": rng.uniform(1, 5, n), "mileage": rng.integers(0, 500_000, n)})
MB = 1024 ** 2
base = df.memory_usage(deep=True).sum() / MB
small = df.astype({"sale_id": "int32", "rating": "float32", "mileage": "uint32"})
print(f"память: {base:.2f} МБ -> {small.memory_usage(deep=True).sum() / MB:.2f} МБ")
# downcast: сам выбирает МИНИМАЛЬНЫЙ тип, вмещающий все значения (может дать и int8/uint16)
auto = pd.to_numeric(df["mileage"], downcast="unsigned")
print("to_numeric downcast:", df["mileage"].dtype, "->", auto.dtype)

df["city"] = rng.choice(["Москва", "СПб", "Казань", "Екатеринбург"], n)
s_str = df["city"].memory_usage(deep=True) / MB
s_cat = df["city"].astype("category").memory_usage(deep=True) / MB
print(f"city: str {s_str:.2f} МБ | category {s_cat:.2f} МБ ({1 - s_cat / s_str:.0%} экономии)")

csv = HERE / "tmp_cars.csv"
t = time.perf_counter(); df.to_csv(csv, index=False); print(f"CSV: {csv.stat().st_size / MB:.1f} МБ, запись {time.perf_counter() - t:.2f} с")
try:
    pq = HERE / "tmp_cars.parquet"
    t = time.perf_counter(); df.assign(city=df["city"].astype("category")).to_parquet(pq); w = time.perf_counter() - t
    t = time.perf_counter(); pd.read_parquet(pq); r = time.perf_counter() - t
    t = time.perf_counter(); pd.read_csv(csv); rc = time.perf_counter() - t
    print(f"Parquet: {pq.stat().st_size / MB:.1f} МБ, запись {w:.2f} с, чтение {r:.2f} с vs CSV {rc:.2f} с; category сохранён:", pd.read_parquet(pq)["city"].dtype)
    pq.unlink()
except ImportError:
    print("Parquet пропущен: нужен pyarrow (python -m pip install pyarrow)")
csv.unlink()
# uint32 (4 байта) экономнее float64 (8 байт) в 2 раза. category хуже str при высокой кардинальности (много уникальных VIN/моделей):
# словарь категорий становится почти таким же большим, как сами строки + коды.
# deep=True у str-столбца учитывает объекты Python-строк (иначе видны только указатели), поэтому оценка больше nbytes.
# Parquet хранит схему (category, datetime) в метаданных; CSV - просто текст, типы теряются при чтении.
