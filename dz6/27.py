r"""
**Задача 27 (groupby: multi-column/as_index/observed).** Создайте DataFrame с `city`, `gender`, `amount`. Примените `groupby(["city", "gender"]).size()`. Примените `groupby("city", as_index=False).agg(...)`. Проверьте `observed=True/False` для `category`-столбца. Проверьте `dropna=False` и `sort=False`. Итерируйте через `for name, group in df.groupby("city"): ...`. Используйте `df.groupby("city").get_group("Москва")`. Ожидаемый вывод: `as_index=False` возвращает `city` как столбец; `observed=False` включает ненаблюдаемые категории; `get_group("Москва")` возвращает подмножество. В комментариях объясните: когда `as_index=False` удобнее (для дальнейшего `merge`/`query` без `reset_index`); как `observed` влияет на результат (с `False` — все категории, с `True` — только встречающиеся); почему `get_group` быстрее `filter` (прямой доступ к группе, без обхода всех); как `dropna=False` включает `NaN`-группы; что произойдёт при `get_group` с несуществующей группой (`KeyError`); как `sort=False` ускоряет группировку (не сортирует ключи).
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(27)
n = 120
df = pd.DataFrame({"city": rng.choice(["Москва", "СПб", None], n, p=[0.5, 0.4, 0.1]), "gender": rng.choice(["М", "Ж"], n), "amount": rng.normal(2e6, 5e5, n)})
print(df.groupby(["city", "gender"]).size())
print(df.groupby("city", as_index=False).agg(total=("amount", "sum")).round(0))
cat = df.assign(city=pd.Categorical(df["city"], categories=["Москва", "СПб", "Казань"]))
print("observed=True :", cat.groupby("city", observed=True).size().to_dict())
print("observed=False:", cat.groupby("city", observed=False).size().to_dict(), "(Казань = 0)")
print("dropna=False:", df.groupby("city", dropna=False).size().to_dict(), "| sort=False порядок:", list(df.groupby("city", sort=False).groups))
for name, group in df.groupby("city"):
    print("группа", name, len(group))
print("get_group:", len(df.groupby("city").get_group("Москва")))
try:
    df.groupby("city").get_group("Нью-Йорк")
except KeyError as e:
    print("несуществующая группа -> KeyError", e)
# as_index=False возвращает ключ как обычный столбец - удобно для дальнейшего merge/query без reset_index.
# observed влияет только на category-ключи: False - все категории (включая пустые), True - только встретившиеся.
# get_group обращается к уже построенному индексу группы напрямую, а filter обходит все группы.
# dropna=False сохраняет NaN-группу. sort=False не сортирует ключи (быстрее, порядок - по первому появлению).
