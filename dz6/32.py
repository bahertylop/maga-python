r"""
**Задача 32 (merge/join/anti-join).** Создайте `sales` и `customers`. Примените `merge(how="inner")`, `"left"`, `"right"`, `"outer"`, `"left_anti"`, `"right_anti"`. Используйте `on="customer_id"`, `left_on`/`right_on`, `suffixes=("_s", "_c")`, `indicator=True`. Проверьте `validate="one_to_one"` — зафиксируйте `MergeError` при дубликатах. Создайте `sales.set_index("customer_id").join(customers.set_index("customer_id"))`. Ожидаемый вывод: `inner` оставляет только совпадающие ключи; `left_anti` возвращает продажи без клиентов; `indicator=True` добавляет столбец `_merge`; `validate="one_to_one"` вызывает `MergeError` при дубликатах. В комментариях объясните: чем `merge` отличается от `join` (`join` — по индексу, `merge` — по столбцам); когда anti-join полезен (поиск «осиротевших» продаж без клиентов); что делает `indicator=True` (добавляет `_merge` с `"both"`/`"left_only"`/`"right_only"`); как `suffixes` предотвращает конфликт имён; почему `validate` защищает от декартова произведения; как `merge` обрабатывает `NaN` в ключах (не совпадают, остаются в `left_only`/`right_only`).
"""
import pandas as pd

customers = pd.DataFrame({"customer_id": [1, 2, 3], "name": ["Анна", "Борис", "Вера"], "city": ["Москва", "СПб", "Казань"]})
sales = pd.DataFrame({"sale_id": [10, 11, 12, 13], "customer_id": [1, 2, 2, 9], "amount": [100, 200, 300, 400], "city": ["М", "С", "С", "?"]})
for how in ("inner", "left", "right", "outer"):
    print(how, "->", len(sales.merge(customers, on="customer_id", how=how)))
try:
    print("left_anti (продажи без клиента):\n", sales.merge(customers, on="customer_id", how="left_anti"))
except ValueError as e:
    print("left_anti не поддерживается:", e)
    print(sales[~sales["customer_id"].isin(customers["customer_id"])])
m = sales.merge(customers, on="customer_id", how="outer", suffixes=("_s", "_c"), indicator=True)
print(m[["customer_id", "city_s", "city_c", "_merge"]])
print("left_on/right_on:", len(sales.merge(customers.rename(columns={"customer_id": "cid"}), left_on="customer_id", right_on="cid")))
dup = pd.concat([customers, customers.iloc[[0]]])
try:
    sales.merge(dup, on="customer_id", validate="many_to_one")
except pd.errors.MergeError as e:
    print("validate ->", type(e).__name__, str(e)[:55])
print(sales.set_index("customer_id").join(customers.set_index("customer_id"), rsuffix="_c").head(3))
# merge - по столбцам (или индексу), join - по ИНДЕКСУ. anti-join находит «осиротевшие» записи (продажи без клиента).
# indicator=True добавляет _merge: both / left_only / right_only. suffixes разруливают конфликт одноимённых столбцов.
# validate (one_to_one, many_to_one...) защищает от неожиданного размножения строк (декартово произведение при дублях ключа).
# Внимание: NaN в ключах Pandas сопоставляет друг с другом (в SQL NULL с NULL не совпадает) - чистите ключи перед merge.
