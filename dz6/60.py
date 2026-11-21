r"""
**Задача 60 (мини-проект: визуализация + выводы).** Используя `full.parquet` из задачи 59, ответьте на 5 бизнес-вопросов: динамика (`groupby(dt.to_period("M"))["revenue"].sum()` → `line`), бренды (`groupby("brand", observed=True).agg(...)` → `barh`), топ-клиенты (`nlargest(10)`), статусы (`groupby("status").size()` → `pie`), города (`groupby("city")["revenue"].sum().sort_values()` → `bar`). Для каждого графика примените `figsize`, `title`, `grid`, `axhline` со средним; сохраните в PNG с `dpi=300`. Сформулируйте 3–5 бизнес-рекомендаций. Ожидаемый вывод: 5 графиков с осмысленными заголовками и линией среднего; 3–5 проверяемых рекомендаций с числами; указаны ограничения (корреляция ≠ причинность, сезонность, выбросы). В комментариях объясните: как аннотировать среднее на графике (`axhline`); почему `barh` удобнее для длинных названий брендов и городов; как скользящее среднее помогает в динамике; какие ограничения у анализа (сезонность авторынка, акции); как проверить отсутствие отрицательных `revenue`; как сравнить два года на одном графике через `pivot`.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

here = Path(__file__).parent
rng = np.random.default_rng(60)
# Таблица full из задачи 59 (если 59.py уже запускался - читаем её; иначе строим эквивалент)
src = [p for p in (here / "project_data" / "full.parquet", here / "project_data" / "full.pkl") if p.exists()]
if src:
    full = pd.read_parquet(src[0]) if src[0].suffix == ".parquet" else pd.read_pickle(src[0])
else:
    n = 20_000
    brands = np.array(["Toyota", "BMW", "Kia", "Audi", "Lada"]); cities = np.array(["Москва", "СПб", "Казань", "Сочи", "Екатеринбург"])
    full = pd.DataFrame({"customer_id": rng.integers(1, 1001, n), "brand": rng.choice(brands, n), "city": rng.choice(cities, n, p=[0.4, 0.25, 0.15, 0.1, 0.1]),
                         "status": rng.choice(["completed", "cancelled", "pending"], n, p=[0.8, 0.1, 0.1]), "price": rng.integers(8, 60, n) * 100_000.0,
                         "discount": rng.uniform(0, 0.15, n), "sale_date": pd.to_datetime("2023-01-01") + pd.to_timedelta(rng.integers(0, 730, n), unit="D")})
    full["revenue"] = full["price"] * (1 - full["discount"]); full["profit"] = full["revenue"] - full["price"] * 0.8
    for c in ("brand", "city", "status"):
        full[c] = full[c].astype("category")
print("данные:", full.shape, "| отрицательная выручка:", int((full["revenue"] < 0).sum()), "(проверка)")
out = here / "report_60"; out.mkdir(exist_ok=True)
def save(fig, name):
    fig.tight_layout(); fig.savefig(out / name, dpi=300); plt.close(fig)
# 1. динамика
m = full.groupby(full["sale_date"].dt.to_period("M"))["revenue"].sum() / 1e6
fig, ax = plt.subplots(figsize=(11, 4.5)); m.plot(kind="line", ax=ax, marker="o", label="Выручка")
m.rolling(3, min_periods=1).mean().plot(ax=ax, ls=":", label="скользящее (3 мес.)")
ax.axhline(m.mean(), color="red", ls="--", label=f"Среднее {m.mean():.0f}"); ax.set_title("Выручка по месяцам, млн руб."); ax.set_ylabel("млн руб."); ax.grid(True, alpha=0.4); ax.legend(); save(fig, "1_dynamics.png")
# 2. бренды
b = full.groupby("brand", observed=True).agg(revenue=("revenue", "sum"), profit=("profit", "sum"), n=("revenue", "size")).sort_values("revenue")
fig, ax = plt.subplots(figsize=(9, 4.5)); (b["revenue"] / 1e6).plot(kind="barh", ax=ax); ax.axvline(b["revenue"].mean() / 1e6, color="red", ls="--", label="Среднее по брендам")
ax.set_title("Выручка по брендам, млн руб."); ax.grid(True, alpha=0.4); ax.legend(); save(fig, "2_brands.png")
# 3. топ-клиенты
top = full.groupby("customer_id")["revenue"].sum().nlargest(10) / 1e6
fig, ax = plt.subplots(figsize=(9, 4.5)); top.sort_values().plot(kind="barh", ax=ax); ax.axvline(full.groupby("customer_id")["revenue"].sum().mean() / 1e6, color="red", ls="--", label="Среднее по клиентам")
ax.set_title("Топ-10 клиентов по выручке, млн руб."); ax.set_ylabel("customer_id"); ax.grid(True, alpha=0.4); ax.legend(); save(fig, "3_top_customers.png")
# 4. статусы
st = full.groupby("status", observed=True).size()
fig, ax = plt.subplots(figsize=(6, 6)); st.plot(kind="pie", autopct="%1.1f%%", ax=ax, ylabel=""); ax.set_title("Статусы продаж"); save(fig, "4_status.png")
# 5. города
cty = full.groupby("city", observed=True)["revenue"].sum().sort_values() / 1e6
fig, ax = plt.subplots(figsize=(9, 4.5)); cty.plot(kind="bar", ax=ax, rot=0); ax.axhline(cty.mean(), color="red", ls="--", label="Среднее по городам")
ax.set_title("Выручка по городам, млн руб."); ax.grid(True, alpha=0.4, axis="y"); ax.legend(); save(fig, "5_cities.png")
# Сравнение двух лет через pivot
yr = full.assign(year=full["sale_date"].dt.year, month=full["sale_date"].dt.month).pivot_table(index="month", columns="year", values="revenue", aggfunc="sum") / 1e6
print("выручка по месяцам, год к году (первые 3):\n", yr.head(3).round(1))
done = full["status"].eq("completed").mean() * 100
print("\nВЫВОДЫ:")
lost = full.loc[full["status"] != "completed", "revenue"].sum() / 1e6
print(f"1) Завершено {done:.1f}% сделок; на отменённые/ожидающие приходится {lost:.0f} млн руб. выручки по прайсу - возврат каждой десятой такой сделки дал бы +{lost*0.1:.0f} млн руб.")
print(f"2) Лидер по выручке - {b.index[-1]} ({b['revenue'].iloc[-1]/b['revenue'].sum()*100:.0f}% общей), аутсайдер - {b.index[0]} ({b['revenue'].iloc[0]/b['revenue'].sum()*100:.0f}%).")
print(f"3) Топ-10 клиентов дают лишь {top.sum()/(full['revenue'].sum()/1e6)*100:.1f}% выручки: зависимости от VIP нет, рост надо искать в широкой базе (кампании по сегментам), а не в точечной работе с топ-клиентами.")
print(f"4) Город {cty.index[-1]} приносит {cty.iloc[-1]/cty.sum()*100:.0f}% выручки; {cty.index[0]} - {cty.iloc[0]/cty.sum()*100:.0f}%.")
print("Ограничения: корреляция != причинность; данные за 2 года - сезонность (авторынок: весна/конец года, акции) не отделена от тренда; выбросы (VIP-клиенты) искажают средние; синтетические данные.")
print("PNG сохранены в:", out.name)
# axhline/axvline рисует линию среднего: для вертикальных столбцов/линий - axhline, для barh - axvline.
# barh удобнее для длинных названий брендов/городов (подписи горизонтальны). Скользящее среднее (3 мес.) сглаживает сезонные скачки и
# показывает тренд. Ограничения анализа: сезонность авторынка, акции и скидки, малое число лет, выбросы, корреляция != причинность.
# Отрицательную выручку проверяем (revenue < 0).sum() == 0 до построения графиков. Два года на одном графике: pivot_table(index="month",
# columns="year") -> yr.plot(): по линии на год. dpi=300 - печатное качество. Рекомендации должны быть проверяемыми (числа выше пересчитываются).
