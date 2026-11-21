r"""
**Задача 56 (антипаттерны).** Создайте DataFrame. Примените `df.drop("col", axis=1, inplace=True)` — зафиксируйте `None`. Воссоздайте и примените `df = df.drop("col", axis=1)`. Попробуйте `.append(new_row)` — зафиксируйте `AttributeError`. Замените на сбор в список + `pd.concat(rows, ignore_index=True)`. Создайте `subset = df[df["price"] > 0]`, измените `subset.loc[subset.index[0], "status"] = "sold"`. Выполните `df["A"][df["B"] > 0] = 1` — зафиксируйте `ChainedAssignmentError`. Ожидаемый вывод: `inplace=True` возвращает `None`; `.append` даёт `AttributeError`; `ChainedAssignmentError` возникает при chained assignment; `subset` не изменяет `df` (CoW). В комментариях объясните: почему `inplace` ломает цепочки (возвращает `None`); как CoW делает `.copy()` ненужным (по умолчанию копирование при записи); почему `.append()` удалён (медленный, каждый раз копирует); в каких случаях `.copy()` всё ещё нужен (принудительное копирование перед изменением); как переписать цикл с `.append` на `pd.concat`; почему `inplace=True` не экономит память для методов, меняющих форму.
"""
import warnings
import pandas as pd

df = pd.DataFrame({"col": [1, 2], "price": [100, -5], "A": [0, 0], "B": [1, 0], "status": ["new", "new"]})
r = df.drop("col", axis=1, inplace=True); print("inplace=True вернул:", r, "| столбцов:", df.shape[1])
df = pd.DataFrame({"col": [1, 2], "price": [100, -5], "A": [0, 0], "B": [1, 0], "status": ["new", "new"]})
df = df.drop("col", axis=1); print("df = df.drop(...):", list(df.columns))
try:
    df.append({"price": 1})
except AttributeError as e:
    print("append ->", type(e).__name__, "-", e)
rows = [{"price": p} for p in (1, 2, 3)]
print("concat:", pd.concat([pd.DataFrame([r]) for r in rows], ignore_index=True)["price"].tolist(), "| проще: pd.DataFrame(rows)")
subset = df[df["price"] > 0]
subset.loc[subset.index[0], "status"] = "sold"
print("subset изменён:", subset["status"].tolist(), "| df не затронут (CoW):", df["status"].tolist())
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    try:
        df["A"][df["B"] > 0] = 1
        print("chained assignment: исключения нет, но df['A'] =", df["A"].tolist(), "(НЕ изменился)")
    except Exception as e:
        print("chained assignment ->", type(e).__name__)
print("предупреждения:", [type(x.message).__name__ for x in w])
df.loc[df["B"] > 0, "A"] = 1; print("правильно через .loc:", df["A"].tolist())
# inplace=True возвращает None -> ломает цепочки (df.drop(..., inplace=True).rename(...) -> AttributeError); при этом часто всё
# равно создаётся копия данных, поэтому память не экономится (для методов, меняющих форму - drop, dropna, reset_index).
# .append удалён в 2.0: каждый вызов копировал ВЕСЬ DataFrame (O(n^2) в цикле); собирайте строки в список и один раз делайте
# pd.concat/pd.DataFrame(rows). В Pandas 3 включён Copy-on-Write: любое «производное» (subset, срез) ведёт себя как копия,
# поэтому защитные .copy() обычно не нужны; .copy() нужен, если вы хотите независимый объект СРАЗУ (до записи) или передаёте
# данные в код, который меняет буфер напрямую (NumPy). Chained assignment (df["A"][mask] = 1) пишет в промежуточный объект и
# при CoW не меняет df: в 3.0 это ChainedAssignmentError-предупреждение (в строгом режиме - исключение); пишите df.loc[mask, "A"] = 1.
