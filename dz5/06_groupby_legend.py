"""Задача 6. Группировка по маркам и настройка легенды."""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
if Path("sales_by_brand.csv").exists():
    df = pd.read_csv("sales_by_brand.csv", parse_dates=["date"])
else:
    df = pd.DataFrame({"date": pd.date_range("2026-01-01", periods=4).tolist()*5,
                      "brand": [b for b in ["Toyota", "Hyundai", "Kia", "Volkswagen", "Renault"] for _ in range(4)],
                      "count": [10, 12, 11, 14, 9, 8, 10, 12, 6, 8, 9, 11, 7, 9, 10, 12, 5, 7, 8, 9]})
fig, ax = plt.subplots(layout="constrained")
for brand, g in df.groupby("brand"):
    ax.plot(g["date"], g["count"], marker="o", label=brand)
ax.set(title="Продажи по маркам", xlabel="Дата", ylabel="Продано")
ax.legend(loc="upper left", ncol=2, title="Марки", framealpha=.9)
# groupby формирует подтаблицы для каждого значения brand — удобно для серий на одном графике.
# ncol=2 размещает элементы в две колонки, помогает при большом количестве марок.
# bbox_to_anchor — координата привязки в долях Axes; loc определяет, какой угол/край
# легенды совмещается с этой точкой. bbox_to_anchor=(1.02,.5) выносит легенду вправо.
ax.legend(loc="upper left", ncol=2, title="Марки", framealpha=.9, bbox_to_anchor=(1.02, .5), borderaxespad=0)
# borderaxespad=0 убирает отступ легенды от заданной точки. label обязателен,
# иначе линия не попадёт в легенду; label начинающийся с '_' игнорируется.
# Если у всех объектов нет подходящих labels, Matplotlib выдаёт No artists with labels found.
plt.show()
