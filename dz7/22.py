"""
Задача 22 (box plot из read_csv). Автосалон сравнивает цены по маркам (Toyota, Hyundai, Kia, Volkswagen). Постройте box plot двумя способами: через df.boxplot(column="price", by="brand", grid=False, patch_artist=True) (обёртка Pandas) и вручную через groups = [g["price"].values for _, g in df.groupby("brand")]; ax.boxplot(groups, tick_labels=names, patch_artist=True, medianprops=dict(color="red", linewidth=2)). Ожидаемый вывод: одинаковые графики двумя разными способами. В комментариях объясните: как df.boxplot(by=...) связан с Matplotlib (это просто обёртка, которая вызывает ax.boxplot под капотом); зачем grid=False; что такое notch=True (вырез для доверительного интервала медианы — если «талии» двух ящиков не пересекаются, медианы различаются статистически); почему patch_artist=True нужен для закраски ящиков и без него facecolor игнорируется; почему в новых версиях Matplotlib (3.9+) параметр labels устарел в пользу tick_labels; что произойдёт при малой выборке (5–10 значений) — box plot станет малоинформативным, лучше strip plot (ax.scatter с jitter).
"""
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).parent
CSV = HERE / "prices_by_brand.csv"
rng = np.random.default_rng(22)

if not CSV.exists():
    mu = {"Toyota": 2.4e6, "Hyundai": 2.0e6, "Kia": 1.9e6, "Volkswagen": 2.6e6}
    pd.DataFrame([(b, rng.normal(m, 3e5)) for b, m in mu.items() for _ in range(60)],
                 columns=["brand", "price"]).to_csv(CSV, index=False)
df = pd.read_csv(CSV)

# В Matplotlib 3.9 параметр labels переименован в tick_labels: у boxplot «labels»
# путали с подписями легенды, а на деле это подписи делений оси. В старых версиях
# используем labels. Определяем имя параметра по версии.
ver = tuple(int(p) for p in matplotlib.__version__.split(".")[:2])
LABELS_KW = "tick_labels" if ver >= (3, 9) else "labels"

fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True, layout="constrained")

# Способ 1: pandas. df.boxplot(by=...) - ТОНКАЯ ОБЁРТКА: делит данные по группам и вызывает
# ax.boxplot(список_массивов, ...) под капотом, затем подписывает оси названиями групп.
# grid=False убирает сетку, которую pandas включает по умолчанию (меньше визуального шума;
# стиль сетки мы настроим сами).
df.boxplot(column="price", by="brand", grid=False, patch_artist=True, ax=axes[0])
axes[0].set_title("df.boxplot(by='brand')")
axes[0].set_xlabel("")

# Способ 2: «руками» через Matplotlib
groups = [g["price"].values for _, g in df.groupby("brand")]
names = [name for name, _ in df.groupby("brand")]

# patch_artist=True: ящики рисуются как Patch (закрашиваемые многоугольники), и у них
# работает set_facecolor. Без него ящик - это набор линий (Line2D), у которых нет
# заливки: facecolor игнорируется/недоступен.
# notch=True добавлял бы «талию» - доверительный интервал медианы: если талии двух
# ящиков НЕ пересекаются по вертикали, медианы различаются (грубая визуальная проверка).
bp = axes[1].boxplot(groups, **{LABELS_KW: names}, patch_artist=True,
                     medianprops=dict(color="red", linewidth=2))
for patch, color in zip(bp["boxes"], plt.cm.Set2.colors):
    patch.set_facecolor(color)
axes[1].set_title("ax.boxplot(groups)")

for ax in axes:
    ax.set_ylabel("Цена, ₽")
fig.suptitle("Цены по маркам: два способа, один результат")
fig.savefig(HERE / "task_22.png", dpi=150)

# Малая выборка (5-10 значений): квартили, усы и выбросы по такому числу точек
# статистически шатки - «ящик» создаёт иллюзию точности. Лучше показать сами точки:
# strip plot - scatter с jitter (случайным сдвигом по X, чтобы точки не слипались).
small = df.groupby("brand").head(7)
fig2, ax = plt.subplots(figsize=(8, 5), layout="constrained")
for i, (name, g) in enumerate(small.groupby("brand"), start=1):
    jitter = rng.uniform(-0.12, 0.12, len(g))
    ax.scatter(np.full(len(g), i) + jitter, g["price"], alpha=0.8)
    ax.hlines(g["price"].median(), i - 0.25, i + 0.25, color="red")
ax.set_xticks(range(1, len(names) + 1), names)
ax.set(title="Малая выборка (n=7): strip plot вместо box plot", ylabel="Цена, ₽")
fig2.savefig(HERE / "task_22_strip.png", dpi=150)
plt.show()
