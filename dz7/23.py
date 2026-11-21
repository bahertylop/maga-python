"""
🟣 Уровень 3. Мастер (задачи 23–32)
Задача 23 (FigureBuilder — ООП-обёртка для сетки). Автосалон готовит дашборд из 4 графиков (динамика продаж, топ моделей, распределение цен, продажи по маркам). При построении код обрастает повторяющимися axes[i, j].plot(...) и axes[i, j].set_title(...). Реализуйте class FigureBuilder с __init__(self, nrows=1, ncols=1, **kw), методами plot(i, j, x, y, **kw), title(i, j, text, **kw), grid(**kw) и savefig(path, **kw), возвращающими self для цепочек. Используйте np.atleast_2d(self.axes), чтобы индексация [i, j] работала и для одномерных сеток. Создайте FigureBuilder(2, 2, figsize=(12, 8), layout="constrained").plot(0, 0, ...).title(0, 0, "Продажи").grid(alpha=0.3).savefig("dashboard.png", dpi=300). Ожидаемый вывод: сетка 2×2 с 4 графиками. В комментариях объясните: зачем fluent API (читаемость цепочек — код похож на английский); что произойдёт при subplots(1, 3) без atleast_2d (одномерный массив — индексация [0, 1] выбросит IndexError); как расширить класс методами set_xlabel, legend, axhline, чтобы сохранить принцип единственной ответственности; когда такой класс — овер-инжиниринг; как связать FigureBuilder с PlotConfig из задачи 2; почему return self в каждом методе — ключевой паттерн (позволяет цепочки любой длины).
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).parent


class FigureBuilder:
    """Fluent-обёртка над plt.subplots: каждый метод возвращает self."""

    def __init__(self, nrows=1, ncols=1, **kw):
        self.nrows, self.ncols = nrows, ncols
        self.fig, axes = plt.subplots(nrows, ncols, **kw)
        # Без atleast_2d при subplots(1, 3) axes - ОДНОМЕРНЫЙ массив из 3 осей, и
        # axes[0, 1] даёт IndexError (too many indices). При subplots(1, 1) axes вообще
        # одиночный Axes, не массив. atleast_2d приводит всё к 2D, а reshape(nrows, ncols)
        # исправляет ориентацию: для subplots(3, 1) atleast_2d даёт (1, 3), а нужно (3, 1).
        self.axes = np.atleast_2d(axes).reshape(nrows, ncols)

    # --- рисование: каждый метод ИМЕЕТ одну ответственность и возвращает self ---
    # `return self` - ключевой паттерн fluent API: результат метода - тот же объект, значит
    # к нему можно сразу применить следующий метод; цепочка любой длины:
    # FigureBuilder(...).plot(...).title(...).grid(...).savefig(...) читается как предложение.
    def plot(self, i, j, x, y, **kw):
        self.axes[i, j].plot(x, y, **kw)
        return self

    def bar(self, i, j, x, height, **kw):
        self.axes[i, j].bar(x, height, **kw)
        return self

    def hist(self, i, j, x, **kw):
        self.axes[i, j].hist(x, **kw)
        return self

    def title(self, i, j, text, **kw):
        self.axes[i, j].set_title(text, **kw)
        return self

    # Расширения (по одной ответственности на метод - «один метод = одно действие»):
    def set_xlabel(self, i, j, text, **kw):
        self.axes[i, j].set_xlabel(text, **kw)
        return self

    def set_ylabel(self, i, j, text, **kw):
        self.axes[i, j].set_ylabel(text, **kw)
        return self

    def legend(self, i, j, **kw):
        self.axes[i, j].legend(**kw)
        return self

    def axhline(self, i, j, y, **kw):
        self.axes[i, j].axhline(y, **kw)
        return self

    def grid(self, **kw):
        for ax in self.axes.flat:      # сетка на всех подграфиках
            ax.grid(**kw)
        return self

    def savefig(self, path, **kw):
        self.fig.savefig(path, **kw)
        return self

    def show(self):
        plt.show()
        return self


# Связь с PlotConfig из задачи 2 (датакласс с настройками стиля): можно принимать
# config в __init__ и делать plt.rcParams.update(config.to_rc()) / config.figsize -> kw.
# Пример-заглушка (в оригинальной задаче 2 структура может отличаться):
from dataclasses import dataclass


@dataclass
class PlotConfig:
    figsize: tuple = (12, 8)
    dpi: int = 150
    grid_alpha: float = 0.3

    def build(self, nrows, ncols):
        return FigureBuilder(nrows, ncols, figsize=self.figsize, layout="constrained")


if __name__ == "__main__":
    rng = np.random.default_rng(23)
    days = np.arange(1, 31)
    sales = 40 + 10 * np.sin(days / 4) + rng.normal(0, 3, 30)
    models = ["A", "B", "C", "D", "E"]
    top = [120, 95, 80, 60, 45]
    prices = rng.normal(2.4e6, 5e5, 500)
    brands = ["Toyota", "Kia", "Hyundai", "VW"]
    brand_sales = [310, 260, 240, 280]

    (FigureBuilder(2, 2, figsize=(12, 8), layout="constrained")
        .plot(0, 0, days, sales, marker="o", label="Продажи")
        .title(0, 0, "Продажи").set_ylabel(0, 0, "шт.")
        .axhline(0, 0, sales.mean(), color="r", ls="--", label="Среднее").legend(0, 0)
        .bar(0, 1, models, top).title(0, 1, "Топ моделей")
        .hist(1, 0, prices, bins=25).title(1, 0, "Распределение цен")
        .bar(1, 1, brands, brand_sales, color="C2").title(1, 1, "Продажи по маркам")
        .grid(alpha=0.3)
        .savefig(HERE / "dashboard.png", dpi=300)
        .show())

    # Проверка на 1D-сетке: subplots(1, 3) работает благодаря atleast_2d
    FigureBuilder(1, 3, figsize=(12, 3)).plot(0, 2, [1, 2], [3, 4]).title(0, 2, "1D-сетка OK")
    # Когда это овер-инжиниринг: для одного-двух графиков обычного plt.subplots достаточно;
    # класс окупается, когда одна и та же сетка собирается в нескольких отчётах.
