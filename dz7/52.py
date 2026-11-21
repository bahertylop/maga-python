"""
Задача 52 (Seaborn: heatmap, clustermap и pivot). Автосалон анализирует продажи по маркам и месяцам (встроенный flights — как аналог). Постройте p = flights.pivot(index="month", columns="year", values="passengers"). Seaborn: sns.heatmap(p, cmap="YlGnBu", annot=True, fmt="d") (с аннотациями), sns.heatmap(p.corr(), cmap="RdBu", vmin=-1, vmax=1, center=0) (корреляции с центром 0), sns.clustermap(p, cmap="viridis", standard_scale=1) (иерархическая кластеризация строк и столбцов). Ожидаемый вывод: 3 heatmap-типа; clustermap переставляет строки/столбцы по схожести. В комментариях объясните: что делает annot=True (добавляет значения в ячейки) и зачем fmt="d" (целые числа); зачем center=0 в корреляциях (белый = ноль, красный = положительный); что такое clustermap (кластеризация — похожие месяцы/годы рядом); как standard_scale=1 нормализует по строкам (сравнение месяцев с разным масштабом); что произойдёт при annot=True на 100×100 (мелко — отключите); как сохранить clustermap через g.savefig (это отдельная фигура, а не Axes).
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

HERE = Path(__file__).parent
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def load_flights():
    try:
        return sns.load_dataset("flights")
    except Exception:       # синтетика: рост по годам + летний сезон
        rng = np.random.default_rng(52)
        rows = [(y, m, int((110 + (y - 1949) * 25) * (1 + 0.3 * np.sin((i - 3) / 12 * 2 * np.pi))
                           + rng.normal(0, 8)))
                for y in range(1949, 1961) for i, m in enumerate(MONTHS)]
        df = pd.DataFrame(rows, columns=["year", "month", "passengers"])
        df["month"] = pd.Categorical(df["month"], MONTHS, ordered=True)
        return df


flights = load_flights()
# pivot: «длинная» таблица -> «широкая» матрица (строки - месяцы, столбцы - годы, ячейки -
# значения). Порядок месяцев сохраняется, т.к. month - упорядоченная категория.
p = flights.pivot(index="month", columns="year", values="passengers")

fig, axes = plt.subplots(1, 2, figsize=(18, 7), layout="constrained")
# annot=True пишет значение в каждую ячейку; fmt="d" - формат целого числа (без .0 и
# научной записи). На 100x100 аннотации превращаются в нечитаемую кашу и тормозят
# отрисовку - там annot=False.
sns.heatmap(p, cmap="YlGnBu", annot=True, fmt="d", ax=axes[0], cbar_kws={"label": "Пассажиры"})
axes[0].set_title("heatmap с аннотациями")

# Корреляции лежат в [-1, 1]: vmin/vmax фиксируют диапазон, center=0 помещает
# нейтральный цвет (белый) в ноль: красный - положительная связь, синий - отрицательная.
sns.heatmap(p.corr(), cmap="RdBu", vmin=-1, vmax=1, center=0, ax=axes[1])
axes[1].set_title("Корреляции между годами")
fig.savefig(HERE / "52_heatmaps.png", dpi=150)

# clustermap - heatmap + иерархическая кластеризация строк и столбцов: похожие по профилю
# месяцы/годы ставятся рядом, слева/сверху рисуются дендрограммы.
# standard_scale=1 нормирует КАЖДЫЙ СТОЛБЕЦ (год) в [0, 1] (минус min, делить на max) -
# так сравнивается форма сезонности независимо от общего масштаба года. (Внимание: в
# seaborn 0 = по строкам, 1 = по столбцам; в тексте задачи указано «по строкам» - неточно.)
# clustermap - figure-level: создаёт собственную фигуру (ClusterGrid), поэтому сохраняем
# через g.savefig (или g.fig.savefig), а не plt.savefig на «оси».
g = sns.clustermap(p, cmap="viridis", standard_scale=1, figsize=(9, 8))
g.savefig(HERE / "52_clustermap.png", dpi=150)
print("порядок строк после кластеризации:", [p.index[i] for i in g.dendrogram_row.reordered_ind])
