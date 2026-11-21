"""
Задача 53 (ReportBuilder — ООП-обёртка для дашбордов). Автосалон готовит ежемесячный отчёт из 5–9 графиков. Код легко превращается в «лапшу» из axes[i, j].plot(...). Правильная архитектура отделяет «что рисовать» от «как размещать». Реализуйте @dataclass class ReportPage: title: str; plot_fn: Callable[[Axes], None] и class ReportBuilder с build() (создаёт фигуру и размещает страницы), save(path, dpi) (вызывает build + savefig + plt.close). Соберите 5 страниц: динамика продаж (line), топ моделей (bar), распределение цен (hist), цены по маркам (box), heatmap марок по месяцам (imshow). Пустые ячейки скройте через axes.flat[n:].axis("off"). Ожидаемый вывод: одна фигура с 5 графиками. В комментариях объясните: зачем ReportPage (разделяет «что рисовать» и «как размещать» — легко добавить новый график); как axes.flat[n:] скрывает пустые ячейки при нечётном числе графиков; зачем plt.close(fig) (освободить память при генерации десятков отчётов); как расширить to_pdf через PdfPages (многостраничный отчёт); как связать с PlotConfig (передавать конфигурацию в __init__); когда такой класс — овер-инжиниринг (для одного графика проще plt.subplots).
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.backends.backend_pdf import PdfPages

HERE = Path(__file__).parent


@dataclass
class PlotConfig:
    """Централизованные настройки (связь с PlotConfig из задачи 2): размеры, dpi, сетка."""
    figsize_per_cell: tuple = (5.5, 4.0)
    ncols: int = 3
    dpi: int = 150
    grid_alpha: float = 0.3


# ReportPage = «ЧТО рисовать»: заголовок + функция, которая рисует на ПЕРЕДАННОЙ оси.
# Она ничего не знает о сетке, размерах фигуры и месте страницы -> страницы можно
# переставлять, добавлять и переиспользовать в разных отчётах без правки раскладки.
@dataclass
class ReportPage:
    title: str
    plot_fn: Callable[[Axes], None]


class ReportBuilder:
    """«КАК размещать»: считает сетку, создаёт фигуру, вызывает plot_fn каждой страницы."""

    def __init__(self, pages: List[ReportPage], config: PlotConfig = PlotConfig()):
        self.pages, self.cfg = pages, config

    def build(self):
        n = len(self.pages)
        ncols = min(self.cfg.ncols, n)
        nrows = int(np.ceil(n / ncols))
        w, h = self.cfg.figsize_per_cell
        fig, axes = plt.subplots(nrows, ncols, figsize=(w * ncols, h * nrows), layout="constrained",
                                 squeeze=False)            # squeeze=False -> axes всегда 2D
        for ax, page in zip(axes.flat, self.pages):
            page.plot_fn(ax)
            ax.set_title(page.title)
            ax.grid(alpha=self.cfg.grid_alpha)
        # axes.flat - плоский итератор по сетке; срез [n:] - все «лишние» ячейки после
        # n-й (при 5 графиках на сетке 2x3 - одна ячейка). axis("off") скрывает рамку и
        # деления, чтобы не торчала пустая ось. (.flat поддерживает срезы - в отличие от
        # обычного итератора - и индексируется как одномерный вид массива.)
        for ax in list(axes.flat)[n:]:
            ax.axis("off")
        return fig

    def save(self, path, dpi=None):
        fig = self.build()
        fig.savefig(path, dpi=dpi or self.cfg.dpi, bbox_inches="tight")
        # close: pyplot хранит ссылки на ВСЕ открытые фигуры; при генерации десятков
        # отчётов память растёт (и RuntimeWarning после 20 фигур). close освобождает её.
        plt.close(fig)
        return Path(path)

    def to_pdf(self, path):
        # Многостраничный вариант: каждая страница отчёта - своя страница PDF
        with PdfPages(path) as pdf:
            for page in self.pages:
                fig, ax = plt.subplots(figsize=(8, 5), layout="constrained")
                page.plot_fn(ax)
                ax.set_title(page.title)
                pdf.savefig(fig)
                plt.close(fig)
        return Path(path)


rng = np.random.default_rng(53)
days = np.arange(1, 31)
sales = 45 + 8 * np.sin(days / 5) + rng.normal(0, 3, 30)
models = ["Camry", "Rio", "X5", "Solaris", "Tiguan"]
top = [120, 95, 80, 70, 55]
prices = rng.normal(2.4e6, 6e5, 600)
brands = ["Toyota", "Kia", "BMW", "Hyundai"]
box_data = [rng.normal(m, 3e5, 80) for m in (2.4e6, 1.9e6, 5.0e6, 2.0e6)]
heat = rng.integers(20, 120, (4, 6))


def p_line(ax): ax.plot(days, sales); ax.set(xlabel="День", ylabel="шт.")
def p_bar(ax): ax.bar(models, top, color="C2"); ax.tick_params(axis="x", rotation=30)
def p_hist(ax): ax.hist(prices, bins=25, color="C1"); ax.set_xlabel("Цена, ?")
def p_box(ax): ax.boxplot(box_data, tick_labels=brands, patch_artist=True); ax.set_ylabel("Цена, ?")
def p_heat(ax):
    im = ax.imshow(heat, cmap="YlGnBu", aspect="auto")
    ax.set_yticks(range(4), brands)
    ax.set_xticks(range(6), ["Янв", "Фев", "Мар", "Апр", "Май", "Июн"])
    ax.figure.colorbar(im, ax=ax)


pages = [ReportPage("Динамика продаж", p_line), ReportPage("Топ моделей", p_bar),
         ReportPage("Распределение цен", p_hist), ReportPage("Цены по маркам", p_box),
         ReportPage("Марки ? месяцы", p_heat)]

if __name__ == "__main__":
    rb = ReportBuilder(pages)
    print("saved:", rb.save(HERE / "53.png"), "|", rb.to_pdf(HERE / "53.pdf"))
    # Новый график = одна функция + одна ReportPage в списке; раскладка не меняется.
    # Овер-инжиниринг: для ОДНОГО графика/разового скрипта проще plt.subplots() и прямое
    # рисование; класс окупается при повторяющихся отчётах и командной работе.
