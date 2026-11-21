r"""
**Задача 59 (мини-проект: EDA + очистка + FE).** Загрузите `customers.csv` (`parse_dates=["registered_at"]`), `cars.csv`, `sales.csv` (`parse_dates=["sale_date"]`), `services.csv`. Проведите EDA: `info()`, `describe()`, `value_counts()`, `isna().sum()`, `duplicated().sum()`. Очистка: `drop_duplicates(subset="customer_id", keep="first")`, проверка диапазонов, ссылочной целостности через `.isin()`. Feature engineering: `merge` четырёх таблиц, `revenue = price * (1 - discount)`, `profit = revenue - cost`, `year/month/quarter` через `.dt`, `age_group` через `pd.cut`. Сохраните в `full.parquet`. Ожидаемый вывод: 51 пропуск в `email`, 10 дубликатов в `customers`; после очистки 1000 клиентов; итоговый DataFrame 50 000 × 15; Parquet сохраняет `category` и `datetime64[us]`. В комментариях объясните: зачем `parse_dates` при загрузке (тип `datetime` вместо строки); как проверить ссылочную целостность (`sales["customer_id"].isin(customers["customer_id"])`); почему `pd.cut` с фиксированными границами надёжнее `qcut` (не зависит от данных); как `merge` четырёх таблиц влияет на размер (декартово произведение при дубликатах); зачем сохранять в Parquet (типы, скорость); как `profit` считается с учётом скидки и себестоимости.
"""
import numpy as np
import pandas as pd
from pathlib import Path

here = Path(__file__).parent / "project_data"; here.mkdir(exist_ok=True)
rng = np.random.default_rng(59)
# ---------- 0. Генерация исходных CSV (в реальной задаче они уже есть) ----------
n_c = 1000
cust = pd.DataFrame({"customer_id": np.arange(1, n_c + 1), "name": [f"Клиент {i}" for i in range(1, n_c + 1)],
                     "city": rng.choice(["Москва", "СПб", "Казань", "Сочи", "Екатеринбург"], n_c), "age": rng.integers(18, 80, n_c),
                     "email": [f"user{i}@mail.ru" for i in range(1, n_c + 1)], "registered_at": pd.date_range("2018-01-01", periods=n_c, freq="D").astype(str)})
cust.loc[rng.choice(n_c, 51, replace=False), "email"] = None
cust = pd.concat([cust, cust.sample(10, random_state=1)], ignore_index=True)       # 10 дубликатов
cust.to_csv(here / "customers.csv", index=False)
cars = pd.DataFrame({"car_id": np.arange(1, 201), "brand": rng.choice(["Toyota", "BMW", "Kia", "Audi", "Lada"], 200), "price": rng.integers(8, 60, 200) * 100_000, "cost_ratio": rng.uniform(0.7, 0.9, 200)})
cars["cost"] = (cars["price"] * cars["cost_ratio"]).round(0); cars.drop(columns="cost_ratio").to_csv(here / "cars.csv", index=False)
n_s = 50_000
sales = pd.DataFrame({"sale_id": np.arange(1, n_s + 1), "customer_id": rng.integers(1, n_c + 1, n_s), "car_id": rng.integers(1, 201, n_s),
                      "discount": rng.uniform(0, 0.15, n_s).round(3), "status": rng.choice(["completed", "cancelled", "pending"], n_s, p=[0.8, 0.1, 0.1]),
                      "sale_date": pd.to_datetime("2023-01-01") + pd.to_timedelta(rng.integers(0, 730, n_s), unit="D")})
sales.to_csv(here / "sales.csv", index=False)
pd.DataFrame({"service_id": np.arange(1, 5001), "sale_id": rng.integers(1, n_s + 1, 5000), "service_cost": rng.integers(1, 30, 5000) * 1000}).to_csv(here / "services.csv", index=False)

