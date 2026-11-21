r"""
**Задача 25 (groupby: size/count/agg).** Создайте DataFrame `sales` с `brand`, `amount` (с пропусками), `count`. Примените `groupby("brand").size()` и `.count()` — сравните. Примените `sum()`, `mean()`, `first()`, `last()`, `nunique()`. Проверьте `skipna=False`. Примените `.agg(["sum", "mean"])` и `.agg(total=("amount", "sum"), avg=("amount", "mean"))`. Ожидаемый вывод: `size()` считает все строки, `count()` — только не-пропуски по каждому столбцу; `skipna=False` даёт `NaN` для групп с пропусками; `NamedAgg` возвращает именованные столбцы. В комментариях объясните: чем `size()` отличается от `count()` (включает `NaN`); как `skipna=False` влияет; почему `NamedAgg` читаемее списка; как `first`/`last` обрабатывают пропуски (по умолчанию пропускают, `skipna=False` — нет); что произойдёт при `agg` с несуществующей функцией (`AttributeError`); как `nunique` считает уникальные с `NaN` (по умолчанию исключает, `dropna=False` — включает).
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(25)
n = 200
sales = pd.DataFrame({"brand": rng.choice(["Toyota", "BMW", "Kia", "Hyundai"], n), "amount": rng.normal(2e6, 5e5, n), "count": rng.integers(1, 6, n)})
sales.loc[rng.choice(n, 20, replace=False), "amount"] = np.nan
g = sales.groupby("brand")
print("size :", g.size().to_dict(), "\ncount:", g["amount"].count().to_dict(), "(без NaN)")
print(g["amount"].agg(["sum", "mean", "first", "last", "nunique"]).round(0))
try:
    print("sum(skipna=False):", g["amount"].sum(skipna=False).round(0).to_dict())
except TypeError as e:
    print("skipna в groupby недоступен в этой версии:", e)
print(g["amount"].agg(["sum", "mean"]).round(0))
print(g.agg(total=("amount", "sum"), avg=("amount", "mean"), n=("count", "size")).round(0))
print("nunique dropna=False:", g["amount"].nunique(dropna=False).to_dict())
try:
    g["amount"].agg("не_функция")
except (AttributeError, TypeError, ValueError) as e:
    print("несуществующая функция ->", type(e).__name__)
# size() считает ВСЕ строки группы (включая NaN), count() - только не-пропуски. skipna=False: группа с пропуском даёт NaN.
# Named aggregation (NamedAgg) читаемее списка: сразу задаёт имя итогового столбца. first/last по умолчанию пропускают NaN
# (берут первое/последнее не-NaN). nunique по умолчанию исключает NaN, dropna=False считает его отдельным значением.
