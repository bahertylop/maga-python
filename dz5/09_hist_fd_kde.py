"""Задача 9. Гистограммы с FD bins и KDE."""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.stats import gaussian_kde

def fd_bins(x: pd.Series) -> int:
    clean = x.dropna()
    if len(clean) < 2: return 1
    q25, q75 = np.percentile(clean, [25, 75])
    iqr = q75 - q25
    width = 2 * iqr / len(clean) ** (1/3)
    # Защита от нулевого IQR (все или почти все значения одинаковы).
    if width <= 0: return max(1, int(np.sqrt(len(clean))))
    return max(1, int((clean.max() - clean.min()) / width))
if Path("sales.csv").exists():
    df = pd.read_csv("sales.csv")
    prices = df["price"].dropna()
else:
    prices = pd.Series(np.random.default_rng(42).normal(2_000_000, 350_000, 500).clip(500_000, 4_000_000))
fig, axes = plt.subplots(2, 2, figsize=(10, 8), layout="constrained")
for ax, bins, title in zip(axes.flat, [fd_bins(prices), 10, 30, "auto"], ["FD", "10 bins", "30 bins", "auto"]):
    ax.hist(prices, bins=bins, edgecolor="white")
    ax.set_title(title)
# FD использует IQR, устойчивее к выбросам, чем правило со стандартным отклонением.
# Мало корзин скрывает локальные пики; слишком много делает случайные колебания заметными.
# density=True нормирует площадь, удобно сравнивать выборки разного объёма (седаны/купе).
# hist — распределение числовой непрерывной переменной, bar — категориальные агрегаты.
# bins=1000 для 500 наблюдений оставит много пустых bins и будет плохо читаться.
# KDE — сглаженная оценка плотности; ниже демонстрация на отдельном графике.
fig2, ax = plt.subplots(layout="constrained")
ax.hist(prices, bins=fd_bins(prices), density=True, alpha=.35, label="Histogram")
x = np.linspace(prices.min(), prices.max(), 300)
ax.plot(x, gaussian_kde(prices)(x), label="KDE")
ax.legend(); ax.set_title("Распределение цен и KDE")
plt.show()
