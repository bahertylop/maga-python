r"""
**Задача 29 (rolling).** Создайте временной ряд из 100 дней (продажи автомобилей). Примените `rolling(7).mean()`, `rolling(7, min_periods=1).mean()`, `rolling(7, center=True).mean()`, `rolling(7, win_type="triang").mean()`, `rolling("30D").sum()`, `rolling("5B").mean()`. Примените `.agg(["mean", "std"])` и `.apply(np.percentile(x, 90), raw=True)`. Ожидаемый вывод: `rolling(7).mean()` — первые 6 значений `NaN`; `min_periods=1` — без `NaN`; `center=True` — метка в центре окна; `rolling("30D")` требует `DatetimeIndex`. В комментариях объясните: чем `center=True` отличается (окно центрируется на текущей точке, а не заканчивается в ней); когда `raw=True` ускоряет `apply` (передаёт NumPy-массив вместо Series); как `win_type` меняет веса (треугольное, гауссово окно); почему временные окна требуют `DatetimeIndex`; что произойдёт при `min_periods > window` (все значения `NaN`); как `closed` влияет на включение границ (`"right"`, `"left"`, `"both"`, `"neither"`).
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(29)
s = pd.Series(rng.integers(5, 30, 100).astype(float), index=pd.date_range("2025-01-01", periods=100))
print("rolling(7) первые NaN:", s.rolling(7).mean().isna().sum(), "| min_periods=1:", s.rolling(7, min_periods=1).mean().isna().sum())
print("center=True метка в центре:", s.rolling(7, center=True).mean().iloc[3].round(2), "== среднее окна 0..6:", s.iloc[:7].mean().round(2))
print("triang:", s.rolling(7, win_type="triang").mean().iloc[6].round(2), "(нужен scipy)")
print("rolling('30D').sum:", s.rolling("30D").sum().iloc[-1])
try:
    s.rolling("5B").mean()
except ValueError as e:
    print("rolling('5B') ->", e)
print("agg:", s.rolling(7).agg(["mean", "std"]).iloc[-1].round(2).to_dict())
print("apply percentile raw=True:", s.rolling(7).apply(lambda x: np.percentile(x, 90), raw=True).iloc[-1])
try:
    s.rolling(7, min_periods=10).mean()
except ValueError as e:
    print("min_periods > window ->", e)
for closed in ("right", "left", "both", "neither"):
    print(f"closed={closed:8s}", s.rolling("3D", closed=closed).sum().iloc[5])
try:
    pd.Series(range(5)).rolling("3D").sum()
except (ValueError, TypeError) as e:
    print("временное окно без DatetimeIndex ->", type(e).__name__)
# center=True: окно ЦЕНТРИРУЕТСЯ на текущей точке (а не заканчивается в ней). raw=True передаёт в функцию ndarray вместо Series:
# быстрее. win_type меняет веса окна (triang, gaussian...). Временные окна ("30D") требуют DatetimeIndex (окно задано
# календарной длиной), "5B" - не фиксированная частота -> ошибка. min_periods > window -> ValueError. closed определяет,
# включаются ли границы окна (right - по умолчанию).
