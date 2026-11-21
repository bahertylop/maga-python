"""
Задача 50 (Seaborn: распределения — histplot, kdeplot, displot, ecdfplot). Автосалон исследует распределение цен по типам кузова (седан, SUV, купе). Seaborn даёт четыре инструмента: histplot (гистограмма с KDE), kdeplot (сглаженная плотность), displot (figure-level сетка), ecdfplot (накопленная CDF). Постройте 4 подграфика: histplot(kde=True), kdeplot(fill=True, common_norm=False), displot(col="body_type", kind="kde"), ecdfplot(hue="body_type"). Ожидаемый вывод: 4 вида визуализации распределений. В комментариях объясните: что делает kde (Kernel Density Estimation — сглаженная оценка плотности); зачем fill=True (заливка под кривой — читается лучше); чем displot отличается от histplot (figure-level создаёт сетку автоматически); что такое ecdf (эмпирическая CDF — «доля автомобилей дешевле X»); что делает common_norm=False (доли внутри групп, а не по всей выборке); что произойдёт при hue с 10+ категориями (все кривые перекроются — используйте displot(col=...) вместо kdeplot(hue=...)).
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

HERE = Path(__file__).parent
rng = np.random.default_rng(50)
df = pd.concat([
    pd.DataFrame({"body_type": "Седан", "price": rng.normal(2.2e6, 4e5, 800)}),
    pd.DataFrame({"body_type": "SUV", "price": np.r_[rng.normal(2.6e6, 3e5, 200), rng.normal(5.0e6, 5e5, 200)]}),
    pd.DataFrame({"body_type": "Купе", "price": rng.normal(4.0e6, 6e5, 80)}),
], ignore_index=True)
sns.set_theme(style="whitegrid")

fig, axes = plt.subplots(1, 3, figsize=(18, 5), layout="constrained")

# (1) histplot(kde=True): гистограмма + кривая KDE. KDE (Kernel Density Estimation) -
# сглаженная оценка плотности: в каждую точку «ставится» колокол-ядро, ядра суммируются.
sns.histplot(data=df, x="price", hue="body_type", kde=True, ax=axes[0])
axes[0].set_title("histplot(kde=True)")

# (2) kdeplot: fill=True заливает область под кривой - перекрытия видны лучше, чем у
# одних контуров. common_norm=False нормирует ПЛОЩАДЬ каждой группы отдельно (каждая = 1):
# сравниваем ФОРМУ. При common_norm=True (по умолчанию) площадь делится между группами
# пропорционально их размеру -> купе (80 шт.) станет почти плоской.
sns.kdeplot(data=df, x="price", hue="body_type", fill=True, common_norm=False, alpha=0.4, ax=axes[1])
axes[1].set_title("kdeplot(fill, common_norm=False)")

# (3) ecdfplot: эмпирическая CDF - «доля автомобилей, которые дешевле X». Читается без
# выбора корзин/ширины ядра, медиана - где кривая пересекает 0.5.
sns.ecdfplot(data=df, x="price", hue="body_type", ax=axes[2])
axes[2].axhline(0.5, color="gray", ls="--")
axes[2].set_title("ecdfplot")
fig.savefig(HERE / "50_axes_level.png", dpi=150)

# (4) displot - FIGURE-level: сам создаёт Figure/FacetGrid, поэтому НЕ принимает ax= и
# его нельзя «вставить» в чужую сетку подграфиков. Поэтому 4-й вид сохраняем отдельной
# фигурой: col="body_type" - одна ячейка на тип кузова. Это же лучше, чем kdeplot(hue=...),
# когда категорий 10+: кривые одной оси слипаются в клубок, а отдельные панели читаются.
g = sns.displot(data=df, x="price", col="body_type", kind="kde", fill=True, height=4, aspect=1)
g.set_titles("{col_name}")
g.savefig(HERE / "50_displot.png", dpi=150, bbox_inches="tight")
print("ok")
