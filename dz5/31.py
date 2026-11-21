"""
**Задача 31 (обработка NaN).** Дан массив цен с пропусками: `prices = np.array([2500000.0, 1800000.0, np.nan, 3200000.0, np.nan, 950000.0])`. Проверьте:
- `np.isnan(prices)` — маска;
- количество NaN;
- `prices.sum()` — `nan`;
- `np.nansum`, `np.nanmean`, `np.nanstd`.

Дополнительно: `np.nan_to_num(prices, nan=0.0)`; `np.isfinite(prices)`. **Что продемонстрировать:** «заражение» NaN и обход. **Вопросы:** почему агрегаты заражаются; когда `nan_to_num`, когда `nanmean`; что вернёт `nanmean` для массива из одних NaN; почему `np.isnan` не работает с целочисленными массивами; как обработать NaN в 2D через `np.nanmean(axis=0)`.
"""
import numpy as np
import warnings

prices = np.array([2500000.0, 1800000.0, np.nan, 3200000.0, np.nan, 950000.0])
mask = np.isnan(prices)
print("маска:", mask, "| NaN:", mask.sum())
print("sum() ->", prices.sum(), "(NaN «заражает»: любая арифметика с NaN даёт NaN)")
print("nansum:", np.nansum(prices), "nanmean:", np.nanmean(prices), "nanstd:", round(np.nanstd(prices), 1))
print("nan_to_num:", np.nan_to_num(prices, nan=0.0))
print("isfinite:", np.isfinite(prices))
# Агрегаты заражаются, потому что результат любой операции с NaN - NaN (NaN != NaN, нет
# «безопасного» числа). nan_to_num подставляет число (0, среднее) и ИЗМЕНЯЕТ данные
# (0 исказит среднее); nanmean просто игнорирует пропуски - данные не трогает.
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    print("nanmean из одних NaN:", np.nanmean(np.array([np.nan, np.nan])), "| предупреждение:", w[0].message)
# isnan для целочисленного массива РАБОТАЕТ (вернёт все False) - в int нельзя хранить NaN;
# ошибку (TypeError) он даёт на нечисловых типах (строки, object).
print("isnan(int):", np.isnan(np.array([1, 2, 3])))
try:
    np.isnan(np.array(["a", "b"]))
except TypeError as e:
    print("isnan(str) ->", type(e).__name__)
two_d = np.array([[1.0, np.nan], [3.0, 4.0]])
print("2D nanmean(axis=0):", np.nanmean(two_d, axis=0))
