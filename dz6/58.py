r"""
**Задача 58 (Pandas 3.0).** Создайте `pd.Series(["a", "b", "c"])` — зафиксируйте `dtype="str"`. Примените `is_string_dtype(series)` — `True`; сравните с `series.dtype == object` — `False`. Выполните `df["A"][df["B"] > 0] = 1` — `ChainedAssignmentError`. Создайте `subset = df[df["sales"] > 0]`, измените `subset` — `df` не изменился. Примените `df.assign(weighted=pd.col("price") * pd.col("discount"))` и `df.loc[pd.col("price") > 1000000]`. Ожидаемый вывод: `dtype` строки — `str`; `is_string_dtype` — `True`; `ChainedAssignmentError` при chained; `pd.col()` работает в `.assign()` и `.loc`. В комментариях объясните: почему `.append()` удалён в 2.0; как мигрировать через 2.3 (включить `pd.options.future.infer_string`); зачем `pd.options.future.infer_string` только в 2.3 (обратная совместимость); что произойдёт при `dtype == object` (не сравнится со `str`); как CoW влияет на производительность (меньше копирований); какие ещё breaking changes есть в 3.0 (`inplace` депрекация, `errors="ignore"` удалён).
"""
import warnings
import pandas as pd
from pandas.api.types import is_string_dtype

s = pd.Series(["a", "b", "c"])
print("dtype:", s.dtype, "| is_string_dtype:", is_string_dtype(s), "| dtype == object:", s.dtype == object, "| версия pandas:", pd.__version__)
df = pd.DataFrame({"A": [0, 0, 0], "B": [1, 0, 1], "sales": [10, 0, 30], "price": [500_000, 2_000_000, 3_000_000], "discount": [0.1, 0.2, 0.0]})
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    df["A"][df["B"] > 0] = 1
print("chained assignment: A =", df["A"].tolist(), "| предупреждения:", sorted({type(x.message).__name__ for x in w}))
subset = df[df["sales"] > 0]; subset.loc[subset.index[0], "sales"] = -1
print("subset изменён:", subset["sales"].tolist(), "| df.sales:", df["sales"].tolist())
if hasattr(pd, "col"):
    print(df.assign(weighted=pd.col("price") * pd.col("discount")))
    print(df.loc[pd.col("price") > 1_000_000])
else:
    print("pd.col() нет в pandas", pd.__version__, "- эквивалент через lambda:")
    print(df.assign(weighted=lambda d: d["price"] * d["discount"])); print(df.loc[lambda d: d["price"] > 1_000_000])
try:
    with pd.option_context("future.infer_string", False):
        print("future.infer_string=False -> dtype:", pd.Series(["a"]).dtype)
except Exception as e:
    print("future.infer_string:", type(e).__name__, e)
# .append удалён в 2.0 (медленный: каждый раз копирует весь DataFrame) - используйте pd.concat.
# Миграция: в 2.3 включают pd.options.future.infer_string = True (и CoW: pd.options.mode.copy_on_write = True), чтобы проверить код
# заранее; опция «future», потому что по умолчанию менять dtype в минорной версии нельзя (обратная совместимость), а в 3.0 это
# поведение по умолчанию. dtype == object для строк в 3.0 -> False (dtype теперь "str"): проверяйте is_string_dtype(s) или s.dtype == "str".
# CoW экономит копирования: срезы/производные - ленивые копии (копирование только при записи), поэтому защитные .copy() не нужны.
# Другие breaking changes 3.0: удалены deprecated-вещи 2.x (inplace-цепочки/chained assignment больше не меняют df,
# errors="ignore" в to_datetime/to_numeric удалён, fillna(method=...), alias "M"/"Y"/"H" заменены на "ME"/"YE"/"h", datetime64[us] по умолчанию и др.).
