r"""
**Задача 31 (concat/stack/unstack/melt).** Создайте два DataFrame продаж за разные периоды с одинаковыми столбцами. Примените `pd.concat([df1, df2])`, `pd.concat(..., ignore_index=True)`, `pd.concat(..., axis=1)`, `pd.concat(..., keys=["a", "b"])`. Попробуйте `pd.concat(..., ignore_index=True, keys=["a", "b"])`. Примените `df.stack()`, `df.unstack()`, `pd.melt(df, id_vars=["city"], value_vars=["Q1", "Q2"], var_name="quarter", value_name="revenue")`. Ожидаемый вывод: `concat` без `ignore_index` дублирует индексы; с `ignore_index` — пересоздаёт; `keys` создаёт MultiIndex; `ignore_index + keys` даёт `ValueError` в Pandas 3.0. В комментариях объясните: почему `concat(ignore_index=True, keys=...)` даёт ошибку в 3.0 (конфликт семантики); чем `melt` отличается от `stack` (`melt` — wide-to-long по столбцам, `stack` — по индексу); как `stack(dropna=False)` сохраняет пропуски; что произойдёт при `unstack` с несуществующим уровнем (`KeyError`); как `keys` создаёт MultiIndex; в каких случаях `melt` предпочтительнее `stack` (когда нужно переплавить широкую таблицу с несколькими value_vars).
"""
import pandas as pd

df1 = pd.DataFrame({"city": ["Москва", "СПб"], "Q1": [10, 20], "Q2": [11, 21]})
df2 = pd.DataFrame({"city": ["Казань", "Сочи"], "Q1": [5, 6], "Q2": [7, 8]})
print(pd.concat([df1, df2]).index.tolist(), "| ignore_index:", pd.concat([df1, df2], ignore_index=True).index.tolist())
print("axis=1:\n", pd.concat([df1, df2], axis=1))
print("keys:\n", pd.concat([df1, df2], keys=["a", "b"]))
try:
    pd.concat([df1, df2], ignore_index=True, keys=["a", "b"])
except ValueError as e:
    print("ignore_index+keys ->", e)
p = df1.set_index("city")
st = p.stack()
print("stack:\n", st, "\nunstack:\n", st.unstack())
try:
    p.stack(dropna=False)
except ValueError as e:
    print("stack(dropna=False) в 3.0 ->", e)
try:
    st.unstack(level="нет")
except (KeyError, IndexError) as e:
    print("unstack несуществующий уровень ->", type(e).__name__)
print(pd.melt(df1, id_vars=["city"], value_vars=["Q1", "Q2"], var_name="quarter", value_name="revenue"))
# В Pandas 3 ignore_index=True вместе с keys несовместимы: keys создают MultiIndex, а ignore_index его выбрасывает - противоречие.
# melt - «wide -> long» по СТОЛБЦАМ (id_vars остаются, остальные плавятся), stack - переносит уровень столбцов в индекс.
# Новый stack (3.0) не удаляет NaN и не принимает dropna (поведение изменилось). melt удобнее, когда плавим несколько value_vars
# в «длинную» таблицу и хотим задать имена var_name/value_name.
