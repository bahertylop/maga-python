r"""
**Задача 38 (categorical: .cat.* API, память).** Примените `.cat.add_categories(["d", "e"])`, `.cat.remove_categories(["a"])`, `.cat.remove_unused_categories()`, `.cat.rename_categories({"a": "x"})`, `.cat.reorder_categories(["c", "b", "a"], ordered=True)`. Создайте 1 000 000 строк с 4 брендами — сравните `memory_usage(deep=True)` для `str` и `category`. Создайте 10 000 строк с 10 000 уникальных значений — сравните `str` vs `category`. Ожидаемый вывод: `category` для 4 значений экономит ≈96% памяти; для 10 000 значений `category` использует **больше** памяти, чем `str`. В комментариях объясните: когда `category` хуже `str` (высокая кардинальность — например, уникальные VIN); как `rename_categories` со списком работает (позиционное соответствие); зачем `remove_unused_categories` (убирает категории, которых нет в данных); что произойдёт при `remove_categories` с используемым значением (`ValueError`); как `reorder_categories` влияет на `sort_values`; как `category` взаимодействует с `groupby` (эффективнее, чем `str`).
"""
import numpy as np
import pandas as pd

c = pd.Series(["a", "b", "a", "c", "b"], dtype="category")
c2 = c.cat.add_categories(["d", "e"]); print("add:", list(c2.cat.categories))
c3 = c.cat.remove_categories(["c"]); print("remove(c):", list(c3.cat.categories), "| значение 'c' ->", c3.iloc[3])
print("remove_unused:", list(c2.cat.remove_unused_categories().cat.categories))
print("rename dict:", list(c.cat.rename_categories({"a": "x"}).cat.categories), "| список:", list(c.cat.rename_categories(["x", "y", "z"]).cat.categories))
print("reorder:", list(c.cat.reorder_categories(["c", "b", "a"], ordered=True).cat.categories))
try:
    c.cat.remove_categories(["a"]).isna().sum()
    print("remove_categories используемой категории -> значения становятся NaN:", c.cat.remove_categories(["a"]).isna().sum(), "шт.")
except ValueError as e:
    print(e)
try:
    c.cat.reorder_categories(["c", "b"])
except ValueError as e:
    print("reorder с неполным набором ->", type(e).__name__)
n = 1_000_000
rng = np.random.default_rng(38)
brands = pd.Series(rng.choice(["Toyota", "BMW", "Kia", "Audi"], n))
m_str, m_cat = brands.memory_usage(deep=True), brands.astype("category").memory_usage(deep=True)
print(f"4 бренда: str={m_str/1e6:.1f} МБ, category={m_cat/1e6:.2f} МБ, экономия {(1-m_cat/m_str)*100:.0f}%")
vin = pd.Series([f"VIN{i:014d}" for i in range(10_000)])
v_str, v_cat = vin.memory_usage(deep=True), vin.astype("category").memory_usage(deep=True)
print(f"10000 VIN: str={v_str/1e3:.0f} КБ, category={v_cat/1e3:.0f} КБ -> category {'ХУЖЕ' if v_cat > v_str else 'лучше'}")
# category хранит словарь уникальных значений + целочисленные коды: при высокой кардинальности словарь = почти все данные,
# да ещё и коды сверху (VIN уникальны -> проигрыш). rename_categories со СПИСКОМ - позиционное переименование (по порядку
# категорий), со словарём - по имени. remove_unused_categories убирает категории, которых нет в данных (после фильтрации).
# remove_categories для используемого значения не падает: значения превращаются в NaN (потеря данных!).
