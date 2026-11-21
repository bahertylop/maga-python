r"""
**Задача 39 (статистика, cov/corr).** Создайте Series цен автомобилей. Вычислите `mean`, `median`, `std(ddof=0)`, `std(ddof=1)`, `var`, `quantile([0.25, 0.5, 0.75])`. Создайте DataFrame метрик 365×5 (показатели моделей: цена, пробег, расход, мощность, возраст). Вычислите `cov()`, `corr()`, `corr(method="spearman")`. Проверьте симметричность `corr` через `(corr == corr.T).all().all()`. Ожидаемый вывод: `std(ddof=1)` больше `std(ddof=0)`; `corr` симметрична, диагональ — единицы; `corr(method="spearman")` даёт ранговую корреляцию. В комментариях объясните: когда `ddof=1` (выборочное стандартное отклонение, по умолчанию в Pandas); почему медиана устойчива к выбросам (50-й перцентиль); чем `cov` отличается от `corr` (масштаб vs нормировка); как `spearman` обрабатывает нелинейные зависимости; что произойдёт при `corr` с `NaN` (по умолчанию pairwise-исключение); как `quantile` интерполирует между точками (по умолчанию линейно).
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(39)
prices = pd.Series(rng.normal(2.5e6, 6e5, 200)); prices.iloc[0] = 3e7
print("mean:", round(prices.mean()), "| median:", round(prices.median()), "(выброс сильно сдвигает mean)")
print("std ddof=0:", round(prices.std(ddof=0)), "| ddof=1:", round(prices.std(ddof=1)), "| var:", round(prices.var()))
print("quantile:", prices.quantile([0.25, 0.5, 0.75]).round(0).tolist(), "| linear/nearest:", prices.quantile(0.3), prices.quantile(0.3, interpolation="nearest"))
m = pd.DataFrame(rng.normal(size=(365, 5)), columns=["price", "mileage", "consumption", "power", "age"])
m["power"] += 0.8 * m["price"]; m["age"] = np.exp(m["mileage"])
print(m.cov().round(2)); corr = m.corr(); print(corr.round(2))
print("симметрична:", (corr == corr.T).all().all(), "| диагональ=1:", np.allclose(np.diag(corr), 1))
print("pearson(age,mileage):", round(m["age"].corr(m["mileage"]), 3), "| spearman:", round(m["age"].corr(m["mileage"], method="spearman"), 3))
m2 = m.copy(); m2.iloc[:100, 0] = np.nan; print("corr с NaN (pairwise):", round(m2.corr().loc["price", "power"], 3))
print("min_periods=300:", m2.corr(min_periods=300).loc["price", "power"])
# ddof=1 - выборочное (несмещённое) стандартное отклонение, по умолчанию в Pandas (в NumPy по умолчанию ddof=0).
# Медиана - 50-й перцентиль, зависит от порядка, а не от величины крайних значений -> устойчива к выбросам.
# cov зависит от масштаба переменных, corr - нормированная ковариация в [-1, 1] (безразмерная).
# Spearman = Pearson по рангам: ловит любую МОНОТОННУЮ зависимость (age=exp(mileage) -> ровно 1).
# corr с NaN исключает пропуски попарно (для каждой пары столбцов отдельно), min_periods требует минимум общих наблюдений.
# quantile между наблюдениями интерполирует (linear по умолчанию; lower/higher/nearest/midpoint).
