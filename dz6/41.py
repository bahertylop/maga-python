r"""
**Задача 41 (сортировка: sort/rank/nlargest/partition/searchsorted/lexsort).** Создайте Series цен автомобилей. Отсортируйте `sort_values()`, `sort_values(ascending=False)`. Примените `rank(ascending=False, method="min")`, `rank(method="dense")`. Примените `nlargest(3)`, `nsmallest(3)`. Создайте 1 000 000 значений — сравните `sort_values().tail(10)`, `nlargest(10)`, `np.partition(values, -10)[-10:]` через `time.perf_counter()`. Примените `np.searchsorted(bounds, prices)`. Примените `np.lexsort((prices, brands))`. Ожидаемый вывод: `rank(method="min")` для `[100, 100, 90]` — `[1, 1, 3]`; `partition` в 10–50 раз быстрее `sort` на 1M; `searchsorted` возвращает позицию для вставки. В комментариях объясните: почему `partition` O(n) (не сортирует полностью, только разделяет); как `searchsorted` с `side` обрабатывает границы (`"left"`/`"right"`); почему последний ключ `lexsort` — основной (сортировка по последнему, затем по предпоследнему); чем `rank` отличается от `argsort` (`rank` — позиция в отсортированном ряду, `argsort` — индексы); что произойдёт при `nlargest` с `keep="all"` (все равные максимальные); как `sort_values` обрабатывает `NaN` (по умолчанию в конец).
"""
import time
import numpy as np
import pandas as pd

p = pd.Series([2.5e6, 1.2e6, 4e6, 900000.0, 3.1e6])
print(p.sort_values().tolist(), p.sort_values(ascending=False).tolist())
r = pd.Series([100, 100, 90])
print("rank min:", r.rank(ascending=False, method="min").tolist(), "| dense:", r.rank(ascending=False, method="dense").tolist(), "| average:", r.rank(ascending=False).tolist())
print("nlargest(3):", p.nlargest(3).tolist(), "| nsmallest(3):", p.nsmallest(3).tolist())
rng = np.random.default_rng(41)
big = rng.random(1_000_000); sb = pd.Series(big)
def t(f):
    t0 = time.perf_counter(); f(); return time.perf_counter() - t0
ts, tn, tp = t(lambda: sb.sort_values().tail(10)), t(lambda: sb.nlargest(10)), t(lambda: np.partition(big, -10)[-10:])
print(f"sort_values: {ts*1e3:.1f} мс | nlargest: {tn*1e3:.1f} мс | partition: {tp*1e3:.1f} мс | sort/partition = {ts/tp:.1f}x")
bounds = np.array([1e6, 2.5e6, 4e6])
print("searchsorted:", np.searchsorted(bounds, np.array([5e5, 1e6, 3e6, 9e6])), "| side='right' для 1e6:", np.searchsorted(bounds, 1e6, side="right"), "| left:", np.searchsorted(bounds, 1e6))
brands = np.array(["Kia", "BMW", "Kia", "BMW"]); prices = np.array([3, 2, 1, 5])
order = np.lexsort((prices, brands))
print("lexsort (основной ключ бренд):", list(zip(brands[order].tolist(), prices[order].tolist())))
# partition - алгоритм introselect (как quickselect), O(n): лишь «разделяет» массив так, что k-й элемент стоит на своём месте,
# слева меньшие, справа большие - без полной сортировки (O(n log n)). Ускорение зависит от машины (обычно в разы-десятки раз).
# searchsorted требует отсортированный массив; side="left" возвращает позицию ПЕРЕД равными, "right" - ПОСЛЕ них.
# lexsort: ПОСЛЕДНИЙ ключ - основной (как в сортировке справа налево, ключи идут от младшего к старшему).
# rank(method="min") - равным значениям минимальный ранг (1,1,3), dense - без пропусков (1,1,2).
