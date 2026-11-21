"""
Задача 51 (Seaborn: категориальные — boxplot, violinplot, barplot, countplot). Автосалон анализирует данные Titanic (встроенный датасет — модель для понимания выживаемости пассажиров, аналогично анализу удержания клиентов). Постройте 4 подграфика: boxplot(x="class", y="age", hue="sex"), violinplot(x="class", y="age", hue="sex", split=True) (split=True — половина «скрипки» для каждой группы), barplot(x="class", y="survived", errorbar="ci") (среднее с CI), countplot(x="class", hue="sex") (частоты). Дополнительно g = sns.catplot(data=titanic, x="class", y="survived", col="sex", kind="bar", errorbar="ci"). Ожидаемый вывод: 5 видов категориальных графиков. В комментариях объясните: когда violinplot лучше boxplot (когда важна плотность распределения — мультимодальность); что делает split=True (разделяет «скрипку» пополам для двух групп — сравнение распределений напрямую); почему barplot показывает среднее (не сумму — для суммы используйте df.groupby(...).agg("sum")); что кодирует errorbar="ci" (доверительный интервал среднего); чем countplot отличается от barplot (частоты vs значения); как catplot (figure-level) vs barplot (axes-level) — когда что.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

HERE = Path(__file__).parent


def load_titanic():
    try:
        return sns.load_dataset("titanic")
    except Exception:       # без сети - синтетический аналог с теми же колонками
        rng = np.random.default_rng(51)
        n = 891
        cls = rng.choice(["First", "Second", "Third"], n, p=[0.24, 0.21, 0.55])
        sex = rng.choice(["male", "female"], n, p=[0.65, 0.35])
        age = np.clip(rng.normal({"First": 38, "Second": 30, "Third": 25}.__getitem__(cls[0]), 12, n), 1, 80)
        age = np.array([rng.normal({"First": 38, "Second": 30, "Third": 25}[c], 12) for c in cls]).clip(1, 80)
        p = np.where(sex == "female", 0.72, 0.19) * np.select([cls == "First", cls == "Second"], [1.2, 1.0], 0.75)
        return pd.DataFrame({"survived": (rng.random(n) < p.clip(0, 1)).astype(int),
                             "class": pd.Categorical(cls, ["First", "Second", "Third"], ordered=True),
                             "sex": sex, "age": age})


sns.set_theme(style="whitegrid")
titanic = load_titanic()

fig, axes = plt.subplots(2, 2, figsize=(14, 10), layout="constrained")
# boxplot - квартили/медиана/выбросы, компактно
sns.boxplot(data=titanic, x="class", y="age", hue="sex", ax=axes[0, 0])
# violinplot: к квартилям добавляет ФОРМУ плотности (видна мультимодальность - два горба),
# split=True рисует по половинке «скрипки» для каждой из двух групп hue (m/f) на ОДНОМ
# теле -> распределения сравниваются напрямую, без двух отдельных фигур.
sns.violinplot(data=titanic, x="class", y="age", hue="sex", split=True, ax=axes[0, 1])
# barplot: СРЕДНЕЕ y по категории (не сумма! для суммы - groupby(...).agg("sum") или
# estimator="sum"). Для 0/1 среднее = доля выживших. errorbar="ci" - доверительный
# интервал среднего (95%, считается бутстрепом) - тонкая линия на столбце.
sns.barplot(data=titanic, x="class", y="survived", errorbar="ci", ax=axes[1, 0])
# countplot: ЧАСТОТЫ (число строк) в каждой категории - значения y не нужны. Сравните с
# barplot: тот агрегирует значение колонки (среднее), этот считает наблюдения.
sns.countplot(data=titanic, x="class", hue="sex", ax=axes[1, 1])
for ax, t in zip(axes.ravel(), ["boxplot", "violinplot(split=True)", "barplot(errorbar='ci')", "countplot"]):
    ax.set_title(t)
fig.savefig(HERE / "51_axes_level.png", dpi=150)

# catplot - FIGURE-level: сетка по col/row (здесь отдельная панель на пол). Берите его,
# когда нужны фасеты по категории; axes-level (barplot и др.) - когда график идёт в
# вашу сетку plt.subplots рядом с другими.
g = sns.catplot(data=titanic, x="class", y="survived", col="sex", kind="bar", errorbar="ci", height=4)
g.set_titles("{col_name}")
g.set_axis_labels("Класс", "Доля выживших")
g.savefig(HERE / "51_catplot.png", dpi=150, bbox_inches="tight")
print(titanic.groupby("class", observed=True)["survived"].mean().round(2).to_dict())
