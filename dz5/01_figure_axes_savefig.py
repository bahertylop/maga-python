"""Задача 1. Figure, Axes, даты, сохранение графика.
Условие: данные sales.csv (date, cars_sold), прочитать parse_dates/index_col,
построить график, сохранить cars_sold.png (dpi=150, bbox_inches='tight'),
вывести типы. Пояснения ниже."""
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


# Если CSV отсутствует, создаём небольшой пример, чтобы файл можно было запустить.
if Path("sales.csv").exists():
    df = pd.read_csv("sales.csv", parse_dates=["date"], index_col="date")
else:
    dates = pd.date_range("2026-01-01", periods=10, freq="D")
    df = pd.DataFrame({"cars_sold": [4, 5, 3, 7, 6, 8, 5, 9, 6, 7]}, index=dates)
    df.index.name = "date"

fig, ax = plt.subplots()  # Обычно создаёт Figure и одну Axes (эквивалент subplot(1,1,1)).
ax.plot(df.index, df["cars_sold"], marker="o")
ax.set(title="Продажи автомобилей по дням", xlabel="Дата", ylabel="Количество")
fig.savefig("cars_sold.png", dpi=150, bbox_inches="tight")  # Сохраняем ДО show.
print(type(fig), type(ax), df.index.dtype)
plt.show()

# Figure (fig) — весь холст: размер, фон, suptitle, несколько Axes, colorbar.
# Axes (ax) — конкретная область построения: данные, оси, сетка, подписи.
# plt.subplots() создаёт Figure и добавляет subplot с позицией 111 (1x1, первый).
# savefig перед show безопаснее: интерактивный backend после show иногда закрывает/очищает фигуру.
# bbox_inches='tight' обрезает лишние поля, чтобы длинные подписи не обрезались.
# Без parse_dates даты остаются строками: обычно воспринимаются как категориальные значения,
# а не как календарная ось времени; иногда даты могут быть интерпретированы некорректно.
# x/y разной длины вызовут ValueError: x and y must have same first dimension.
