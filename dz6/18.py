r"""
**Задача 18 (NaN: isna/dropna/fillna).** Создайте Series с пропусками (email клиентов автосалона). Проверьте `isna()`, `notna()`, `isna().sum()`. Примените `dropna(how="all")`, `dropna(thresh=2)`, `dropna(subset=["email"])`. Заполните через `fillna(0)`, `fillna(df.mean())`, `fillna(df.median())`, `fillna(df.mode().iloc[0])`. Для DataFrame примените `fillna({"A": 0, "B": df["B"].mean()})`. Проверьте, что `series == np.nan` всегда `False`. Ожидаемый вывод: `dropna(how="all")` удаляет только строки, где все значения `NaN`; `thresh=2` оставляет строки с ≥2 не-пропусками; `fillna(mode)` для строкового столбца возвращает моду (самое частое значение). В комментариях объясните: чем `thresh` отличается от `how` (`thresh` — минимальное число не-пропусков, `how` — "any"/"all"); почему `fillna(method=...)` удалён в Pandas 3.0 (используйте `ffill()`/`bfill()`); как `dropna(ignore_index=True)` сбрасывает индекс; почему сравнение с `np.nan` не работает (`NaN != NaN` по IEEE 754); в каких случаях `fillna(mode)` предпочтительнее `mean` (для категориальных/строковых данных, например, город); как `subset` ограничивает область проверки (только указанные столбцы).
"""
import numpy as np
import pandas as pd

email = pd.Series(["a@x.ru", None, "b@y.ru", None, "a@x.ru"])
print("isna:", email.isna().tolist(), "| sum:", email.isna().sum(), "| notna.sum:", email.notna().sum())
df = pd.DataFrame({"A": [1, None, None], "B": [2, 3, None], "C": [None, None, None]})
print("how='all':", df.dropna(how="all").shape, "| thresh=1:", df.dropna(thresh=1).shape, "| subset=['A']:", df.dropna(subset=["A"]).shape)
print("dropna(ignore_index=True) индекс:", df.dropna(how="all", ignore_index=True).index.tolist())
s = pd.Series([10.0, None, 30.0, 30.0])
print("fillna 0/mean/median/mode:", s.fillna(0).tolist(), s.fillna(s.mean()).tolist()[1], s.fillna(s.median()).tolist()[1], s.fillna(s.mode().iloc[0]).tolist()[1])
print("fillna(mode) для строк:", email.fillna(email.mode().iloc[0]).tolist())
print("fillna dict:", df.fillna({"A": 0, "B": df["B"].mean()}))
print("series == np.nan:", (s == np.nan).any(), "| isna:", s.isna().sum())
try:
    s.fillna(method="ffill")
except TypeError as e:
    print("fillna(method=) удалён ->", e)
print("ffill():", s.ffill().tolist())
# thresh - минимальное число НЕпропусков в строке, how - "any"/"all" (взаимоисключают друг друга). method= удалён в 3.0:
# используйте ffill()/bfill(). NaN != NaN по IEEE 754, поэтому ==np.nan всегда False - только isna().
# mode предпочтительнее mean для категориальных/строковых данных (город, бренд). subset ограничивает проверку
# указанными столбцами. ignore_index=True сбрасывает индекс после удаления.
