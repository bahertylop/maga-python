"""Задача 4. Стиль линий как dataclass, пять линий на пяти Axes."""
from dataclasses import dataclass
import matplotlib.pyplot as plt
@dataclass
class LineStyle:
    color: str = "steelblue"
    linewidth: float = 2
    marker: str = "o"
    markersize: int = 8
    alpha: float = 1
    def as_kwargs(self) -> dict:
        return vars(self).copy()
months = range(1, 7)
series = [[12, 15, 11, 18, 17, 20], [9, 13, 14, 15, 16, 18],
          [8, 10, 12, 13, 15, 17], [7, 9, 11, 12, 13, 15], [6, 8, 9, 11, 12, 14]]
styles = [LineStyle("steelblue", marker="o"), LineStyle("darkorange", marker="s"),
          LineStyle("seagreen", marker="^"), LineStyle("purple", marker="D", alpha=.7),
          LineStyle("#cc3344", marker="x", linewidth=3)]
fig, axes = plt.subplots(5, 1, figsize=(9, 12), layout="constrained")
for ax, y, style in zip(axes, series, styles):
    ax.plot(months, y, **style.as_kwargs())
    ax.grid(alpha=.25)
# Строка формата plot: [marker][line][color], например 'ob-' = круги, сплошная линия, blue.
# Эквивалент: ax.plot(x, y, 'ob-') и ax.plot(x, y, color='b', marker='o', linestyle='-').
# markerfacecolor задаёт заливку маркера, markeredgecolor — обводку; контраст помогает различать.
# alpha<1 делает наложения прозрачнее; alpha=0 полностью невидима (может быть условно скрытой).
# linewidth в points: 1 point = 1/72 inch; DPI влияет на число пикселей, не на физическую толщину.
# Цвет задаётся именем, HEX ('#cc3344') или RGB-кортежем, например (0.8, 0.2, 0.1).
axes[0].plot(months, series[0], "ob-", label="format string")
axes[0].plot(months, series[0], color="b", marker="o", linestyle="-", label="kwargs")
axes[0].legend()
plt.show()
