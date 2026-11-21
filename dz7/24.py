"""
Задача 24 (GridSpec и subplot_mosaic). Автосалон строит дашборд с большим графиком динамики продаж сверху и двумя меньшими снизу (топ моделей и марки). Реализуйте двумя способами: через gs = fig.add_gridspec(2, 2, height_ratios=[2, 1], width_ratios=[3, 1]) с ax1 = fig.add_subplot(gs[0, :]), ax2 = fig.add_subplot(gs[1, 0]), ax3 = fig.add_subplot(gs[1, 1]); и через fig, axes = plt.subplot_mosaic("AAA;BC", figsize=(12, 8), layout="constrained") с обращением axes["A"], axes["B"], axes["C"]. Ожидаемый вывод: верхний график во всю ширину в 2× выше нижних. В комментариях объясните: как gs[0, :] означает «вся первая строка» (срез по NumPy), а gs[1, 0] — конкретная ячейка; зачем height_ratios=[2, 1] и width_ratios=[3, 1]; почему subplot_mosaic читается лучше для сложных сеток («AAA;BC» — почти как ASCII-арт); как GridSpecFromSubplotSpec создаёт вложенные сетки; что произойдёт при пересечении областей (например, gs[0, :2] и gs[0, 1:] — наложение, Matplotlib выдаст предупреждение); как сохранить layout="constrained" с GridSpec (передать в figure(layout="constrained")).
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpecFromSubplotSpec

HERE = Path(__file__).parent
rng = np.random.default_rng(24)
days = np.arange(1, 61)
sales = 45 + 8 * np.sin(days / 6) + rng.normal(0, 3, 60)
models = ["A", "B", "C", "D"]
top = [120, 95, 80, 60]
brands = ["Toyota", "Kia"]
bs = [310, 260]


def draw(ax1, ax2, ax3):
    ax1.plot(days, sales)
    ax1.set_title("Динамика продаж")
    ax2.bar(models, top)
    ax2.set_title("Топ моделей")
    ax3.bar(brands, bs, color="C2")
    ax3.set_title("Марки")


# Способ 1: GridSpec. layout="constrained" передаём в plt.figure(): GridSpec сам по себе
# не управляет отступами, а менеджер раскладки живёт у Figure.
fig = plt.figure(figsize=(12, 8), layout="constrained")

# Сетка 2x2: height_ratios=[2, 1] - верхняя строка в 2 раза выше нижней;
# width_ratios=[3, 1] - левый столбец в 3 раза шире правого.
gs = fig.add_gridspec(2, 2, height_ratios=[2, 1], width_ratios=[3, 1])

# gs поддерживает индексацию как массив NumPy: gs[0, :] - срез «строка 0, все столбцы»
# (объединяет обе ячейки верхней строки в одну широкую область); gs[1, 0] - одна ячейка.
ax1 = fig.add_subplot(gs[0, :])
ax2 = fig.add_subplot(gs[1, 0])
ax3 = fig.add_subplot(gs[1, 1])
draw(ax1, ax2, ax3)
fig.suptitle("GridSpec")
fig.savefig(HERE / "task_24_gridspec.png", dpi=150)

# Способ 2: subplot_mosaic. Раскладка задаётся «ASCII-артом»: строки через ';', одинаковая
# буква = одна ось, занимающая все помеченные ячейки.
# Внимание: все строки мозаики должны иметь ОДИНАКОВУЮ длину. Строка "AAA;BC" (3 и 2 символа)
# вызовет ValueError, поэтому берём "AAAA;BBBC": 4 столбца, A на всю ширину, B на 3
# столбца, C на 1 -> то же соотношение 3:1, что и width_ratios=[3, 1].
fig2, axes = plt.subplot_mosaic("AAAA;BBBC", figsize=(12, 8), layout="constrained",
                                gridspec_kw={"height_ratios": [2, 1]})
draw(axes["A"], axes["B"], axes["C"])      # доступ по именам, а не по [i, j]
fig2.suptitle("subplot_mosaic")
fig2.savefig(HERE / "task_24_mosaic.png", dpi=150)

# Вложенные сетки: GridSpecFromSubplotSpec делит ОДНУ ячейку внешней сетки на свою
# подсетку со своими отступами и пропорциями.
fig3 = plt.figure(figsize=(12, 6), layout="constrained")
outer = fig3.add_gridspec(1, 2, width_ratios=[2, 1])
inner = GridSpecFromSubplotSpec(2, 1, subplot_spec=outer[1], height_ratios=[1, 1])
big = fig3.add_subplot(outer[0])
big.plot(days, sales)
big.set_title("Основной график")
for k, (name, data) in enumerate([("Топ моделей", top), ("Марки", bs * 2)]):
    a = fig3.add_subplot(inner[k])
    a.bar(range(len(data)), data)
    a.set_title(name)
fig3.savefig(HERE / "task_24_nested.png", dpi=150)

# Пересечение областей (gs[0, :2] и gs[0, 1:] на сетке 1x3): Matplotlib НЕ запрещает это -
# обе оси создаются и просто накладываются друг на друга (перекрытие по столбцу 1),
# график становится нечитаемым; иногда constrained layout выдаёт предупреждение
# о невозможности подобрать раскладку. Следите, чтобы срезы не пересекались.
plt.show()
