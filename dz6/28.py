r"""
**Задача 28 (cut/qcut/crosstab/pivot_table, продвинутый).** Создайте DataFrame `customers` с `age`, `city`, `gender`, `purchase_amount`. Примените `cut` и `qcut` к `age`. Создайте `crosstab(index="city", columns="age_group", margins=True, normalize="index")` и `crosstab(..., values="purchase_amount", aggfunc="sum")`. Создайте `pivot_table(values="purchase_amount", index="city", columns="gender", aggfunc=["sum", "mean"], margins=True, fill_value=0)`. Примените `cut` с `right=False`. Ожидаемый вывод: `aggfunc=["sum", "mean"]` создаёт MultiIndex по столбцам; `right=False` сдвигает границы; `fill_value=0` заменяет `NaN`. В комментариях объясните: как `cut` с `right=False` меняет границы (интервалы `[a, b)` вместо `(a, b]`); когда `margins` полезен (итоговые строки/столбцы); как `aggfunc` списком влияет на структуру (MultiIndex в столбцах); чем `crosstab` с `values` отличается от `pivot_table` (`crosstab` — частотная таблица, но с `values`/`aggfunc` становится агрегацией); как `normalize="columns"` меняет интерпретацию (доли по столбцам); что произойдёт при `qcut` с `q=4` на малых данных (может упасть из-за дубликатов или недостатка значений).
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(28)
n = 300
c = pd.DataFrame({"age": rng.integers(18, 81, n), "city": rng.choice(["Москва", "СПб", "Казань"], n), "gender": rng.choice(["М", "Ж"], n), "purchase_amount": rng.normal(2e6, 5e5, n)})
c["age_group"] = pd.cut(c["age"], [0, 25, 35, 45, 55, 100], labels=["<25", "25-35", "35-45", "45-55", ">55"])
print(pd.crosstab(c["city"], c["age_group"], margins=True, normalize="index").round(2))
print(pd.crosstab(c["city"], c["gender"], values=c["purchase_amount"], aggfunc="sum").round(0))
print(pd.crosstab(c["city"], c["gender"], normalize="columns").round(2))
pt = c.pivot_table(values="purchase_amount", index="city", columns="gender", aggfunc=["sum", "mean"], margins=True, fill_value=0)
print(pt.round(0)); print("уровни столбцов:", pt.columns.nlevels)
print("right=False:", pd.cut(pd.Series([25, 26]), [0, 25, 100], right=False).tolist(), "| right=True:", pd.cut(pd.Series([25, 26]), [0, 25, 100]).tolist())
try:
    print(pd.qcut(pd.Series([1, 2]), q=4).tolist())
except ValueError as e:
    print("qcut на малых данных ->", e)
# right=False: интервалы [a, b), по умолчанию (a, b]. margins=True добавляет итоговые строку/столбец All.
# aggfunc=список создаёт MultiIndex в столбцах (верхний уровень - функция). crosstab - частотная таблица по умолчанию (подсчёт),
# но с values+aggfunc работает как агрегация (почти то же, что pivot_table). normalize="columns" - доли по столбцам.
# qcut на малой/однообразной выборке падает: границы квантилей совпадают -> duplicates="drop" или меньше q.
