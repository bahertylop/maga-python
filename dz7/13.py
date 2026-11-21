"""
Задача 13 (аннотации с argmax/argmin). Автосалон анализирует дневные продажи за месяц и хочет выделить дни-пики и дни-провалы (например, старт сезонных акций и «мёртвый» февраль). Загрузите daily_sales.csv с parse_dates=["date"], index_col="date", найдите idx_max = df["cars_sold"].idxmax() и idx_min = df["cars_sold"].idxmin(). Добавьте аннотации через ax.annotate(f"Пик: {df.loc[idx_max, 'cars_sold']:,}", xy=(idx_max, df.loc[idx_max, "cars_sold"]), xytext=(10, 20), textcoords="offset points", arrowprops=dict(arrowstyle="->", color="green", connectionstyle="arc3,rad=0.2")); аналогично для минимума с xytext=(-80, -30), color="red". Ожидаемый вывод: стрелки указывают на пики, текст смещён и не перекрывает линию. В комментариях объясните: чем textcoords="offset points" отличается от "data" и почему первый удобнее для смещения текста; почему idxmax() в Pandas возвращает метку индекса, а не позицию, и как это используется в xy; зачем arc3,rad=0.2 (изогнутая стрелка) и как rad=-0.2 развернёт изгиб; как bbox=dict(boxstyle="round,pad=0.5", facecolor="lightyellow", edgecolor="orange") в annotate улучшает читаемость поверх линий; что произойдёт без ha/va (текст «прилипнет» к точке и перекроет маркер); как аннотировать несколько близких точек, чтобы они не перекрывались.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).parent
CSV = HERE / "daily_sales.csv"

# --- синтетические данные (если файла нет) ---
if not CSV.exists():
    rng = np.random.default_rng(42)
    n = 60
    dates = pd.date_range("2024-01-01", periods=n, freq="D")
    sales = 45 + 6 * np.sin(np.arange(n) * 2 * np.pi / 7) + rng.normal(0, 3, n)
    sales[20:24] += 45          # старт сезонной акции -> пик
    sales[40:46] -= 30          # «мёртвый» февраль -> провал
    pd.DataFrame({"date": dates, "cars_sold": np.clip(sales, 3, None).round().astype(int)}) \
        .to_csv(CSV, index=False)

df = pd.read_csv(CSV, parse_dates=["date"], index_col="date")

# idxmax()/idxmin() возвращают МЕТКУ индекса (здесь Timestamp), а не позицию (для позиции -
# argmax()). Метка сразу годится для xy: ось X у нас - даты, т.е. xy задаётся в координатах
# данных (x = дата, y = значение). Через .loc[метка, колонка] достаём само значение.
idx_max = df["cars_sold"].idxmax()
idx_min = df["cars_sold"].idxmin()

fig, ax = plt.subplots(figsize=(12, 6), layout="constrained")
ax.plot(df.index, df["cars_sold"], marker="o", ms=3, color="C0")

# textcoords="offset points": xytext - смещение текста в ПУНКТАХ от точки xy. Смещение не
# зависит от масштаба данных и размера окна (20 pt всегда 20 pt). С textcoords="data"
# пришлось бы считать смещение в днях/штуках, оно «плыло» бы при зуме и смене диапазона.
#
# connectionstyle="arc3,rad=0.2": стрелка рисуется дугой (квадратичная кривая Безье); rad -
# степень изгиба. rad=-0.2 изгибает в противоположную сторону. Изгиб помогает
# обойти линию графика и не закрывать данные.
#
# bbox=dict(boxstyle="round,pad=0.5", ...): подложка под текстом, чтобы подпись читалась
# поверх линии и сетки.
#
# ha/va: без них текст выравнивается по умолчанию (ha="left", va="baseline"). Для текста,
# смещённого влево/вниз (минимум), «левый край» окажется ближе к точке и текст наползёт
# на стрелку/маркер. Явные ha="right", va="top" ставят «угол» текста к стрелке.
ax.annotate(
    f"Пик: {df.loc[idx_max, 'cars_sold']:,}",
    xy=(idx_max, df.loc[idx_max, "cars_sold"]),
    xytext=(10, 20), textcoords="offset points",
    ha="left", va="bottom", color="green", fontweight="bold",
    bbox=dict(boxstyle="round,pad=0.5", facecolor="lightyellow", edgecolor="orange"),
    arrowprops=dict(arrowstyle="->", color="green", connectionstyle="arc3,rad=0.2"),
)
ax.annotate(
    f"Провал: {df.loc[idx_min, 'cars_sold']:,}",
    xy=(idx_min, df.loc[idx_min, "cars_sold"]),
    xytext=(-80, -30), textcoords="offset points",
    ha="right", va="top", color="red", fontweight="bold",
    bbox=dict(boxstyle="round,pad=0.5", facecolor="lightyellow", edgecolor="orange"),
    arrowprops=dict(arrowstyle="->", color="red", connectionstyle="arc3,rad=-0.2"),  # rad<0 - изгиб в другую сторону
)

# Несколько близких точек: (1) разные смещения (чередуем вверх/вниз, влево/вправо),
# (2) разные rad у стрелок, (3) аннотируем только значимые точки (топ-N), а не все подряд.
# Здесь - 3 следующих по величине пика (кроме главного), с разведёнными смещениями.
others = df["cars_sold"].drop(idx_max).nlargest(3).sort_index()
offsets = [(-70, 35), (50, 45), (-20, 60)]
for (d, v), off in zip(others.items(), offsets):
    ax.annotate(str(v), xy=(d, v), xytext=off, textcoords="offset points",
                ha="center", va="bottom", fontsize=9,
                arrowprops=dict(arrowstyle="-", color="gray", connectionstyle="arc3,rad=0.15"))

ax.set(title="Дневные продажи автосалона", xlabel="Дата", ylabel="Продано, шт.")
ax.grid(alpha=0.3)
ax.margins(y=0.25)  # запас по Y, чтобы подписи не вылезали за оси
fig.savefig(HERE / "task_13.png", dpi=150)
plt.show()
