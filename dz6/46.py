r"""
**Задача 46 (SQL ↔ Pandas).** Переведите на Pandas: `SELECT city, COUNT(*) AS cnt, AVG(amount) AS avg_amount FROM sales INNER JOIN customers ON ... WHERE status = 'completed' GROUP BY city HAVING COUNT(*) > 100 ORDER BY avg_amount DESC LIMIT 10`. Реализуйте через method chaining: `merge` → `query` → `groupby().agg()` → `reset_index()` → `query` → `sort_values` → `head(10)`. Реализуйте `UNION ALL` через `pd.concat`, `UNION` через `drop_duplicates()`. Реализуйте `LAG` через `shift`, `RANK` через `rank(method="min")`. Ожидаемый вывод: результат совпадает с SQL-запросом; `LAG` = `shift(1)`; `RANK` = `rank(method="min")`; `UNION ALL` = `concat(ignore_index=True)`. В комментариях объясните: чем `size()` отличается от `count()`; как `HAVING` через `query` после `groupby`; как перевести `ROW_NUMBER` (`groupby().cumcount() + 1`); почему `reset_index` нужен перед `query` по агрегату; как `LAG` с `groupby` работает (`groupby().shift(1)`); когда `as_index=False` заменяет `reset_index`.
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(46)
customers = pd.DataFrame({"customer_id": range(1, 501), "city": rng.choice(["Москва", "СПб", "Казань", "Сочи"], 500)})
sales = pd.DataFrame({"customer_id": rng.integers(1, 501, 3000), "amount": rng.normal(2e6, 5e5, 3000), "status": rng.choice(["completed", "cancelled"], 3000, p=[0.8, 0.2])})
res = (sales.merge(customers, on="customer_id", how="inner").query("status == 'completed'")
       .groupby("city").agg(cnt=("amount", "size"), avg_amount=("amount", "mean")).reset_index()
       .query("cnt > 100").sort_values("avg_amount", ascending=False).head(10))
print(res.round(0))
a = pd.DataFrame({"x": [1, 2, 2]}); b = pd.DataFrame({"x": [2, 3]})
print("UNION ALL:", pd.concat([a, b], ignore_index=True)["x"].tolist(), "| UNION:", pd.concat([a, b]).drop_duplicates()["x"].tolist())
s = pd.DataFrame({"g": ["a", "a", "b", "b"], "v": [3, 5, 4, 1]})
s["lag"] = s.groupby("g")["v"].shift(1); s["lag_def"] = s.groupby("g")["v"].shift(1, fill_value=0)
s["rank"] = s["v"].rank(method="min", ascending=False); s["row_number"] = s.groupby("g").cumcount() + 1
print(s)
# size() считает все строки группы (COUNT(*)), count() - только не-NaN значения столбца (COUNT(col)).
# HAVING - это фильтр ПОСЛЕ агрегации: сначала groupby.agg, потом .query("cnt > 100"). reset_index нужен, чтобы ключ группы
# стал столбцом (query по агрегату и последующий sort/merge работают со столбцами; а ключ в индексе недоступен по имени
# в части операций). ROW_NUMBER() OVER (PARTITION BY g) = groupby("g").cumcount() + 1. LAG(v, 1, 0) = shift(1, fill_value=0);
# LAG в SQL работает внутри партиции -> groupby(...).shift, а не просто shift (иначе значение «протечёт» между группами).
# UNION ALL = concat(ignore_index=True), UNION = concat + drop_duplicates; LIMIT 10 = head(10).
