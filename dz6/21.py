r"""
**Задача 21 (astype/to_numeric/to_datetime).** Создайте Series `["1", "2", "abc", "4", "5"]` (количество автомобилей в наличии). Примените `astype(int)` — зафиксируйте `ValueError`. Примените `pd.to_numeric(s, errors="coerce")`. Создайте Series `["2025-01-01", "invalid", "2025-02-01"]`, примените `pd.to_datetime(errors="coerce")`. Примените `pd.to_numeric(col, downcast="integer")`. Примените `df.convert_dtypes()`. Ожидаемый вывод: `astype(int)` на `"abc"` даёт `ValueError`; `to_numeric(errors="coerce")` даёт `NaN` на `"abc"`; `to_datetime(errors="coerce")` даёт `NaT` на `"invalid"`; `downcast` уменьшает тип. В комментариях объясните: почему `errors="ignore"` удалён в Pandas 3.0 (непредсказуемое поведение); чем `Int64` лучше `int64` при наличии `NaN` (поддерживает `pd.NA`); как `downcast` выбирает тип (минимальный, вмещающий все значения); в каких случаях `convert_dtypes` даёт неожиданный результат (может превратить строки в `string` dtype); что произойдёт при `to_datetime` с неверным форматом без `errors` (`ValueError`); как `to_numeric` обрабатывает строки с пробелами (обычно обрезает, но лучше `str.strip()`).
"""
import pandas as pd

s = pd.Series(["1", "2", "abc", "4", "5"])
try:
    s.astype(int)
except ValueError as e:
    print("astype(int) ->", type(e).__name__, e)
print("to_numeric coerce:", pd.to_numeric(s, errors="coerce").tolist())
d = pd.Series(["2025-01-01", "invalid", "2025-02-01"])
print("to_datetime coerce:", pd.to_datetime(d, errors="coerce").tolist())
try:
    pd.to_datetime(d)
except ValueError as e:
    print("без errors ->", type(e).__name__)
try:
    pd.to_numeric(s, errors="ignore")
except ValueError as e:
    print("errors='ignore' удалён в 3.0 ->", e)
print("downcast:", pd.to_numeric(pd.Series(["1", "2", "100"]), downcast="integer").dtype)
df = pd.DataFrame({"a": [1, 2, None], "b": ["x", "y", None], "c": [1.5, 2.5, 3.5]})
print("convert_dtypes:", df.convert_dtypes().dtypes.astype(str).tolist())
print("пробелы:", pd.to_numeric(pd.Series([" 5 "]), errors="coerce").tolist(), "(лучше сначала .str.strip())")
# errors="ignore" удалён: он молча возвращал ИСХОДНЫЕ данные при ошибке - результат непредсказуем по типу. coerce превращает
# нечисловое в NaN/NaT (число некорректных = isna().sum()). Int64 (nullable) хранит пропуски без превращения в float.
# downcast выбирает минимальный тип, вмещающий все значения. convert_dtypes переводит в nullable-типы (Int64, string, boolean) и
# иногда меняет то, что вы не ожидали (float с целыми значениями -> Int64).
