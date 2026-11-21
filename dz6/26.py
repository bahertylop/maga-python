r"""
**Задача 26 (groupby: transform/filter/apply).** Используйте DataFrame из задачи 25. Примените `.agg({"amount": ["sum", "mean"], "count": ["count", "max"]})`. Примените `transform("mean")` и `transform(lambda x: x.fillna(x.mean()))`. Примените `filter(lambda g: len(g) > 50)`. Примените `apply(weighted_avg)` с `np.average(amount, weights=count)`. Примените `apply(..., include_groups=False)`. Ожидаемый вывод: `transform("mean")` возвращает Series той же длины; `filter` оставляет только группы с >50 строками; `apply` с `include_groups=False` не передаёт группировочные столбцы в функцию. В комментариях объясните: в каких случаях `transform` незаменим (когда нужен результат той же длины, например, заполнение пропусков групповым средним); почему `apply` медленнее встроенных методов; что делает `include_groups=False` (убирает группировочные столбцы из DataFrame внутри функции); как `filter` отличается от булевой маски (фильтрует целые группы, а не строки); когда `agg` со словарём предпочтительнее списка (разные функции для разных столбцов); почему `transform` возвращает Series той же длины, а `agg` — свёрнутый результат.
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(26)
n = 300
d = pd.DataFrame({"brand": rng.choice(["Toyota", "BMW", "Kia"], n, p=[0.5, 0.3, 0.2]), "amount": rng.normal(2e6, 5e5, n), "count": rng.integers(1, 6, n)})
d.loc[rng.choice(n, 25, replace=False), "amount"] = np.nan
g = d.groupby("brand")
print(g.agg({"amount": ["sum", "mean"], "count": ["count", "max"]}).round(0))
print("transform('mean') длина:", len(g["amount"].transform("mean")), "== len(df):", len(d))
filled = g["amount"].transform(lambda x: x.fillna(x.mean()))
print("NaN до/после заполнения групповым средним:", d["amount"].isna().sum(), "->", filled.isna().sum())
big = g.filter(lambda x: len(x) > 50)
print("filter(len>50) бренды:", sorted(big["brand"].unique()))
def weighted_avg(x):
    ok = x["amount"].notna()
    return np.average(x.loc[ok, "amount"], weights=x.loc[ok, "count"])
print("apply с весами:", g.apply(weighted_avg, include_groups=False).round(0).to_dict())
# transform незаменим, когда нужен результат ТОЙ ЖЕ длины (заполнить пропуски средним по группе, нормировать внутри группы);
# agg сворачивает группу в одно значение. apply медленнее встроенных методов: Python-функция вызывается на каждой группе.
# include_groups=False не передаёт группировочные столбцы внутрь функции (в 3.0 это поведение по умолчанию).
# filter отбирает ЦЕЛЫЕ группы по условию, булева маска - отдельные строки. agg со словарём - разные функции для разных столбцов.
