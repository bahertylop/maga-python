"""Задача 2. Конфигурация фигуры через dataclass и фабрика."""
from dataclasses import dataclass, replace
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

@dataclass
class PlotConfig:
    figsize: tuple = (10, 6)  # дюймы
    dpi: int = 100
    facecolor: str = "white"
    layout: str = "constrained"
    def with_dpi(self, new_dpi: int):
        return replace(self, dpi=new_dpi)  # новый объект конфигурации, исходный не меняется

def make_figure(cfg: PlotConfig):
    fig, ax = plt.subplots(figsize=cfg.figsize, dpi=cfg.dpi,
                           facecolor=cfg.facecolor, layout=cfg.layout)
    return fig, ax

if Path("sales.csv").exists():
    df = pd.read_csv("sales.csv", parse_dates=["date"])
    y = df["cars_sold"] if "cars_sold" in df else df.iloc[:, -1]
else:
    y = pd.Series([4, 5, 3, 7, 6, 8, 5, 9, 6, 7])
cfg = PlotConfig(figsize=(12, 8), dpi=200, facecolor="#f5f5f5")
fig, ax = make_figure(cfg)
ax.plot(y)
ax.set_title("Продажи автосалона")
width_px, height_px = fig.get_size_inches() * fig.dpi
print(f"{int(width_px)} × {int(height_px)} px")  # 2400 × 1600
# fig inches * dpi = pixels; inches удобны, т.к. dpi позволяет одинаково масштабировать
# макет для экрана/печати. constrained layout автоматически распределяет место под подписи.
# Facecolor Figure — фон всего холста; Axes.set_facecolor — фон области графика.
# Экран обычно 100–150 dpi, печать — около 300 dpi и выше. Результат зависит от backend.
# replace даёт неизменяемую по смыслу конфигурацию: удобный функциональный стиль поверх ООП.
# Разные фоны полезны: фирменный цвет всей фигуры и белая область данных.
ax.set_facecolor("white")
fig.savefig("plot_config.png", bbox_inches="tight")
plt.show()
