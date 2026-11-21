"""
Задача 28 (contour функции потерь). Автосалон использует ML для прогнозирования спроса на модели. Чтобы понять, насколько сложна оптимизация модели, визуализируйте функцию потерь от двух параметров (например, w1 = скидка, w2 = рекламный бюджет). Используйте функцию Розенброка loss(w1, w2) = (w1 - 1)**2 + 10 * (w2 - w1**2)**2. Создайте meshgrid 200×200, постройте cf = ax.contourf(W1, W2, np.log1p(Z), levels=20, cmap="viridis") и поверх ax.contour(W1, W2, np.log1p(Z), levels=15, colors="white", linewidths=0.5). Отметьте минимум ax.plot(1, 1, "r*", markersize=20). Ожидаемый вывод: «долина Розенброка» с изолиниями и минимумом. В комментариях объясните: зачем np.log1p(Z) (сжать динамический диапазон — иначе вся «долина» будет одного цвета); почему для несимметричных данных выбирают sequential-палитру, а для симметричных относительно нуля — diverging (RdBu); что делает clabel(contour, inline=True); как levels=np.logspace(-1, 3, 20) помогает для данных, меняющихся в тысячи раз; что произойдёт при levels=3 (теряется форма); как norm="log" в contourf автоматически применяет логарифмическую шкалу.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).parent


def loss(w1, w2):
    return (w1 - 1) ** 2 + 10 * (w2 - w1 ** 2) ** 2


w1 = np.linspace(-2, 2, 200)
w2 = np.linspace(-1, 3, 200)
W1, W2 = np.meshgrid(w1, w2)           # две 2D-сетки 200x200 - координаты каждого узла
Z = loss(W1, W2)

fig, axes = plt.subplots(2, 2, figsize=(14, 11), layout="constrained")

# 1) Основной: log1p сжимает динамический диапазон. Z меняется от 0 до ~сотен; в линейной
# шкале почти вся «долина» (малые значения) попадёт в один цвет, а цвета израсходуются на
# крутые склоны. log1p(Z)=ln(1+Z) корректен и в нуле (в отличие от log).
ax = axes[0, 0]
cf = ax.contourf(W1, W2, np.log1p(Z), levels=20, cmap="viridis")
cs = ax.contour(W1, W2, np.log1p(Z), levels=15, colors="white", linewidths=0.5)
# clabel подписывает изолинии значениями; inline=True «вырезает» кусок линии под текстом,
# чтобы цифры читались.
ax.clabel(cs, inline=True, fontsize=7)
ax.plot(1, 1, "r*", markersize=20, label="Минимум (1, 1)")
fig.colorbar(cf, ax=ax, label="log(1 + loss)")
ax.set_title("log1p(Z), levels=20")
ax.legend()
# Палитра: loss >= 0 и не симметрична вокруг какого-то центра -> sequential (viridis:
# светлее = больше). Diverging (RdBu, coolwarm) нужна, когда есть содержательный
# центр (0, среднее) и важны знаки отклонений - корреляции, ошибки прогноза.

# 2) levels=np.logspace(-1, 3, 20): границы уровней расположены по геометрической прогрессии
# (0.1 ... 1000) - данные, меняющиеся в тысячи раз, получают равномерную детализацию и
# около минимума, и на склонах (линейные уровни «съели» бы долину).
ax = axes[0, 1]
cf = ax.contourf(W1, W2, Z, levels=np.logspace(-1, 3, 20), cmap="viridis", extend="both")
ax.plot(1, 1, "r*", markersize=20)
fig.colorbar(cf, ax=ax, label="loss")
ax.set_title("levels=np.logspace(-1, 3, 20)")

# 3) norm="log": логарифмическая шкала цвета без ручного преобразования Z.
# Требует положительных значений (на минимуме Z=0 - добавляем малое смещение).
ax = axes[1, 0]
cf = ax.contourf(W1, W2, Z + 1e-3, levels=np.logspace(-3, 3, 20), norm="log", cmap="viridis")
ax.plot(1, 1, "r*", markersize=20)
fig.colorbar(cf, ax=ax, label="loss (log scale)")
ax.set_title('norm="log"')

# 4) levels=3: всего 3 уровня -> форма «банановой» долины теряется, остаются грубые зоны.
ax = axes[1, 1]
cf = ax.contourf(W1, W2, np.log1p(Z), levels=3, cmap="viridis")
ax.plot(1, 1, "r*", markersize=20)
fig.colorbar(cf, ax=ax)
ax.set_title("levels=3 - форма потеряна")

for a in axes.ravel():
    a.set(xlabel="w1 (скидка)", ylabel="w2 (рекламный бюджет)")
fig.savefig(HERE / "task_28.png", dpi=150)
plt.show()
