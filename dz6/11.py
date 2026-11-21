r"""
**Задача 11 (Parquet, сжатие, фильтры).** Сохраните DataFrame продаж в Parquet. Сравните размер файла и скорость чтения с CSV через `time.perf_counter()` (прогрев + 5 замеров). Прочитайте Parquet с `columns=["sale_id", "sale_date"]` — сравните с полным чтением. Прочитайте с `filters=[("sale_date", ">=", "2025-01-01")]` — проверьте `len(result)`. Сохраните в три сжатых CSV: `compression="gzip"`, `"bz2"`, `"xz"`. Ожидаемый вывод: Parquet в 2–5 раз меньше CSV и в 3–10 раз быстрее; `columns=[...]` ускоряет чтение в 2–3 раза; `filters` возвращает только подходящие строки; `xz` даёт наименьший размер, `gzip` — баланс. В комментариях объясните: почему Parquet быстрее и компактнее (колоночное хранение, сжатие по столбцам); как фильтры работают без чтения всего файла (predicate pushdown — статистика min/max в row groups); какой компрессор даёт лучший размер (`xz`, но медленный); почему Parquet сохраняет `category` и `datetime`; как `columns` влияет на объём (читаются только нужные колонки); в каких случаях `filters` не сработает (фильтр по несортированному столбцу без статистики, сложные выражения).
"""
import time
import numpy as np
import pandas as pd
from pathlib import Path

HERE = Path(__file__).parent
rng = np.random.default_rng(11)
n = 400_000
df = pd.DataFrame({"sale_id": np.arange(n), "sale_date": pd.Timestamp("2024-01-01") + pd.to_timedelta(rng.integers(0, 700, n), unit="D"),
                   "amount": rng.uniform(5e5, 5e6, n)})

def bench(fn, repeat=5):
    fn()                                    # прогрев
    best = 1e9
    for _ in range(repeat):
        t = time.perf_counter(); fn(); best = min(best, time.perf_counter() - t)
    return best

csv = HERE / "sales_big.csv"; df.to_csv(csv, index=False)
print(f"CSV: {csv.stat().st_size / 1e6:.1f} МБ, чтение {bench(lambda: pd.read_csv(csv)) * 1e3:.0f} мс")
for comp in ("gzip", "bz2", "xz"):
    f = HERE / f"sales_big.csv.{comp}"; df.to_csv(f, index=False, compression=comp)
    print(f"{comp:5s} {f.stat().st_size / 1e6:.1f} МБ"); f.unlink()
try:
    pq = HERE / "sales_big.parquet"; df.to_parquet(pq)
    print(f"Parquet: {pq.stat().st_size / 1e6:.1f} МБ, чтение {bench(lambda: pd.read_parquet(pq)) * 1e3:.0f} мс, "
          f"2 столбца {bench(lambda: pd.read_parquet(pq, columns=['sale_id', 'sale_date'])) * 1e3:.0f} мс")
    res = pd.read_parquet(pq, filters=[("sale_date", ">=", pd.Timestamp("2025-01-01"))])
    print("filters >= 2025-01-01:", len(res), "строк из", n)
    pq.unlink()
except ImportError:
    print("Parquet пропущен: нужен pyarrow (python -m pip install pyarrow)")
csv.unlink()
# Parquet быстрее и компактнее: данные хранятся КОЛОНКАМИ (однотипные значения сжимаются лучше),
# с кодированием/сжатием по столбцам; сохраняет типы (category, datetime). columns=[...] читает только нужные
# колонки. filters использует предикат-pushdown: в метаданных row groups лежат min/max, и блоки, где условие
# заведомо ложно, не читаются. Не поможет: фильтр по несортированному столбцу (min/max каждого блока охватывают всё),
# сложные выражения/функции. xz даёт наименьший размер, но медленный; gzip - баланс.
