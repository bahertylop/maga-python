r"""
**Задача 37 (categorical: создание, коды, ordered).** Создайте `pd.Series(["a", "b", "c", "a"], dtype="category")`. Примените `astype("category")` к строковому столбцу. Создайте `pd.Categorical(["средний", "низкий", "высокий"], categories=["низкий", "средний", "высокий"], ordered=True)`. Проверьте `.cat.categories`, `.cat.codes`, `.cat.ordered`. Создайте `CategoricalDtype` с `ordered=True`. Отсортируйте Series. Примените `groupby("category", observed=False/True)`. Ожидаемый вывод: `codes` для `["a", "b", "c", "a"]` — `[0, 1, 2, 0]`; `ordered=True` даёт сортировку по порядку категорий; `observed=False` включает ненаблюдаемые категории. В комментариях объясните: почему `-1` — код пропуска; как `ordered=True` влияет на сортировку (порядок задаётся `categories`); чем `observed=False` отличается (включает все категории в `groupby`); что произойдёт при присвоении значения вне категорий (`ValueError`); как `category` влияет на память (хранит коды + словарь); почему `category` не подходит для высококардинальных данных (словарь занимает много памяти).
"""
import numpy as np
import pandas as pd

s = pd.Series(["a", "b", "c", "a"], dtype="category")
print("categories:", list(s.cat.categories), "| codes:", s.cat.codes.tolist(), "| ordered:", s.cat.ordered)
df = pd.DataFrame({"category": ["low", "high", "mid", "low"], "x": [1, 2, 3, 4]})
df["category"] = df["category"].astype("category"); print("astype:", df["category"].dtype)
cat = pd.Categorical(["средний", "низкий", "высокий"], categories=["низкий", "средний", "высокий"], ordered=True)
print("сортировка:", sorted(cat), "| codes:", list(cat.codes), "| min/max:", cat.min(), cat.max())
dt = pd.CategoricalDtype(["низкий", "средний", "высокий"], ordered=True)
srs = pd.Series(["средний", "низкий", "высокий", "низкий"], dtype=dt)
print(srs.sort_values().tolist())
print("пропуск -> код:", pd.Series(["a", None], dtype="category").cat.codes.tolist())
g = pd.DataFrame({"c": pd.Categorical(["a", "a", "b"], categories=["a", "b", "z"]), "v": [1, 2, 3]})
print("observed=False:", g.groupby("c", observed=False)["v"].sum().to_dict(), "| observed=True:", g.groupby("c", observed=True)["v"].sum().to_dict())
try:
    s.iloc[0] = "не из категорий"
except (TypeError, ValueError) as e:
    print("значение вне категорий ->", type(e).__name__, "-", str(e)[:60])
# -1 в codes - код пропуска (NaN): категории нумеруются с 0, поэтому -1 не может быть реальной категорией.
# ordered=True: порядок задаётся списком categories (а не алфавитом) - по нему работают sort, min/max и сравнения (<, >).
# observed=False включает в groupby и НЕнаблюдаемые категории (результат 0/NaN), observed=True - только встретившиеся.
# Присвоение значения вне categories -> TypeError/ValueError (в Pandas 3 - TypeError): сначала add_categories.
