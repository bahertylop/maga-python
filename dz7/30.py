"""
Задача 30 (box plot с notch и сравнение с violinplot). Автосалон сравнивает распределение цен по типам кузова. Box plot компактен, но скрывает мультимодальность — а в SUV цена может быть бимодальной (компактные кроссоверы vs полноразмерные внедорожники). Постройте bp = ax.boxplot(groups, tick_labels=names, patch_artist=True, notch=True, showmeans=True, medianprops=dict(color="red", linewidth=2), meanprops=dict(marker="D", markerfacecolor="yellow", markeredgecolor="black", markersize=10)). Рядом постройте ax.violinplot(groups, showmedians=True, showextrema=True). Ожидаемый вывод: box plot с «талией» и жёлтыми ромбами средних рядом с violin plot, где видна бимодальность в SUV. В комментариях объясните: что показывает notch (доверительный интервал медианы — если «талии» двух ящиков не пересекаются, медианы статистически различаются); зачем showmeans, если уже есть медиана; почему violinplot информативнее box plot (видна плотность — два «горба» в SUV сразу заметны); когда box plot лучше (мало данных, много групп — компактность); как наложить точки через ax.scatter (strip plot) поверх box plot; что произойдёт при notch=True на малой выборке (Matplotlib выведет предупреждение о ненадёжности).
"""
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).parent
rng = np.random.default_rng(30)

names = ["Седан", "SUV", "Купе"]
groups = [rng.normal(2.2e6, 4e5, 300),
          np.r_[rng.normal(2.6e6, 3e5, 150), rng.normal(5.0e6, 4e5, 150)],  # бимодальный SUV
          rng.normal(4.0e6, 6e5, 80)]

ver = tuple(int(p) for p in matplotlib.__version__.split(".")[:2])
LABELS_KW = "tick_labels" if ver >= (3, 9) else "labels"

fig, axes = plt.subplots(1, 3, figsize=(17, 6), layout="constrained")

# --- Box plot ---
ax = axes[0]
# notch=True - «талия» вокруг медианы: приблизительный 95% доверительный интервал медианы
# (≈ медиана ± 1.57*IQR/√n). Если талии двух ящиков НЕ пересекаются по вертикали -
# медианы, вероятно, различаются статистически.
# showmeans=True: среднее рядом с медианой. Разница среднее-медиана показывает асимметрию
# распределения/влияние выбросов (медиана устойчива, среднее - нет).
bp = ax.boxplot(groups, **{LABELS_KW: names}, patch_artist=True, notch=True, showmeans=True,
                medianprops=dict(color="red", linewidth=2),
                meanprops=dict(marker="D", markerfacecolor="yellow",
                               markeredgecolor="black", markersize=10))
for patch, c in zip(bp["boxes"], ["C0", "C1", "C2"]):
    patch.set_facecolor(c)
    patch.set_alpha(0.6)
# Strip plot поверх: точки с jitter по X; zorder выше ящиков
for i, g in enumerate(groups, start=1):
    ax.scatter(i + rng.uniform(-0.15, 0.15, len(g)), g, s=6, alpha=0.25, color="k", zorder=3)
ax.set_title("Box plot (notch + среднее + точки)")

# --- Violin plot ---
# violinplot рисует оценку плотности (KDE) зеркально по обе стороны от оси: ширина = плотность.
# Два горба в SUV видны сразу, а в box plot они «схлопываются» в один ящик
# (квартили не показывают мультимодальность).
ax = axes[1]
ax.violinplot(groups, showmedians=True, showextrema=True)
ax.set_xticks(range(1, 4), names)
ax.set_title("Violin plot - видна бимодальность SUV")

# --- Малая выборка с notch=True ---
# При n≈6 доверительный интервал медианы огромен: «талия» выходит за пределы ящика (края
# выреза переходят за квартили - ящик выглядит «сломанным»), и Matplotlib может выдать
# предупреждение. Для малых n лучше убрать notch и показывать сами точки.
ax = axes[2]
small = [g[:6] for g in groups]
ax.boxplot(small, **{LABELS_KW: names}, notch=True, patch_artist=True)
ax.set_title("notch=True при n=6: ненадёжно")

# Когда box plot лучше violin: мало данных (KDE по 10 точкам - фикция) и много групп (10-30
# ящиков компактно сравнимы, 30 «скрипок» нечитаемы).
for a in axes:
    a.set_ylabel("Цена, ₽")
    a.grid(axis="y", alpha=0.3)
fig.savefig(HERE / "task_30.png", dpi=150)
plt.show()
