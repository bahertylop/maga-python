"""
Задача 29 (heatmap корреляций). Автосалон изучает, какие признаки сильнее всего коррелируют с ценой автомобиля (мощность, пробег, год выпуска, объём двигателя, расход топлива). Постройте corr = df.select_dtypes("number").corr(method="spearman") (ранговая корреляция устойчива к выбросам), затем im = ax.imshow(corr, cmap="RdBu", vmin=-1, vmax=1) с fig.colorbar(im, label="Spearman ρ"). Скройте верхнюю половину через маску mask = np.triu(np.ones_like(corr, dtype=bool), k=1); corr_masked = corr.mask(mask). Аннотируйте значения через for i, j in zip(*np.where(~mask)): ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center"). Ожидаемый вывод: матрица 5×5 с диагональю 1.0 и цветовой шкалой. В комментариях объясните: почему vmin=-1, vmax=1 фиксирует диапазон (нуль всегда белый, иначе цвет «плавает» в зависимости от данных); зачем diverging-палитра RdBu для корреляций; как select_dtypes("number") защищает от ошибок (строковые столбцы типа «марка» не коррелируют); почему method="spearman" предпочтительнее pearson для реальных бизнес-данных; как np.where(~mask) даёт координаты только нижнего треугольника; как отсортировать признаки по корреляции с целевой (corr.abs().sort_values(by="price", ascending=False)) для приоритизации.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).parent
rng = np.random.default_rng(29)
n = 300
year = rng.integers(2008, 2024, n)
mileage = (2024 - year) * rng.uniform(8_000, 20_000, n)
power = rng.normal(150, 40, n).clip(70)
engine = (power / 75 + rng.normal(0, 0.3, n)).clip(1.0)
consumption = 4 + engine * 1.5 + rng.normal(0, 0.5, n)
price = 600_000 + (year - 2008) * 90_000 + power * 6_000 - mileage * 2 + rng.normal(0, 150_000, n)
df = pd.DataFrame({"brand": rng.choice(["Toyota", "Kia", "VW"], n), "price": price,
                   "power": power, "mileage": mileage, "year": year,
                   "engine": engine, "consumption": consumption})

# select_dtypes("number") оставляет только числовые столбцы: текстовая колонка brand
# не имеет коэффициента корреляции и вызвала бы ошибку (или предупреждение) в corr().
# Spearman - корреляция рангов: устойчива к выбросам и ловит любую монотонную связь,
# а у бизнес-данных (цены, пробеги) почти всегда есть «хвосты» и выбросы; Pearson же
# требует линейности и чувствителен к выбросам.
corr = df.select_dtypes("number").corr(method="spearman")

# Маска верхнего треугольника (k=1: диагональ остаётся). Верх симметричен низу, поэтому
# показывать его - лишний шум.
mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
corr_masked = corr.mask(mask)          # True в маске -> NaN (клетка остаётся пустой)

fig, ax = plt.subplots(figsize=(9, 8), layout="constrained")
# vmin=-1, vmax=1 фиксируют диапазон цвета: 0 всегда в середине шкалы (белый), +1 - тёмно-
# красный/синий... Без фиксации Matplotlib возьмёт min/max данных, и цвет станет
# «плавать»: одна и та же корреляция выглядела бы по-разному на разных наборах данных.
# RdBu - divergent-палитра: корреляции симметричны вокруг нуля (знак важен),
# поэтому нейтральный центр и два контрастных цвета для + и -.
im = ax.imshow(corr_masked.values, cmap="RdBu", vmin=-1, vmax=1)
fig.colorbar(im, label="Spearman ρ")

ax.set_xticks(range(len(corr)), corr.columns, rotation=45, ha="right")
ax.set_yticks(range(len(corr)), corr.index)

# np.where(~mask) - индексы (строки, столбцы) всех True в ~mask, т.е. клетки нижнего
# треугольника с диагональю. zip(*...) превращает два массива в пары (i, j).
for i, j in zip(*np.where(~mask)):
    ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center",
            color="white" if abs(corr.iloc[i, j]) > 0.6 else "black")

ax.set_title("Корреляции Спирмена")
fig.savefig(HERE / "task_29.png", dpi=150)

# Приоритизация признаков: по модулю корреляции с целевой переменной (price)
print(corr["price"].drop("price").abs().sort_values(ascending=False))
plt.show()
