r"""
**Задача 43 (np.where/select/clip).** Примените `np.where(prices < 500000, 500000, prices)`, `np.select([prices < 1000000, prices < 2500000, prices >= 2500000], ["бюджет", "стандарт", "премиум"], default="?")`, `np.clip(prices, 500000, 5000000)`. Сравните с `prices.where(prices >= 500000, 500000)` и `prices.mask(prices > 3000000, 3000000)`. Примените `np.log`, `np.sqrt`, `np.abs`, `np.round`, `np.cumsum`, `np.percentile`. Ожидаемый вывод: `np.where` и `.where` дают одинаковый результат; `np.select` возвращает `["бюджет", "стандарт", "премиум"]` по порядку; `np.clip` обрезает с обеих сторон; `np.log(0)` — `-inf`. В комментариях объясните: почему порядок условий в `select` важен (первое совпадение); когда `clip` лучше `where` (обрезать с двух сторон); чем `np.where` отличается от `.where()` (`np.where` возвращает NumPy-массив, `.where()` — Series); что вернёт `np.log` для 0 и отрицательных (`-inf`, `nan`); как `np.cumsum` связан с `expanding().sum()`; когда `np.select` предпочтительнее вложенного `np.where` (читаемость для 3+ условий).
"""
import numpy as np
import pandas as pd

prices = pd.Series([300000, 800000, 1500000, 2800000, 6000000.0])
w1 = np.where(prices < 500000, 500000, prices); w2 = prices.where(prices >= 500000, 500000)
print("np.where:", type(w1).__name__, "| .where:", type(w2).__name__, "| равны:", np.array_equal(w1, w2.to_numpy()))
seg = np.select([prices < 1000000, prices < 2500000, prices >= 2500000], ["бюджет", "стандарт", "премиум"], default="?")
print(seg.tolist())
print("clip:", np.clip(prices, 500000, 5000000).tolist(), "| mask:", prices.mask(prices > 3000000, 3000000).tolist())
with np.errstate(divide="ignore", invalid="ignore"):
    print("log(0), log(-1):", np.log(0.0), np.log(-1.0))
print("log:", np.log(prices).round(2).tolist()[:2], "| sqrt:", np.sqrt(prices).round(0).tolist()[:2], "| cumsum:", np.cumsum(prices).tolist()[:3])
print("abs:", np.abs(pd.Series([-1, 2])).tolist(), "| round:", np.round(pd.Series([1.234]), 1).tolist(), "| p90:", np.percentile(prices, 90))
print("порядок условий:", np.select([prices < 2500000, prices < 1000000], ["A", "B"], default="?").tolist()[:2], "(второе условие недостижимо)")
# select берёт ПЕРВОЕ совпавшее условие - поэтому условия идут от узких к широким; при перестановке частные случаи «съедаются».
# clip обрезает сразу с обеих сторон одним вызовом, where/mask - одну сторону (нужно два вызова). np.where возвращает ndarray
# (теряет индекс/метки), Series.where сохраняет Series; НО логика противоположна: .where оставляет значения там, где условие ИСТИННО,
# а np.where(cond, x, y) берёт x там, где истинно. np.log(0) = -inf (RuntimeWarning divide), np.log(отрицательного) = nan (invalid).
