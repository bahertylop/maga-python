"""Задача 7. Топ моделей: bar и barh, value_counts."""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
if Path("sales.csv").exists():
    df = pd.read_csv("sales.csv")
    if "model" not in df: df["model"] = ["Model " + str(i % 12) for i in range(len(df))]
else:
    df = pd.DataFrame({"model": ["Sedan A", "SUV B", "Hatch C", "Sedan A", "SUV B", "Coupe D", "Sedan A", "SUV B", "Wagon E", "Hatch C"]})
top = df["model"].value_counts().head(10)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), layout="constrained")
ax1.bar(top.index, top.values)
for i, v in enumerate(top.values): ax1.text(i, v + .1, str(v), ha="center")
ax1.set_title("Топ моделей (bar)"); ax1.tick_params(axis="x", rotation=45)
ax2.barh(top.index[::-1], top.values[::-1])
for i, v in enumerate(top.values[::-1]): ax2.text(v + .1, i, str(v), va="center")
ax2.set_title("Топ моделей (barh)")
# value_counts сортирует по убыванию; head(10) оставляет первые десять.
# В barh разворачиваем массивы, чтобы лидер отображался сверху; без разворота — снизу.
# Сравнение столбцов должно начинаться с нуля: ylim(50,200) обрезает основание и преувеличивает разницу.
# barh удобен для длинных названий. normalize=True даёт доли (0..1), можно умножить на 100.
# Подписи можно поставить внутрь столбца, например ax.text(v/2, i, str(v), ha='center', color='white').
plt.show()
