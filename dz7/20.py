"""
Задача 20 (pie топ-N с «Прочее»). Автосалон визуализирует распределение продаж по моделям — их десятки, но в презентации нужны только топ-5 плюс «Прочее». Получите counts = df["model"].value_counts(), оставьте top5 = counts.head(5), посчитайте other = counts.iloc[5:].sum(), объедините через pd.concat([top5, pd.Series({"Прочее": other})]). Постройте ax.pie(combined.values, labels=combined.index, autopct="%1.1f%%", explode=(0.05, 0, 0, 0, 0, 0), wedgeprops={"edgecolor": "white", "linewidth": 2}). Ожидаемый вывод: 6 секторов, где «Прочее» визуально меньше остальных, но вклад виден по подписи. В комментариях объясните: как pd.concat объединяет Series и почему pd.Series({"Прочее": other}) создаёт Series с одним элементом; зачем группировать мелкие категории (читаемость — 20 мелких секторов сливаются в кашу); когда pie вообще уместна (доли целого, ≤7 категорий, положительные суммируемые данные); как autopct=lambda p: f"{p * sum / 100:.0f}" показывает абсолютные значения вместо процентов; как отсортировать категории по размеру перед pie — что важнее, размер или алфавитный порядок; почему explode=(0.05, 0, 0, ...) выделяет первый сектор.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).parent
rng = np.random.default_rng(20)

models = [f"Model {chr(65 + i)}" for i in range(20)]
w = np.array([30, 24, 18, 14, 11] + [3] * 15, dtype=float)
df = pd.DataFrame({"model": rng.choice(models, 2000, p=w / w.sum())})

# value_counts() уже сортирует по убыванию -> head(5) = топ-5 моделей.
counts = df["model"].value_counts()
top5 = counts.head(5)
other = counts.iloc[5:].sum()          # сумма всех остальных моделей

# pd.Series({"Прочее": other}) - из словаря строится Series с одним элементом
# (ключ -> индекс, значение -> данные). pd.concat склеивает Series по индексу друг
# за другом (по оси 0), сохраняя метки обеих частей.
combined = pd.concat([top5, pd.Series({"Прочее": other})])

# Зачем группировать: 20 мелких секторов по 1-3% сливаются в «кашу» подписей, глаз не
# различает малые углы. Pie уместна только для долей целого: положительные суммируемые
# значения и не более ~7 категорий. Для сравнения значений между собой лучше bar.
# Порядок: логичнее сортировать по размеру (убывание, по часовой стрелке) -
# читатель сразу видит ранг; алфавит нужен лишь для справочного поиска. «Прочее»
# по правилу ставят последним, даже если оно больше отдельных моделей.
fig, axes = plt.subplots(1, 2, figsize=(14, 7), layout="constrained")
colors = list(plt.cm.tab10.colors[:5]) + ["lightgray"]

ax = axes[0]
# explode - кортеж смещений секторов от центра, ПО ОДНОМУ значению на сектор (длина
# должна совпадать с числом секторов - 6). (0.05, 0, 0, ...) = выдвинуть только первый
# сектор (самый крупный) на 5% радиуса.
ax.pie(combined.values, labels=combined.index, autopct="%1.1f%%", colors=colors,
       explode=(0.05, 0, 0, 0, 0, 0), startangle=90, counterclock=False,
       wedgeprops={"edgecolor": "white", "linewidth": 2})
ax.set_title("Доли, %")

# autopct принимает функцию p -> строка, где p - процент. Абсолютное значение = p * total / 100.
total = combined.sum()
ax = axes[1]
ax.pie(combined.values, labels=combined.index,
       autopct=lambda p: f"{p * total / 100:.0f}", colors=colors,
       explode=(0.05, 0, 0, 0, 0, 0), startangle=90, counterclock=False,
       wedgeprops={"edgecolor": "white", "linewidth": 2})
ax.set_title("Абсолютные значения, шт.")

fig.suptitle("Продажи по моделям: топ-5 + «Прочее»")
fig.savefig(HERE / "task_20.png", dpi=150)
plt.show()
