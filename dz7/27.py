"""
Задача 27 (scatter + RANSAC-тренд). Автосалон анализирует связь рекламного бюджета и числа продаж, но в данных есть несколько дней с аномальными результатами (крупные корпоративные заказы искажают картину). Обычная линейная регрессия через np.polyfit сдвигается этими выбросами. Реализуйте два тренда: OLS через m, b = np.polyfit(x, y, 1) и RANSAC через RANSACRegressor(random_state=42).fit(X, y). Наложите оба: OLS — "r--", RANSAC — "g-", подпишите в легенде. Вычислите r_pearson = np.corrcoef(x, y)[0, 1] и r_spearman = scipy.stats.spearmanr(x, y).correlation. В комментариях объясните: чем OLS отличается от RANSAC; как интерпретировать разницу между r_pearson и r_spearman (нелинейность, выбросы — если Пирсон «портится», а Спирмен стабилен, значит, выбросы); почему polyfit(deg=2) для нелинейных зависимостей (например, эффект «насыщения» рекламы); как zorder держит RANSAC-линию поверх точек; что произойдёт при полном отсутствии выбросов (RANSAC ≈ OLS); как сохранить ransac.estimator_ — коэффициенты найденной модели для отчёта.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import scipy.stats
from sklearn.linear_model import RANSACRegressor

HERE = Path(__file__).parent
rng = np.random.default_rng(27)

n = 120
x = rng.uniform(50, 500, n)                  # рекламный бюджет, тыс. ₽
y = 10 + 0.12 * x + rng.normal(0, 3, n)      # продажи, шт.
out = rng.choice(n, 8, replace=False)
y[out] += rng.uniform(40, 70, 8)             # дни с крупными корпоративными заказами

# OLS (МНК) минимизирует сумму квадратов остатков по ВСЕМ точкам -> выбросы с большими
# остатками получают огромный вес и сдвигают линию. RANSAC: случайно берёт малые
# подвыборки, строит модель, считает «inliers» (точки, близкие к модели), и оставляет
# модель с наибольшим числом inliers; итоговая модель обучается только на inliers.
m, b = np.polyfit(x, y, 1)
X = x.reshape(-1, 1)                          # sklearn требует 2D-признаки
ransac = RANSACRegressor(random_state=42).fit(X, y)
x_line = np.linspace(x.min(), x.max(), 100)

r_pearson = np.corrcoef(x, y)[0, 1]
res = scipy.stats.spearmanr(x, y)
r_spearman = getattr(res, "statistic", None) or res.correlation   # .statistic в новом scipy

fig, ax = plt.subplots(figsize=(10, 6), layout="constrained")
ax.scatter(x, y, alpha=0.6, label="Дни")
ax.scatter(x[~ransac.inlier_mask_], y[~ransac.inlier_mask_], c="orange",
           edgecolors="black", label="Не inliers (RANSAC)")
ax.plot(x_line, m * x_line + b, "r--", lw=2, label=f"OLS: наклон {m:.3f}")
# zorder=4: линия рисуется поверх точек (у scatter по умолчанию zorder=1)
ax.plot(x_line, ransac.predict(x_line.reshape(-1, 1)), "g-", lw=2.5, zorder=4,
        label=f"RANSAC: наклон {ransac.estimator_.coef_[0]:.3f}")
ax.set(title=f"Pearson r={r_pearson:.2f}, Spearman ρ={r_spearman:.2f}",
       xlabel="Рекламный бюджет, тыс. ₽", ylabel="Продажи, шт.")
ax.legend()
ax.grid(alpha=0.3)

# r_pearson vs r_spearman: Pearson меряет ЛИНЕЙНУЮ связь по значениям и «портится» от
# выбросов; Spearman - по рангам (монотонную связь), от выбросов почти не страдает. Если
# Pearson заметно ниже Spearman - в данных выбросы (или нелинейность). В реальности
# при выбросах Spearman держится ближе к «настоящей» связи.
#
# Нелинейность («насыщение» рекламы): прямая плохо описывает эффект убывающей отдачи;
# тогда np.polyfit(x, y, 2) (или лог-модель) даёт кривую, которая «выходит на плато».
#
# Без выбросов RANSAC ≈ OLS: почти все точки - inliers, итоговая модель обучается на всех.
#
# Параметры найденной модели для отчёта: ransac.estimator_ - линейная модель, обученная на
# inliers: ransac.estimator_.coef_[0] - наклон, ransac.estimator_.intercept_ - сдвиг.
print(f"OLS:    y = {m:.3f}*x + {b:.2f}")
print(f"RANSAC: y = {ransac.estimator_.coef_[0]:.3f}*x + {ransac.estimator_.intercept_:.2f}")
fig.savefig(HERE / "task_27.png", dpi=150)
plt.show()
