r"""
**Задача 52 (SQL + Pandas + viz).** Возьмите SQL-запрос из задачи 46, реализуйте в Pandas, постройте через `df.plot(kind="barh", x="city", y="avg_amount")`. Добавьте `ax.axvline(df["avg_amount"].mean(), color="red", linestyle="--", label="Среднее")`. Примените `ax.set_xlabel("Средний чек (руб.)")`, `ax.legend()`. Ожидаемый вывод: горизонтальные столбцы по городам; вертикальная линия среднего; легенда; подпись оси. В комментариях объясните: как аннотировать средний уровень (axvline); почему `barh` удобнее для длинных названий городов; как сохранить график с высоким разрешением (`dpi=300`); что произойдёт при `plot` без `figsize`; как добавить подписи значений на столбцы (`ax.bar_label`); как сравнить два среза на одном графике (`hue`/`stacked`).
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

rng = np.random.default_rng(52)
customers = pd.DataFrame({"customer_id": range(1, 801), "city": rng.choice(["Москва", "Санкт-Петербург", "Нижний Новгород", "Казань", "Сочи"], 800)})
sales = pd.DataFrame({"customer_id": rng.integers(1, 801, 4000), "amount": rng.normal(2e6, 5e5, 4000), "status": rng.choice(["completed", "cancelled"], 4000, p=[0.85, 0.15])})
res = (sales.merge(customers, on="customer_id").query("status == 'completed'").groupby("city").agg(cnt=("amount", "size"), avg_amount=("amount", "mean"))
       .reset_index().query("cnt > 100").sort_values("avg_amount"))
fig, ax = plt.subplots(figsize=(10, 5))
res.plot(kind="barh", x="city", y="avg_amount", ax=ax, legend=False, color="tab:blue")
ax.axvline(res["avg_amount"].mean(), color="red", linestyle="--", label="Среднее")
ax.set_xlabel("Средний чек (руб.)"); ax.set_ylabel(""); ax.legend(); ax.set_title("Средний чек по городам")
ax.bar_label(ax.containers[0], fmt="%.0f", padding=3)
fig.tight_layout(); fig.savefig(Path(__file__).parent / "plot_52.png", dpi=300); plt.close(fig)
print(res.round(0)); print("среднее по городам:", round(res["avg_amount"].mean())); print("сохранено plot_52.png (dpi=300)")
# axvline рисует вертикальную линию среднего (для barh значения лежат по X; для вертикальных bar нужна axhline).
# barh удобнее для длинных названий городов: подписи горизонтальны и не накладываются. Без figsize график рисуется
# в размере по умолчанию (6.4x4.8 дюйма) - длинные подписи могут не поместиться. Подписи значений: ax.bar_label(ax.containers[0]).
# Сравнение двух срезов: hue/stacked - в Pandas через plot(kind="barh", stacked=True) на таблице pivot (по столбцу на срез)
# или в Seaborn sns.barplot(hue=...). dpi=300 - высокое разрешение для печати. Условие cnt > 100 - аналог HAVING из задачи 46.
