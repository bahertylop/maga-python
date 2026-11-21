r"""
**Задача 51 (pd.col() в цепочках).** Создайте DataFrame. Постройте цепочку `df.assign(ratio=pd.col("sold") / pd.col("stock")).loc[pd.col("ratio") > 0.5].assign(double_sold=pd.col("sold") * 2).sort_values("ratio")`. Сравните с вариантом через `lambda`. Проверьте, что `pd.col()` работает в `.loc` и `.assign()`. Примените `.pipe(print)` внутри цепочки. Ожидаемый вывод: оба варианта дают идентичный результат; `pd.col()` работает в `.loc` и `.assign()`; `.pipe(print)` выводит промежуточный DataFrame. В комментариях объясните: почему `pd.col()` пока «начальная поддержка» (новый API, не все методы поддерживают); в каких случаях `lambda` всё ещё нужен (сложные выражения, вызовы внешних функций); как `pd.col()` читается в длинных цепочках (без `lambda x: x[...]`); что произойдёт при `pd.col()` со списком столбцов (не поддерживается); как `.pipe` помогает отлаживать (вставка `print`/`head` в цепочку); когда цепочка становится нечитаемой (более 5–7 шагов).
"""
import pandas as pd

df = pd.DataFrame({"model": ["A", "B", "C", "D"], "sold": [30, 80, 45, 90], "stock": [100, 100, 60, 100]})
if not hasattr(pd, "col"):
    print("pd.col() есть только в pandas >= 3.0 (у вас", pd.__version__ + "); показан вариант с lambda")
r2 = (df.assign(ratio=lambda x: x["sold"] / x["stock"]).loc[lambda x: x["ratio"] > 0.5].assign(double_sold=lambda x: x["sold"] * 2).sort_values("ratio"))
print(r2)
if hasattr(pd, "col"):
    r1 = (df.assign(ratio=pd.col("sold") / pd.col("stock")).loc[pd.col("ratio") > 0.5]
          .assign(double_sold=pd.col("sold") * 2).sort_values("ratio"))
    print("идентичны lambda-варианту:", r1.equals(r2))
    print(".pipe(print) печатает DataFrame, но возвращает None - продолжить цепочку после него нельзя:")
    try:
        df.assign(ratio=pd.col("sold") / pd.col("stock")).pipe(print).loc[pd.col("ratio") > 0.5]
    except Exception as e:
        print("   ->", type(e).__name__, "-", e)
    dbg = df.assign(ratio=pd.col("sold") / pd.col("stock")).pipe(lambda d: (print(d.head(2)), d)[1]).loc[pd.col("ratio") > 0.5]
    print("отладочный pipe, возвращающий df, работает:", len(dbg), "строки")
    try:
        df.assign(s=pd.col(["sold", "stock"]).sum())
    except Exception as e:
        print("pd.col(список) ->", type(e).__name__, "-", str(e)[:60])
# pd.col("x") - ленивое выражение: вместо lambda x: x["x"] читается в цепочке «как формула». Это начальная поддержка (3.0):
# работает в assign и loc/[]; не все методы и выражения поддерживаются, поэтому сложное (вызов внешних функций, np.where на
# нескольких столбцах, условная логика) по-прежнему пишут через lambda. pd.col принимает ОДНО имя столбца, список не поддерживается.
# .pipe(func) вставляет в цепочку отладочный вывод; но print возвращает None, поэтому для отладки нужна функция,
# которая печатает и возвращает df (lambda d: (print(d), d)[1]). Цепочка длиннее 5-7 шагов становится нечитаемой - разбивайте на этапы.
