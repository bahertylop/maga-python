"""
Задача 15 (группированные столбцы из pivot_table). Автосалон сравнивает продажи по маркам за 2023 и 2024 год. Постройте pivot = sales.pivot_table(index="brand", columns="year", values="count", aggfunc="sum"), получите x = np.arange(len(pivot.index)) и width = 0.8 / len(pivot.columns). Через цикл for i, year in enumerate(pivot.columns): offset = (i - len(pivot.columns) / 2 + 0.5) * width; ax.bar(x + offset, pivot[year], width, label=str(year)) постройте сгруппированные столбцы. Установите ax.set_xticks(x) и ax.set_xticklabels(pivot.index). Ожидаемый вывод: парные столбцы (2023 и 2024) для каждой марки. В комментариях объясните: почему width = 0.8 / n_years, а не фиксированный 0.35 (иначе столбцы перекроются при 3+ группах); как формула (i - n/2 + 0.5) * width обобщается на любое число групп; как pivot_table сразу готовит данные — что было бы, если бы данных не было в правильной форме; зачем set_xticks и set_xticklabels по отдельности; что произойдёт при width=0.8 с двумя группами (полностью перекроются); как добавить третью группу (например, прогноз на 2025) и почему это работает без изменений в коде.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).parent
rng = np.random.default_rng(3)

# «Длинная» таблица: одна строка = (марка, год, месяц, число продаж)
brands = ["Toyota", "Hyundai", "Kia", "Volkswagen", "Skoda"]
rows = [(b, y, m, int(rng.integers(20, 60) * (1.1 if y == 2024 else 1.0)))
        for b in brands for y in (2023, 2024) for m in range(1, 13)]
sales = pd.DataFrame(rows, columns=["brand", "year", "month", "count"])

# pivot_table превращает «длинные» данные в «широкие»: строки = марки, столбцы = годы,
# значения = сумма. Один столбец pivot[year] = один набор столбцов на графике.
# Без такой формы пришлось бы вручную фильтровать sales по каждому году, выравнивать марки
# по порядку (риск, что у одного года нет какой-то марки -> смещение столбцов) и
# суммировать циклами. pivot_table выравнивает индекс и заполняет пропуски (fill_value).
pivot = sales.pivot_table(index="brand", columns="year", values="count", aggfunc="sum")


def grouped_bars(ax, pivot):
    x = np.arange(len(pivot.index))          # центры групп: 0, 1, 2, ...
    # Группа занимает 0.8 единицы по оси X (остаётся 0.2 зазора между группами).
    # width = 0.8 / n делит эту ширину на n столбцов - любое число групп помещается.
    # Фиксированные 0.35 годятся только для 2 групп: при 3 столбцах суммарная ширина
    # 1.05 > 1 -> соседние группы налезают друг на друга.
    n = len(pivot.columns)
    width = 0.8 / n
    for i, year in enumerate(pivot.columns):
        # Формула: смещение центра i-го столбца относительно центра группы.
        # (i - n/2 + 0.5) * width: для n=2 -> -0.5w и +0.5w, для n=3 -> -w, 0, +w,
        # для n=4 -> -1.5w, -0.5w, 0.5w, 1.5w. Т.е. набор симметричен вокруг нуля
        # при любом n.
        offset = (i - n / 2 + 0.5) * width
        ax.bar(x + offset, pivot[year], width, label=str(year))
    # set_xticks - ГДЕ ставить деления (числовые позиции центров групп), set_xticklabels -
    # ЧТО на них писать. Ось X у bar с числовыми x - числовая, подписи марок
    # нужно назначать отдельно. (Всегда сначала set_xticks, иначе предупреждение
    # FixedFormatter without FixedLocator.)
    ax.set_xticks(x)
    ax.set_xticklabels(pivot.index)
    ax.legend(title="Год")
    ax.grid(axis="y", alpha=0.3)


fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 5), layout="constrained")
grouped_bars(ax1, pivot)
ax1.set(title="2023 vs 2024", ylabel="Продано, шт.")

# Третья группа: прогноз на 2025. Функция та же, без изменений: n = len(pivot.columns)
# растёт до 3, и width / offset пересчитываются автоматически.
pivot3 = pivot.copy()
pivot3[2025] = (pivot[2024] * 1.08).round()
grouped_bars(ax2, pivot3)
ax2.set(title="+ прогноз 2025 (код не менялся)")

# Антипример: width=0.8 для КАЖДОГО из двух столбцов с offset = ±0.4*... -> столбцы по
# 0.8 шириной со сдвигом всего 0.8 (при offset=±0.4) почти полностью перекрывают друг друга.
x = np.arange(len(pivot.index))
for i, year in enumerate(pivot.columns):
    ax3.bar(x + (i - 1 + 0.5) * 0.1, pivot[year], 0.8, alpha=0.6, label=str(year))
ax3.set_xticks(x, pivot.index)
ax3.set_title("Ошибка: width=0.8 для двух групп")
ax3.legend()

fig.savefig(HERE / "task_15.png", dpi=150)
plt.show()