# ---------- 1. Загрузка ----------
customers = pd.read_csv(here / "customers.csv", parse_dates=["registered_at"])
cars = pd.read_csv(here / "cars.csv"); sales = pd.read_csv(here / "sales.csv", parse_dates=["sale_date"]); services = pd.read_csv(here / "services.csv")
# ---------- 2. EDA ----------
print("customers dtypes:", dict(customers.dtypes.astype(str)))
print(customers.describe().round(1).T[["count", "mean", "min", "max"]])
print("статусы:", sales["status"].value_counts().to_dict())
print("пропуски в customers:", customers.isna().sum()[lambda s: s > 0].to_dict(), "| дубликаты (customer_id):", customers.duplicated(subset="customer_id").sum(), "| полные:", customers.duplicated().sum())
# ---------- 3. Очистка ----------
customers = customers.drop_duplicates(subset="customer_id", keep="first")
print("клиентов после очистки:", len(customers))
assert customers["age"].between(18, 100).all() and (cars["price"] > 0).all() and sales["discount"].between(0, 1).all()
print("ссылочная целостность sales->customers:", sales["customer_id"].isin(customers["customer_id"]).all(), "| sales->cars:", sales["car_id"].isin(cars["car_id"]).all())
# ---------- 4. Feature engineering ----------
svc = services.groupby("sale_id", as_index=False)["service_cost"].sum()
full = (sales.merge(customers[["customer_id", "city", "age"]], on="customer_id", how="left", validate="many_to_one")
        .merge(cars[["car_id", "brand", "price", "cost"]], on="car_id", how="left", validate="many_to_one")
        .merge(svc, on="sale_id", how="left", validate="one_to_one"))
full["service_cost"] = full["service_cost"].fillna(0)
full["revenue"] = full["price"] * (1 - full["discount"]); full["profit"] = full["revenue"] - full["cost"]
full["year"], full["month"], full["quarter"] = full["sale_date"].dt.year, full["sale_date"].dt.month, full["sale_date"].dt.quarter
full["age_group"] = pd.cut(full["age"], [0, 25, 35, 45, 55, 120], labels=["<=25", "26-35", "36-45", "46-55", "56+"])
for c in ("city", "brand", "status"):
    full[c] = full[c].astype("category")
print("итог:", full.shape, "| строк sales:", len(sales), "(должно совпасть - дубликатов ключей нет)")
print(full[["revenue", "profit"]].describe().round(0).loc[["mean", "min", "max"]])
out = here / "full.parquet"
try:
    full.to_parquet(out); back = pd.read_parquet(out); print("Parquet:", back["brand"].dtype, back["sale_date"].dtype)
except ImportError:
    out = here / "full.pkl"; full.to_pickle(out); print("pyarrow не установлен -> сохранено в pickle (", out.name, "), типы тоже сохраняются:", full["brand"].dtype, full["sale_date"].dtype)
# parse_dates сразу превращает строку в datetime64 (иначе - str: нельзя .dt, сортировка по тексту, нет арифметики дат).
# Ссылочная целостность: sales["customer_id"].isin(customers["customer_id"]).all() - нет «осиротевших» продаж (иначе left merge даст NaN).
# pd.cut с ФИКСИРОВАННЫМИ границами надёжнее qcut: группы одинаковы при любом наборе данных (qcut зависит от распределения).
# merge нескольких таблиц: при дубликатах ключа в правой таблице строки размножаются (декартово произведение по ключу) - поэтому
# validate="many_to_one"/"one_to_one" и предварительная свёртка services по sale_id (агрегация), иначе размер таблицы вырастет.
# Parquet хранит типы (category, datetime), сжат, быстро читается по столбцам, в отличие от CSV (всё - текст). Без pyarrow - pickle.
# profit = revenue - cost, где revenue = price * (1 - discount): скидка уменьшает выручку, себестоимость от неё не зависит.
# Контрольные числа из задания (51 пропуск, 10 дублей, 1000 клиентов) воспроизведены на синтетических данных; 15 столбцов зависит от набора признаков.
