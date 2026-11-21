r"""
**Задача 57 (Dask/Polars/Vaex).** Создайте DataFrame 100 000 строк, сохраните в `huge.csv` и `huge.hdf5`. Для Dask: `dd.read_csv("huge.csv")`, `df.groupby("brand")["sales"].sum().compute()` — сравните время с Pandas. Для Polars: `pl.read_csv("huge.csv")`, `df.group_by("brand").agg(pl.col("sales").sum())` — зафиксируйте разницу синтаксиса и скорость. Для Vaex: `vaex.open("huge.hdf5")`, `df[df["sales"] > 1000].groupby("brand", agg="sum")`. Ожидаемый вывод: Dask ленив — вычисления только при `.compute()`; Polars в 2–10× быстрее Pandas; Vaex не загружает файл в память. В комментариях объясните: когда Pandas перестаёт справляться (данные не влезают в RAM); чем Dask отличается от Polars (ленивые вычисления vs быстрый Rust-движок); зачем Vaex нужен memory-mapping (работа с файлом на диске); как `.compute()` запускает вычисления; как Polars использует многоядерность; что такое out-of-core (вычисления вне RAM).
"""
import time
import numpy as np
import pandas as pd
from pathlib import Path

rng = np.random.default_rng(57)
N = 100_000
here = Path(__file__).parent
pdf = pd.DataFrame({"brand": rng.choice(["Toyota", "BMW", "Kia", "Audi"], N), "sales": rng.integers(0, 5000, N)})
csv = here / "huge.csv"; pdf.to_csv(csv, index=False)
t0 = time.perf_counter(); base = pd.read_csv(csv).groupby("brand")["sales"].sum(); t_pd = time.perf_counter() - t0
print(f"Pandas: {t_pd*1e3:.1f} мс\n", base.to_dict())
try:
    import dask.dataframe as dd
    t0 = time.perf_counter(); lazy = dd.read_csv(csv).groupby("brand")["sales"].sum(); t_lazy = time.perf_counter() - t0
    res = lazy.compute(); print(f"Dask: построение графа {t_lazy*1e3:.1f} мс (ленивое), compute {time.perf_counter()-t0:.2f} с", res.to_dict())
except ImportError:
    print("Dask не установлен (pip install 'dask[dataframe]'): пример -> dd.read_csv('huge.csv').groupby('brand')['sales'].sum().compute()")
try:
    import polars as pl
    t0 = time.perf_counter(); out = pl.read_csv(csv).group_by("brand").agg(pl.col("sales").sum()); t_pl = time.perf_counter() - t0
    print(f"Polars: {t_pl*1e3:.1f} мс\n", out)
except ImportError:
    print("Polars не установлен (pip install polars): pl.read_csv('huge.csv').group_by('brand').agg(pl.col('sales').sum())")
try:
    import vaex
    h5 = here / "huge.hdf5"; vaex.from_pandas(pdf).export_hdf5(str(h5))
    v = vaex.open(str(h5)); print(v[v["sales"] > 1000].groupby("brand", agg="sum")); h5.unlink()
except ImportError:
    print("Vaex не установлен (pip install vaex): vaex.open('huge.hdf5'); df[df['sales'] > 1000].groupby('brand', agg='sum')")
csv.unlink()
# Pandas перестаёт справляться, когда данные не помещаются в RAM (часто нужен запас x3-5 от размера файла из-за промежуточных копий).
# Dask - ленивые вычисления + разбиение на партиции: строится граф задач, реально считается при .compute(), параллелит по ядрам и
# умеет out-of-core. Polars - быстрый движок на Rust (многопоточность, SIMD, ленивый режим scan_csv + оптимизатор запросов),
# синтаксис выражений pl.col(...). Vaex использует memory-mapping: файл (HDF5/Arrow) отображается в память на диске и страницы
# подгружаются по требованию, поэтому файл целиком в RAM не загружается; операции ленивые. Out-of-core = вычисления над данными,
# которые не помещаются в RAM (чтение и обработка кусками с диска). Ускорение Polars (2-10x) зависит от задачи и числа ядер.
# ВАЖНО: Dask/Polars/Vaex в окружении, где писались решения, не были установлены - эти ветки не запускались (только Pandas-базовая линия).
