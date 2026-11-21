"""
Задача 17 (scatter + polyfit + выбросы по z-score). Автосалон исследует связь пробега и цены автомобиля с пробегом — но в данных есть «коллекционные» экземпляры с аномально высокой ценой при большом пробеге. Постройте облако точек через ax.scatter(df["mileage"], df["price"], alpha=0.6), вычислите m, b = np.polyfit(df["mileage"], df["price"], 1) и нарисуйте тренд ax.plot(x_line, m * x_line + b, "r--"). Выбросы определите по z = np.abs((df["price"] - df["price"].mean()) / df["price"].std()); mask = z > 3 и выделите отдельным ax.scatter(df.loc[mask, "mileage"], df.loc[mask, "price"], c="red", marker="X", s=200, edgecolors="black", label="Выбросы", zorder=5). Добавьте в заголовок r = np.corrcoef(df["mileage"], df["price"])[0, 1]. В комментариях объясните: что означает m в polyfit (наклон — сколько рублей цены теряется на каждый километр пробега); почему polyfit чувствителен к выбросам и как RANSACRegressor из sklearn.linear_model решает проблему; как zorder держит выбросы поверх точек; что произойдёт при нелинейной зависимости (например, квадратичное падение цены) — линейный тренд введёт в заблуждение и нужен polyfit(deg=2); как np.corrcoef[0, 1] извлекает коэффициент корреляции Пирсона из матрицы; почему коэффициент Пирсона чувствителен к выбросам, а Спирмен (scipy.stats.spearmanr) — нет.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).parent
rng = np.random.default_rng(7)

n = 200
mileage = rng.uniform(5_000, 300_000, n)
price = 2_000_000 - 4.5 * mileage + rng.normal(0, 120_000, n)
# «Коллекционные» экземпляры: большой пробег и очень высокая цена
idx = rng.choice(n, 6, replace=False)
mileage[idx] = rng.uniform(150_000, 250_000, 6)
price[idx] = rng.uniform(3_200_000, 3_800_000, 6)
df = pd.DataFrame({"mileage": mileage, "price": price})

# m, b = polyfit(..., 1): y = m*x + b. m - наклон: на сколько рублей меняется цена
# при росте пробега на 1 км (у нас m < 0: каждый км «стоит» примерно -4.5 ₽).
m, b = np.polyfit(df["mileage"], df["price"], 1)
x_line = np.linspace(df["mileage"].min(), df["mileage"].max(), 100)

# z-score: на сколько стандартных отклонений значение отстоит от среднего.
z = np.abs((df["price"] - df["price"].mean()) / df["price"].std())
mask = z > 3

# np.corrcoef(x, y) возвращает матрицу 2x2 [[1, r], [r, 1]]; элемент [0, 1] - r Пирсона.
r = np.corrcoef(df["mileage"], df["price"])[0, 1]
rho = spearmanr(df["mileage"], df["price"])[0]

fig, axes = plt.subplots(1, 2, figsize=(15, 6), layout="constrained")
ax = axes[0]
ax.scatter(df["mileage"], df["price"], alpha=0.6, label="Автомобили")
ax.plot(x_line, m * x_line + b, "r--", label=f"OLS: {m:,.2f} ₽/км")

# zorder задаёт порядок отрисовки: больше zorder -> рисуется позже -> поверх. По
# умолчанию scatter имеет zorder=1, линии - 2; zorder=5 гарантирует, что выбросы
# окажутся поверх всех точек и линии тренда.
ax.scatter(df.loc[mask, "mileage"], df.loc[mask, "price"], c="red", marker="X", s=200,
           edgecolors="black", label="Выбросы", zorder=5)

# Чувствительность polyfit: МНК минимизирует сумму КВАДРАТОВ ошибок, поэтому далёкие
# точки получают огромный вес и «тянут» линию на себя. Решение - RANSAC: многократно
# подгоняет модель по случайным подвыборкам, выбирает ту, под которую подходит больше
# всего точек (inliers), и игнорирует выбросы.
try:
    from sklearn.linear_model import RANSACRegressor
    ransac = RANSACRegressor(random_state=42).fit(df[["mileage"]].values, df["price"].values)
    ax.plot(x_line, ransac.predict(x_line.reshape(-1, 1)), "g-", lw=2, label="RANSAC")
except ImportError:
    print("sklearn не установлен - RANSAC пропущен")

# Pearson r - линейная связь по ВЕЛИЧИНАМ, поэтому чувствителен к выбросам (они меняют и
# среднее, и ковариацию). Spearman - корреляция по РАНГАМ (порядку), значение выброса
# не важно, важно лишь его место в порядке -> устойчив к выбросам и к любой монотонной
# нелинейности.
ax.set(title=f"Пробег vs цена: Pearson r={r:.2f}, Spearman ρ={rho:.2f}",
       xlabel="Пробег, км", ylabel="Цена, ₽")
ax.legend()
ax.grid(alpha=0.3)

# --- Нелинейная зависимость: квадратичное падение цены ---
# Линейный тренд («прямая») не отражает изгиб и систематически ошибается (занижает в
# середине и завышает по краям), поэтому вывод «каждый км = -X ₽» вводит в заблуждение.
# Нужна polyfit(deg=2) (или другая модель).
x2 = rng.uniform(0, 300_000, 150)
y2 = 2_000_000 * np.exp(-x2 / 120_000) + rng.normal(0, 60_000, 150)
ax2 = axes[1]
ax2.scatter(x2, y2, alpha=0.5)
xl = np.linspace(0, 300_000, 200)
ax2.plot(xl, np.polyval(np.polyfit(x2, y2, 1), xl), "r--", label="deg=1 (вводит в заблуждение)")
ax2.plot(xl, np.polyval(np.polyfit(x2, y2, 2), xl), "g-", label="deg=2")
ax2.set(title="Нелинейная зависимость", xlabel="Пробег, км", ylabel="Цена, ₽")
ax2.legend()
ax2.grid(alpha=0.3)

fig.savefig(HERE / "task_17.png", dpi=150)
plt.show()
