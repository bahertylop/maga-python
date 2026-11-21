"""
Задача 26 (bar с yerr из agg(["mean", "std"])). Автосалон сравнивает среднюю скидку по маркам с учётом разброса между сделками. Получите stats = results.groupby("brand")["discount"].agg(["mean", "std"]). Постройте bars = ax.bar(stats.index, stats["mean"], yerr=stats["std"], capsize=8, color=plt.cm.viridis(np.linspace(0.2, 0.8, len(stats))), edgecolor="black"). Установите ax.set_ylim(0, stats["mean"].max() * 1.3), подпишите значения через for bar, (m, s) in zip(bars, stats.itertuples(index=False)): ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + s + 500, f"{m:,.0f}", ha="center"). Ожидаемый вывод: столбцы с планками ошибок и подписями. В комментариях объясните: как agg(["mean", "std"]) готовит данные в одну строку (что было бы без agg — пришлось бы дважды вызывать groupby); почему yerr=std корректен (это стандартное отклонение, а не SEM; для SEM поделите на sqrt(n)); почему set_ylim с запасом * 1.3 (чтобы планки и подписи не обрезались); что произойдёт без capsize; как zip(bars, stats.itertuples()) обходит две коллекции одновременно; почему для метрик-долей set_ylim(0, 1) обязателен.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).parent
rng = np.random.default_rng(26)
mu = {"Toyota": 50_000, "Hyundai": 70_000, "Kia": 80_000, "Volkswagen": 60_000, "Skoda": 65_000}
results = pd.DataFrame([(b, rng.normal(m, m * 0.15)) for b, m in mu.items() for _ in range(80)],
                       columns=["brand", "discount"])

# agg(["mean", "std"]) считает обе статистики за ОДИН проход groupby и возвращает
# таблицу с колонками mean и std (индекс - марки). Без agg пришлось бы вызывать
# groupby дважды (.mean() и .std()) и склеивать результаты вручную.
stats = results.groupby("brand")["discount"].agg(["mean", "std"])

fig, ax = plt.subplots(figsize=(10, 6), layout="constrained")

# yerr=std - планка = ±1 стандартное отклонение: показывает разброс САМИХ СДЕЛОК.
# Это не SEM (стандартная ошибка среднего = std / sqrt(n)); SEM показывает точность
# оценки среднего и гораздо короче. Выбирайте то, что хотите сообщить читателю.
# capsize - длина «шляпок» на концах планок; без него планки - просто тонкие линии
# без ограничителей, границы диапазона читаются хуже.
bars = ax.bar(stats.index, stats["mean"], yerr=stats["std"], capsize=8,
              color=plt.cm.viridis(np.linspace(0.2, 0.8, len(stats))), edgecolor="black")

# Запас по Y: верхний конец планки = mean + std, плюс место под текст. Без запаса
# подписи и верхние «шляпки» упрутся в верхнюю границу осей или обрежутся.
# Для метрик-долей (0..1) set_ylim(0, 1) обязателен: иначе автомасштаб с планками
# покажет значения > 100% или отрицательные, что бессмысленно.
ax.set_ylim(0, stats["mean"].max() * 1.3)

# zip обходит две коллекции параллельно: bars (контейнер столбцов) и строки stats
# (itertuples(index=False) -> кортежи (mean, std)). Порядок одинаков, т.к. оба построены
# из одной таблицы stats.
for bar, (m, s) in zip(bars, stats.itertuples(index=False)):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + s + 500,
            f"{m:,.0f}", ha="center", va="bottom")

ax.set(title="Средняя скидка по маркам (±SD)", ylabel="Скидка, ₽")
ax.grid(axis="y", alpha=0.3)
fig.savefig(HERE / "task_26.png", dpi=150)
plt.show()
