"""
Задача 18 (density, cumulative, step). Автосалон сравнивает распределения цен по трём типам кузова (седан, SUV, купе). Если построить обычные гистограммы, купе (мало продаж) будет визуально «раздавлено» седаном (много продаж). Постройте 4 подграфика: (а) наложение с alpha=0.5; (б) density=True (нормировка площади к 1); (в) cumulative=True (накопленная частота); (г) histtype="step" (только контуры). Для каждого for body, g in df.groupby("body_type"): ax.hist(g["price"], ...). В комментариях объясните: зачем density=True при разном n; как cumulative=True находит медиану (точка, где накопленная частота = 0.5) и как её отметить через ax.axvline(median_value); почему histtype="step" лучше при 3+ сериях; как зафиксировать bins при сравнении (bins=np.linspace(min, max, 21)) — что будет при автоматическом подборе корзин для каждой группы отдельно; как наложить KDE через scipy.stats.gaussian_kde; что произойдёт при cumulative=-1 (обратная накопленная — от 1 к 0, полезно для «доли автомобилей дороже X»).
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde

HERE = Path(__file__).parent
rng = np.random.default_rng(11)

df = pd.concat([
    pd.DataFrame({"body_type": "Седан", "price": rng.normal(2.2e6, 4e5, 800)}),
    pd.DataFrame({"body_type": "SUV", "price": np.r_[rng.normal(2.6e6, 3e5, 200),   # компактные
                                                      rng.normal(5.0e6, 5e5, 200)]}),  # полноразмерные -> бимодальность
    pd.DataFrame({"body_type": "Купе", "price": rng.normal(4.0e6, 6e5, 80)}),
], ignore_index=True)

# Общие корзины для всех групп. Если дать bins=20 каждой группе отдельно, у каждой будут
# СВОИ границы и ширина корзин (по диапазону группы) -> столбцы несопоставимы по ширине
# и положению, сравнение формы распределений теряет смысл.
bins = np.linspace(df["price"].min(), df["price"].max(), 21)
colors = {"Седан": "C0", "SUV": "C1", "Купе": "C2"}

fig, axes = plt.subplots(2, 2, figsize=(14, 9), layout="constrained")
ax_a, ax_b, ax_c, ax_d = axes.ravel()

for body, g in df.groupby("body_type"):
    c = colors[body]
    # (а) наложение: купе (80 шт.) почти не видно рядом с седаном (800 шт.)
    ax_a.hist(g["price"], bins=bins, alpha=0.5, color=c, label=f"{body} (n={len(g)})")

    # (б) density=True: высота столбца = доля/ширина корзины, ПЛОЩАДЬ гистограммы = 1.
    # Группы с разным n становятся сопоставимыми: сравниваем ФОРМУ, а не объём продаж.
    ax_b.hist(g["price"], bins=bins, alpha=0.5, density=True, color=c, label=body)
    # KDE: сглаженная оценка плотности (ядро - гауссово); масштаб совпадает с density=True.
    xs = np.linspace(bins[0], bins[-1], 300)
    ax_b.plot(xs, gaussian_kde(g["price"])(xs), color=c, lw=2)

    # (в) cumulative=True + density=True: накопленная доля от 0 до 1 (ECDF-подобная кривая).
    # Медиана - точка, где накопленная частота достигает 0.5. Находим её как
    # np.median, а на графике отмечаем вертикалью axvline в этой точке.
    ax_c.hist(g["price"], bins=bins, cumulative=True, density=True, histtype="step",
              color=c, lw=2, label=body)
    med = np.median(g["price"])
    ax_c.axvline(med, color=c, ls=":", lw=1.5)

    # (г) histtype="step" - только контур без заливки: при 3+ сериях заливки
    # перекрываются и смешиваются в грязные цвета, а контуры остаются читаемыми.
    ax_d.hist(g["price"], bins=bins, histtype="step", lw=2, density=True, color=c, label=body)

ax_c.axhline(0.5, color="gray", ls="--", lw=1)
ax_a.set_title("(а) Наложение, alpha=0.5 - купе «раздавлено»")
ax_b.set_title("(б) density=True + KDE")
ax_c.set_title("(в) cumulative=True, пунктир - медианы")
ax_d.set_title('(г) histtype="step"')
for ax in axes.ravel():
    ax.legend()
    ax.grid(alpha=0.3)
    ax.set_xlabel("Цена, ₽")
fig.savefig(HERE / "task_18.png", dpi=150)

# cumulative=-1: «обратная» накопленная - от 1 до 0 (доля значений >= x).
# Читается как «какая доля автомобилей дороже X ₽?».
fig2, ax = plt.subplots(figsize=(8, 5), layout="constrained")
for body, g in df.groupby("body_type"):
    ax.hist(g["price"], bins=bins, cumulative=-1, density=True, histtype="step",
            lw=2, color=colors[body], label=body)
ax.set(title="cumulative=-1: доля автомобилей дороже X", xlabel="Цена, ₽", ylabel="Доля")
ax.legend()
ax.grid(alpha=0.3)
fig2.savefig(HERE / "task_18_reverse_cumulative.png", dpi=150)
plt.show()
