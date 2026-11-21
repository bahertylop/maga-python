"""
Задача 16 (stacked bar + errorbar). Автосалон показывает структуру продаж по каналам (салон, онлайн, партнёры) для каждой марки. Постройте pivot = sales.pivot_table(index="brand", columns="channel", values="count", aggfunc="sum"), реализуйте накопление через bottom = np.zeros(len(pivot)); for ch in pivot.columns: ax.bar(pivot.index, pivot[ch], bottom=bottom, label=ch); bottom += pivot[ch].values. Добавьте планки ошибок к сумме через ax.errorbar(pivot.index, bottom, yerr=stds.values, fmt="none", capsize=8, ecolor="black"). Ожидаемый вывод: накопленные столбцы с планками ошибок наверху каждого. В комментариях объясните: как bottom=bottom реализует накопление и почему bottom += pivot[ch].values (а не bottom = pivot[ch]) — что будет, если забыть +=; почему yerr нужен для суммы, а не для отдельного канала (планка «утонет» внутри столбца и будет вводить в заблуждение); зачем fmt="none" (только планки, без маркеров); как error_kw={"elinewidth": 2, "ecolor": "black"} объединяет стиль; что произойдёт при неправильном порядке категорий в bottom и yerr (планки окажутся не на тех столбцах); как вычислить стандартное отклонение по маркам (sales.groupby("brand")["count"].std()).
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).parent
rng = np.random.default_rng(5)

brands = ["Toyota", "Hyundai", "Kia", "Volkswagen", "Skoda"]
channels = ["Салон", "Онлайн", "Партнёры"]
share = {"Салон": 1.0, "Онлайн": 0.6, "Партнёры": 0.4}
rows = [(b, ch, q, int(rng.normal(900 * share[ch] * (1 + 0.1 * i), 250)))
        for i, b in enumerate(brands) for ch in channels for q in range(8)]
sales = pd.DataFrame(rows, columns=["brand", "channel", "quarter", "count"])

pivot = sales.pivot_table(index="brand", columns="channel", values="count", aggfunc="sum")
pivot = pivot[channels]  # фиксируем порядок каналов

# Стандартное отклонение по маркам. ВАЖНО: порядок индекса должен совпадать с pivot!
# groupby сортирует марки по алфавиту, как и pivot_table, но надёжнее сделать reindex.
stds = sales.groupby("brand")["count"].std().reindex(pivot.index)

fig, axes = plt.subplots(1, 2, figsize=(14, 6), layout="constrained")
ax = axes[0]

# bottom - массив «нижних границ» для текущего слоя. Первый слой стартует с нуля.
# После каждого слоя bottom увеличивается на его значения, и следующий слой
# рисуется поверх предыдущего.
# `bottom += pivot[ch].values` - накопление (in-place, по числам). Если забыть += (или
# записать bottom = pivot[ch]), то все слои стартуют с нуля / с высоты только предыдущего
# канала -> столбцы наложатся друг на друга, а не сложатся. Также `.values` важен: float-массив
# NumPy складывается поэлементно без выравнивания индексов Pandas (а bottom - ndarray).
bottom = np.zeros(len(pivot))
for ch in pivot.columns:
    ax.bar(pivot.index, pivot[ch], bottom=bottom, label=ch)
    bottom += pivot[ch].values

# Планки ошибок относятся к ИТОГУ (bottom теперь = сумма всех каналов), т.е. к вершине
# столбца. Если рисовать yerr для отдельного канала, планка окажется внутри столбца
# и будет выглядеть как погрешность общего итога - ввод в заблуждение.
# fmt="none" - не рисовать маркер/линию соединения, только сами планки.
# Порядок bottom и stds.values ОБЯЗАН совпадать с порядком pivot.index: иначе планка
# одной марки окажется на столбце другой.
ax.errorbar(pivot.index, bottom, yerr=stds.values, fmt="none", capsize=8, ecolor="black")
ax.set(title="Структура продаж по каналам (планки: SD по маркам)", ylabel="Продано, шт.")
ax.legend()

# Вариант с error_kw - то же стиль через параметр bar (для планок самого слоя).
# error_kw={"elinewidth": 2, "ecolor": "black"} собирает стиль планок в одном словаре.
# Здесь - простой bar с yerr, показывающий этот способ.
ax2 = axes[1]
ax2.bar(pivot.index, bottom, yerr=stds.values, capsize=8,
        error_kw={"elinewidth": 2, "ecolor": "black"}, color="lightsteelblue")
ax2.set(title="Итог по маркам: bar(yerr=..., error_kw=...)")

for a in axes:
    a.grid(axis="y", alpha=0.3)
fig.savefig(HERE / "task_16.png", dpi=150)
plt.show()
