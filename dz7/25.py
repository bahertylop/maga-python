"""
Задача 25 (sharex/sharey и синхронизация зума). Автосалон строит два подграфика: дневные продажи и их первая разность (прирост день ко дню). Обе линии относятся к одним и тем же датам, и хочется синхронизировать зум. Создайте fig, axes = plt.subplots(2, 1, sharex=True, figsize=(12, 8), layout="constrained"), постройте axes[0].plot(df.index, df["cars_sold"]) и axes[1].plot(df.index, df["cars_sold"].diff()), уберите подпись X у верхнего (axes[0].set_xlabel("")). Дополнительно создайте вторую фигуру без layout и примените fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1, hspace=0.05) — почти вплотную. Ожидаемый вывод: две синхронизированные оси X; без дублирования подписи. В комментариях объясните: как sharex синхронизирует зум (перетаскивание одной оси двигает обе); зачем убирать подпись X у верхнего подграфика (визуальный шум — даты повторяются); почему subplots_adjust не работает с layout="constrained"; что делает hspace=0.05; как ax.get_xlim() получить текущие границы для сохранения в отчёт; что произойдёт при sharex="col" в сетке 2×2.
"""
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).parent
rng = np.random.default_rng(25)
df = pd.DataFrame({"cars_sold": (50 + np.cumsum(rng.normal(0, 4, 90))).round()},
                  index=pd.date_range("2024-01-01", periods=90, freq="D"))

# sharex=True: обе оси используют ОДИН объект оси X (общие пределы и локаторы). Зум или
# сдвиг на любом из графиков автоматически двигает другой - даты всегда выровнены.
# У общей оси подписи делений верхнего графика скрываются автоматически.
fig, axes = plt.subplots(2, 1, sharex=True, figsize=(12, 8), layout="constrained")
axes[0].plot(df.index, df["cars_sold"])
axes[1].plot(df.index, df["cars_sold"].diff(), color="C1")
axes[1].axhline(0, color="gray", lw=0.8)

# Подпись оси X у верхнего убираем: те же даты повторять дважды - шум; хватает нижней.
axes[0].set_xlabel("")
axes[1].set_xlabel("Дата")
axes[0].set_ylabel("Продано, шт.")
axes[1].set_ylabel("Прирост день ко дню")
for ax in axes:
    ax.grid(alpha=0.3)

# get_xlim() возвращает границы в «числовых» единицах дат (дни от эпохи); переводим
# в даты через mdates.num2date, чтобы записать в отчёт.
x0, x1 = axes[0].get_xlim()
print("Видимый диапазон:", mdates.num2date(x0).date(), "-", mdates.num2date(x1).date())
fig.savefig(HERE / "task_25.png", dpi=150)

# Вторая фигура БЕЗ layout: subplots_adjust работает только с ручной раскладкой.
# При layout="constrained" (и "tight") менеджер раскладки сам пересчитывает позиции
# при каждой отрисовке и перезаписывает ваши значения - subplots_adjust игнорируется
# (с предупреждением). Поэтому две системы не смешиваем.
# hspace - вертикальный зазор между подграфиками в ДОЛЯХ средней высоты оси;
# hspace=0.05 - почти вплотную (подходит при sharex, когда подписи не мешают).
fig2, axes2 = plt.subplots(2, 1, sharex=True, figsize=(12, 8))
axes2[0].plot(df.index, df["cars_sold"])
axes2[1].plot(df.index, df["cars_sold"].diff(), color="C1")
fig2.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1, hspace=0.05)
fig2.savefig(HERE / "task_25_adjust.png", dpi=150)

# sharex="col" в сетке 2x2: ось X делится ВНУТРИ каждого столбца (верхний и нижний график
# столбца синхронны), но между столбцами - независимы. sharex=True - общая ось для всех
# четырёх; sharex="row" - общая по строкам. То же для sharey.
plt.show()
