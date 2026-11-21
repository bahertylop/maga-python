"""
Задача 49 (Seaborn set_theme и relplot с col/row). Автосалон анализирует данные о чаевых (встроенный tips) как аналог анализа среднего чека в сервисном центре. Seaborn — надстройка над Matplotlib, которая автоматизирует «красивые дефолты» и группировку. Выполните sns.set_theme(style="whitegrid", palette="muted", font_scale=1.2), загрузите tips = sns.load_dataset("tips"), постройте g = sns.relplot(data=tips, x="total_bill", y="tip", hue="sex", col="time", row="smoker", kind="scatter", height=3, aspect=1.2). Настройте g.set_titles("{col_name} — {row_name}"), g.set_axis_labels("Сумма счёта", "Чаевые"), g.fig.suptitle(...). Ожидаемый вывод: 2×2 FacetGrid (пол × время × курение). В комментариях объясните: как col/row строят сетку (col — столбцы, row — строки); что такое FacetGrid (обёртка над сеткой подграфиков); чем relplot (figure-level) отличается от scatterplot (axes-level) — первый создаёт сетку, второй рисует на одной оси; как ax= встраивает axes-level функцию в matplotlib-фигуру; что делает col_wrap=2 (переносит сетку, если много столбцов); как g.savefig("grid.png", dpi=200, bbox_inches="tight") сохраняет всю сетку.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

HERE = Path(__file__).parent


def load_tips():
    """Встроенный датасет скачивается с GitHub; без сети строим синтетический аналог."""
    try:
        return sns.load_dataset("tips")
    except Exception:
        rng = np.random.default_rng(49)
        n = 244
        bill = rng.gamma(4, 5, n).clip(3, 50)
        return pd.DataFrame({
            "total_bill": bill, "tip": (bill * rng.uniform(0.08, 0.22, n)).round(2),
            "sex": rng.choice(["Male", "Female"], n), "smoker": rng.choice(["Yes", "No"], n),
            "day": rng.choice(["Thur", "Fri", "Sat", "Sun"], n),
            "time": rng.choice(["Lunch", "Dinner"], n, p=[0.3, 0.7]), "size": rng.integers(1, 6, n)})


# set_theme задаёт стиль, палитру и масштаб шрифтов ГЛОБАЛЬНО (через rcParams)
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.2)
tips = load_tips()

# relplot - FIGURE-level: сам создаёт Figure и сетку подграфиков (FacetGrid). col=... -
# отдельный СТОЛБЕЦ на каждое значение (Lunch/Dinner), row=... - отдельная СТРОКА (smoker
# Yes/No); hue красит точки внутри каждой ячейки. Итого 2x2 ячейки, в каждой пол (цвет).
# FacetGrid - обёртка над сеткой Axes: хранит данные, разбивает по col/row/hue и рисует в
# каждой ячейке одну и ту же функцию.
g = sns.relplot(data=tips, x="total_bill", y="tip", hue="sex", col="time", row="smoker",
                kind="scatter", height=3, aspect=1.2)
g.set_titles("{col_name} — {row_name}")          # шаблон: значения из col и row
g.set_axis_labels("Сумма счёта", "Чаевые")
g.fig.suptitle("Чаевые: время × курение × пол", y=1.02)
# g.savefig сохраняет ВСЮ сетку (а не одну Axes); bbox_inches="tight" - чтобы suptitle
# и легенда за пределами осей не обрезались.
g.savefig(HERE / "49_grid.png", dpi=200, bbox_inches="tight")

# col_wrap=2: если одна категория (нет row) и значений в col много, сетка переносится на
# новую строку после 2 столбцов. Сочетать col_wrap с row нельзя.
g2 = sns.relplot(data=tips, x="total_bill", y="tip", hue="sex", col="day", col_wrap=2,
                 height=3, aspect=1.2)
g2.savefig(HERE / "49_wrap.png", dpi=120, bbox_inches="tight")

# axes-level (scatterplot) рисует на ОДНОЙ оси и принимает ax=: так её встраивают в
# обычный plt.subplots рядом с чистым Matplotlib. Сетку он не создаёт.
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4), layout="constrained")
sns.scatterplot(data=tips, x="total_bill", y="tip", hue="sex", ax=a1)
a2.hist(tips["tip"], bins=20)                     # обычный Matplotlib на соседней оси
a1.set_title("scatterplot(ax=...)")
fig.savefig(HERE / "49_axes_level.png", dpi=120)
print("grid shape:", g.axes.shape)
