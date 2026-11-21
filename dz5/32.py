"""
**Задача 32 (статистика).** Дан массив цен за год формы `(365,)`. Вычислите:
- `mean`, `median`, `std`, `var`, `min`, `max`, `ptp`;
- `std(ddof=0)` vs `std(ddof=1)`;
- `np.percentile(prices, [25, 50, 75])` — квартили;
- `np.quantile(prices, [0.1, 0.9])` — децили.

Для матрицы `(365, 5)` — среднее и std по характеристикам (`axis=0`) и по моделям (`axis=1`). **Что продемонстрировать:** все статистики и разницу `ddof`. **Вопросы:** когда `ddof=1` предпочтительнее; почему медиана устойчива к выбросам (пример: один автомобиль за 50 000 000); как `quantile` связан с `percentile`; почему `ptp` = `max - min`.
"""
import numpy as np

rng = np.random.default_rng(32)
prices = rng.normal(2e6, 5e5, 365)
print(f"mean={prices.mean():.0f} median={np.median(prices):.0f} std={prices.std():.0f} var={prices.var():.3e} "
      f"min={prices.min():.0f} max={prices.max():.0f} ptp={np.ptp(prices):.0f}")
print("ddof=0:", prices.std(ddof=0).round(1), "| ddof=1:", prices.std(ddof=1).round(1))
print("квартили:", np.percentile(prices, [25, 50, 75]).round(0), "| децили 10/90:", np.quantile(prices, [0.1, 0.9]).round(0))

data = rng.normal([2e6, 150, 8, 2.0, 1500], [5e5, 30, 2, 0.5, 200], size=(365, 5))
print("по характеристикам (axis=0): mean", data.mean(axis=0).round(1), "std", data.std(axis=0).round(1))
print("по моделям (axis=1) shape:", data.mean(axis=1).shape)
# ddof=0 - дисперсия «генеральной» совокупности (делим на n), ddof=1 - несмещённая оценка
# по ВЫБОРКЕ (делим на n-1): предпочтительна, когда данные - выборка из большего целого
# (почти всегда). Медиана устойчива к выбросам: один автомобиль за 50 млн сильно сдвигает
# среднее, но почти не двигает медиану.
with_outlier = np.append(prices, 50_000_000)
print(f"с выбросом: mean {prices.mean():.0f} -> {with_outlier.mean():.0f} | median {np.median(prices):.0f} -> {np.median(with_outlier):.0f}")
# quantile принимает доли 0..1, percentile - проценты 0..100 (одно и то же: q=0.9 == p=90).
# ptp (peak to peak) = max - min: размах. (ndarray.ptp удалён в NumPy 2 - используйте np.ptp.)
print("quantile == percentile:", np.allclose(np.quantile(prices, 0.9), np.percentile(prices, 90)))
