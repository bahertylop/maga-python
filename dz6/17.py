r"""
**Задача 17 (cut/qcut/crosstab/pivot_table).** Создайте DataFrame `customers` с `age` (18–80), `city`, `gender`, `purchase_amount`. Примените `pd.cut(age, bins=[0, 25, 35, 45, 55, 100], labels=["<25", "25-35", "35-45", "45-55", ">55"])` и `pd.qcut(age, q=4, labels=["Q1", "Q2", "Q3", "Q4"])`. Сравните размеры групп через `value_counts()`. Создайте `crosstab(index="city", columns="age_group", margins=True, normalize="index")` и `pivot_table(values="purchase_amount", index="city", columns="gender", aggfunc="mean", margins=True, fill_value=0)`. Ожидаемый вывод: `cut` даёт группы разной ширины (разного размера), `qcut` — примерно равного; `margins=True` добавляет строку `All`; `normalize="index"` показывает доли по строкам. В комментариях объясните: в каких случаях `qcut` падает (дубликаты в данных) и как решается через `duplicates="drop"`; как `normalize` меняет интерпретацию (`"index"` — доли по строкам, `"columns"` — по столбцам, `True` — по всей таблице); как `margins` добавляет итоги; чем `pivot_table` безопаснее `pivot` (умеет агрегировать дубликаты через `aggfunc`); как `fill_value` влияет на результат (заменяет `NaN` после агрегации); что произойдёт при `cut` с `right=False` (границы не включаются справа).
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(17)
n = 300
c = pd.DataFrame({"age": rng.integers(18, 81, n), "city": rng.choice(["Москва", "СПб", "Казань"], n),
                  "gender": rng.choice(["М", "Ж"], n), "purchase_amount": rng.normal(2e6, 5e5, n).round(0)})
c["age_group"] = pd.cut(c["age"], bins=[0, 25, 35, 45, 55, 100], labels=["<25", "25-35", "35-45", "45-55", ">55"])
c["age_q"] = pd.qcut(c["age"], q=4, labels=["Q1", "Q2", "Q3", "Q4"])
print("cut  :", c["age_group"].value_counts().sort_index().tolist(), "(разные размеры)")
print("qcut :", c["age_q"].value_counts().sort_index().tolist(), "(примерно равные)")
ct = pd.crosstab(c["city"], c["age_group"], margins=True, normalize="index")
print(ct.round(2))
pt = pd.pivot_table(c, values="purchase_amount", index="city", columns="gender", aggfunc="mean", margins=True, fill_value=0)
print(pt.round(0))
try:
    pd.qcut(pd.Series([1, 1, 1, 1, 2]), 4)
except ValueError as e:
    print("qcut с дублями ->", str(e)[:60], "...")
print("duplicates='drop':", pd.qcut(pd.Series([1, 1, 1, 1, 2]), 4, duplicates="drop").nunique(), "интервала")
print("right=False:", pd.cut(pd.Series([25]), [0, 25, 100], right=False).iloc[0], "(25 попадает в [25, 100))")
# normalize: "index" - доли по строкам, "columns" - по столбцам, True/"all" - по всей таблице. margins=True добавляет итог
# (строку/столбец All). pivot_table агрегирует дубликаты через aggfunc (pivot на них падает). fill_value заменяет NaN
# ПОСЛЕ агрегации. qcut падает на дублях границ квантилей -> duplicates="drop". right=False: интервалы [a, b).
