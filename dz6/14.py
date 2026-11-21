r"""
**Задача 14 (срезы, Copy-on-Write, chained assignment).** Создайте Series из 30 цен автомобилей. Выполните срезы: `iloc[:7]`, `iloc[-7:]`, `iloc[10:20]`, `iloc[::2]`, `iloc[::-1]`. Создайте `subset = prices.iloc[2:5]`, измените `subset.iloc[0] = 999` — проверьте исходный Series. Попробуйте `prices.iloc[2:5][0] = 999`. Сравните `.loc["a":"c"]` и `.iloc[0:3]`. Ожидаемый вывод: `prices.iloc[10:20]` содержит 10 элементов (конечная позиция не включается); изменение `subset` не влияет на `prices` (CoW); `prices.iloc[2:5][0] = 999` вызывает `ChainedAssignmentError`. В комментариях объясните: почему в Pandas 3.0 chained assignment не работает (CoW запрещает неявные цепочки); в каких случаях `.copy()` всё ещё нужен (если нужно гарантированно независимое изменение); как `np.shares_memory` помогает проверить view; почему `.loc` включает конечную метку, а `.iloc` — нет; что произойдёт при `.iloc` с шагом 0 (`ValueError`); как срез с отрицательным шагом влияет на порядок индекса.
"""
import warnings
import numpy as np
import pandas as pd

prices = pd.Series(np.arange(30) * 100_000 + 500_000)
print(prices.iloc[:7].tolist(), prices.iloc[-7:].tolist(), len(prices.iloc[10:20]), prices.iloc[::2].shape, prices.iloc[::-1].index[:3].tolist())
subset = prices.iloc[2:5]
subset.iloc[0] = 999                    # Copy-on-Write: исходный Series НЕ изменится
print("исходный не тронут:", prices.iloc[2], "| subset[0]:", subset.iloc[0])
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    prices.iloc[2:5][2] = 999           # цепочка: запись во временный объект
    print("chained ->", [type(x.message).__name__ for x in w], "| исходный:", prices.iloc[2], "(изменение НЕ применилось)")
s = pd.Series([1, 2, 3, 4], index=list("abcd"))
print("loc['a':'c']:", len(s.loc["a":"c"]), "| iloc[0:3]:", len(s.iloc[0:3]))
try:
    prices.iloc[::0]
except ValueError as e:
    print("шаг 0 ->", e)
print("отрицательный шаг разворачивает порядок индекса:", prices.iloc[::-1].index[:3].tolist())
# В Pandas 3.0 действует Copy-on-Write: любой результат индексирования ведёт себя как копия, поэтому цепочка
# x[...][...] = v пишет в временный объект и не меняет исходник (ChainedAssignmentError предупреждает об этом).
# .copy() всё ещё нужен, когда явно нужна независимая копия до изменения большого объекта в старых версиях/внешних вью.
# np.shares_memory(a, b) проверяет общую память. .loc включает конец (метки), .iloc - нет (позиции).
