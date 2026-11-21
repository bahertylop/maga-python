r"""
**Задача 54 (chunksize/usecols/dtype).** Создайте CSV на 500 000 строк (логи продаж). Прочитайте: целиком; через `chunksize=100_000` с агрегацией суммы; через `usecols=["sale_id", "amount"]`; через `dtype={"sale_id": "int32", "amount": "float32"}`. Сравните время и память (`memory_usage(deep=True)`). Ожидаемый вывод: `chunksize` даёт пиковую память ≈1/5 полного чтения; `usecols` сокращает память пропорционально числу столбцов; `dtype` уменьшает память в 2 раза для чисел. В комментариях объясните: когда `chunksize` обязателен (файл не влезает в память); как `usecols` экономит память; почему `dtype` при чтении лучше `astype` после (не создаётся промежуточный `object`); как агрегировать по чанкам (суммировать результаты); что произойдёт при `chunksize` больше размера файла (один чанк); как `nrows` помогает при тестировании (быстрая проверка структуры).
"""
import time
import tracemalloc
import numpy as np
import pandas as pd
from pathlib import Path

rng = np.random.default_rng(54)
N = 500_000
path = Path(__file__).parent / "sales_log.csv"
pd.DataFrame({"sale_id": np.arange(N), "amount": rng.uniform(1e5, 5e6, N).round(2), "brand": rng.choice(["Toyota", "BMW", "Kia", "Audi"], N),
              "city": rng.choice(["Москва", "СПб", "Казань"], N), "status": rng.choice(["completed", "cancelled"], N)}).to_csv(path, index=False)
def measure(f):
    tracemalloc.start(); t0 = time.perf_counter(); r = f(); dt = time.perf_counter() - t0
    peak = tracemalloc.get_traced_memory()[1]; tracemalloc.stop(); return r, dt, peak
full, t1, p1 = measure(lambda: pd.read_csv(path))
def chunked():
    total = 0.0
    for ch in pd.read_csv(path, chunksize=100_000):
        total += ch["amount"].sum()
    return total
tot, t2, p2 = measure(chunked)
cols, t3, p3 = measure(lambda: pd.read_csv(path, usecols=["sale_id", "amount"]))
typed, t4, p4 = measure(lambda: pd.read_csv(path, usecols=["sale_id", "amount"], dtype={"sale_id": "int32", "amount": "float32"}))
head, _, _ = measure(lambda: pd.read_csv(path, nrows=5))
print(f"{'способ':28s}{'время, с':>10s}{'пик памяти, МБ':>16s}{'размер df, МБ':>15s}")
for n, t, p, d in (("целиком", t1, p1, full), ("chunksize=100_000", t2, p2, None), ("usecols", t3, p3, cols), ("usecols+dtype(32 бита)", t4, p4, typed)):
    print(f"{n:28s}{t:10.2f}{p/1e6:16.1f}{(d.memory_usage(deep=True).sum()/1e6 if d is not None else float('nan')):15.1f}")
print("сумма по чанкам == сумме целиком:", np.isclose(tot, full["amount"].sum()), "| nrows=5:", head.shape)
print("chunksize больше файла -> чанков:", sum(1 for _ in pd.read_csv(path, chunksize=10_000_000)))
path.unlink()
# chunksize обязателен, когда файл НЕ влезает в память: читаем кусками и накапливаем результат (суммы складываем; для среднего
# храним сумму и счётчик). usecols читает только нужные столбцы -> память падает ~пропорционально их числу. dtype при чтении лучше
# astype после: данные сразу парсятся в нужный тип, не создаётся промежуточный полноразмерный float64/object. chunksize больше
# числа строк -> один чанк. nrows=5 - быстрая проверка структуры/типов без чтения всего файла.
# Замечание: float32 теряет точность (~7 значащих цифр) - для денег в копейках лучше float64 или целые копейки.
