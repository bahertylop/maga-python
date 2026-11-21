r"""
**Задача 55 (PyArrow: dtype_backend).** Создайте CSV на 1 000 000 строк со строковым столбцом (названия моделей). Прочитайте с `dtype_backend="pyarrow"` и без — сравните `dtypes`, время, память. Примените `.str.lower()` на `str` (PyArrow) vs `object`. Ожидаемый вывод: с `dtype_backend="pyarrow"` строки имеют `dtype=string[pyarrow]`; скорость `.str.lower()` в 5–6× выше; память в 2 раза меньше. В комментариях объясните: когда `dtype_backend="pyarrow"` даёт максимальный выигрыш (большие строковые столбцы с моделями); как `str`-dtype (3.0) связан с PyArrow (нативный строковый тип); почему без PyArrow fallback на `object` (медленные Python-строки); что произойдёт при `dtype_backend="pyarrow"` на числовых (тоже ускоряет); как PyArrow влияет на Parquet (нативное чтение/запись); как сравнить производительность корректно.
"""
import time
import numpy as np
import pandas as pd
from pathlib import Path

try:
    import pyarrow  # noqa: F401
    HAVE_PA = True
except ImportError:
    HAVE_PA = False
rng = np.random.default_rng(55)
N = 1_000_000
models = np.array(["Toyota Camry", "BMW X5", "Kia Rio", "Audi A6", "Lada Vesta", "Skoda Octavia"])
path = Path(__file__).parent / "models.csv"
pd.DataFrame({"model": rng.choice(models, N), "price": rng.integers(5e5, 5e6, N)}).to_csv(path, index=False)
def tm(f):
    f(); t0 = time.perf_counter(); r = f(); return r, time.perf_counter() - t0
base, tb = tm(lambda: pd.read_csv(path))
print("по умолчанию: dtypes =", dict(base.dtypes.astype(str)), f"| чтение {tb:.2f} с | память {base.memory_usage(deep=True).sum()/1e6:.1f} МБ")
_, ts = tm(lambda: base["model"].str.lower())
print(f"str.lower() на dtype {base['model'].dtype}: {ts*1e3:.0f} мс")
obj = base.astype({"model": object})
_, to = tm(lambda: obj["model"].str.lower())
print(f"str.lower() на object: {to*1e3:.0f} мс")
if HAVE_PA:
    pa_df, tpa = tm(lambda: pd.read_csv(path, dtype_backend="pyarrow"))
    print("dtype_backend='pyarrow': dtypes =", dict(pa_df.dtypes.astype(str)), f"| чтение {tpa:.2f} с | память {pa_df.memory_usage(deep=True).sum()/1e6:.1f} МБ")
    _, tl = tm(lambda: pa_df["model"].str.lower()); print(f"str.lower() на pyarrow: {tl*1e3:.0f} мс")
else:
    print("pyarrow НЕ установлен: ветка dtype_backend='pyarrow' пропущена (pip install pyarrow) - в Pandas 3 строки тогда хранятся в собственном str-dtype на object-хранилище.")
path.unlink()
# dtype_backend="pyarrow" особенно выгоден для больших СТРОКОВЫХ столбцов (названия моделей): строки лежат одним буфером Arrow,
# а не миллионом Python-объектов -> память в разы меньше, str-операции быстрее. В Pandas 3.0 dtype "str" по умолчанию использует
# PyArrow как хранилище, если он установлен (иначе - fallback на object-хранилище: медленные Python-строки). Числовые столбцы
# с pyarrow тоже ускоряются/экономятся и поддерживают пропуски без приведения к float (nullable-типы int64[pyarrow]).
# Parquet (pandas <-> Arrow) читается/пишется нативно, без промежуточных преобразований. Сравнивать честно: прогрев, одинаковые данные,
# несколько прогонов; результаты зависят от версии pandas/pyarrow и машины - цифры из задания (5-6x, в 2 раза) ориентировочные.
