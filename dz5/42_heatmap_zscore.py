"""
Задача 42 (heatmap z-score с кастомной аннотацией).
Матрица марка × месяц, стандартизация по столбцам и отметки |z| > 2.

Объяснения:
- Z-score приводит значения к единицам стандартного отклонения от среднего;
  это позволяет сравнивать относительные отклонения, даже если масштабы брендов разные.
- RdBu_r — обратная палитра RdBu; фиксируем пределы -3..3, крайние значения насыщаются.
- bbox с фоном повышает читаемость текста поверх цветов.
- Аннотации можно ограничить сильными отклонениями и небольшими матрицами.
- Нулевая линия на colorbar отмечает нейтральный уровень.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

rng = np.random.default_rng(42)
brands = ["Toyota", "Hyundai", "Kia", "Volkswagen", "Renault"]
months = ["Янв", "Фев", "Мар", "Апр", "Май", "Июн", "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"]
data = rng.poisson(lam=np.array([220, 160, 90, 130, 70])[:, None] *
                  (1 + 0.15*np.sin(np.arange(12)[None, :])), size=(5, 12))
df = pd.DataFrame(data, index=brands, columns=months)

# Стандартизация по столбцам (в каждом месяце сравниваем марки относительно месячного среднего).
z = (df - df.mean(axis=0)) / df.std(axis=0).replace(0, np.nan)
z = z.fillna(0)

fig, ax = plt.subplots(figsize=(12, 5.5), layout="constrained")
im = ax.imshow(z, cmap="RdBu_r", vmin=-3, vmax=3, aspect="auto")
ax.set_xticks(range(len(months)), labels=months)
ax.set_yticks(range(len(brands)), labels=brands)
ax.set_title("Продажи: z-score по месяцам")
cbar = fig.colorbar(im, ax=ax)
cbar.ax.axhline(0, color="black", linewidth=1)
if abs(z.values).max() > 2 and z.shape[0]*z.shape[1] < 100:
    for i, j in np.ndindex(z.shape):
        if abs(z.iloc[i, j]) > 2:
            ax.text(j, i, f"{z.iloc[i, j]:.1f}", color="white", fontsize=8,
                    bbox=dict(boxstyle="round,pad=0.2", facecolor="black", alpha=0.5))
plt.show()
