r"""
**Задача 35 (resample/shift/diff/pct_change).** Создайте DataFrame с `DatetimeIndex` (2 года ежедневных продаж). Примените `resample("ME").agg(total=("revenue", "sum"), avg=("revenue", "mean"))`, `resample("QE").size()`, `resample("D").ffill()` (upsampling). Примените `shift(1)`, `shift(-1)`, `diff()`, `pct_change() * 100`. Примените `groupby("customer_id").transform(lambda x: x.rolling(7).sum())`. Ожидаемый вывод: `resample("ME").agg` даёт 24 строки; `shift(1)` сдвигает значения, `shift(-1)` — в обратную сторону; `diff()` даёт разности, `pct_change()` — проценты; `ffill()` при upsampling копирует значение вперёд. В комментариях объясните: чем downsampling отличается от upsampling (агрегация vs интерполяция/заполнение); когда `ffill` лучше `interpolate` (для категориальных/дискретных данных); как `pct_change` используется в финансах (рост выручки автосалона); почему `shift` с `freq` сдвигает индекс, а не данные (календарный сдвиг); что произойдёт при `resample` без `DatetimeIndex` (`TypeError`); как `resample` связан с `groupby` (по сути — группировка по временным интервалам).
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(35)
idx = pd.date_range("2023-01-01", periods=730, freq="D")
df = pd.DataFrame({"revenue": rng.normal(5e6, 1e6, 730), "customer_id": rng.integers(1, 4, 730)}, index=idx)
m = df.resample("ME").agg(total=("revenue", "sum"), avg=("revenue", "mean"))
print("месяцев:", len(m), "| кварталы:", df.resample("QE").size().tolist())
print("upsampling ffill:", df["revenue"].resample("12h").ffill().shape)
print("shift(1)/shift(-1):", df["revenue"].shift(1).iloc[1].round(0) == df["revenue"].iloc[0].round(0), df["revenue"].shift(-1).iloc[0].round(0) == df["revenue"].iloc[1].round(0))
print("diff:", df["revenue"].diff().iloc[1].round(0), "| pct_change %:", (df["revenue"].pct_change() * 100).iloc[1].round(2))
print("shift(freq='D') сдвигает ИНДЕКС:", df["revenue"].shift(1, freq="D").index[0].date())
df["roll7"] = df.groupby("customer_id")["revenue"].transform(lambda x: x.rolling(7).sum())
try:
    pd.DataFrame({"x": [1, 2, 3]}).resample("D")
except TypeError as e:
    print("resample без DatetimeIndex ->", type(e).__name__)
# downsampling (D -> ME) АГРЕГИРУЕТ данные, upsampling (D -> 12h) создаёт новые метки, которые надо заполнить (ffill/interpolate).
# ffill лучше interpolate для дискретных/категориальных данных. pct_change - темп роста (в финансах - рост выручки автосалона).
# shift(n) двигает ДАННЫЕ относительно индекса; shift(n, freq=...) двигает сам ИНДЕКС. resample требует DatetimeIndex/PeriodIndex/
# TimedeltaIndex (или on=столбец дат). resample - по сути groupby по временным корзинам.
