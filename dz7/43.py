"""
Задача 43 (Slider с PlotState-датаклассом). Автосалон проводит интерактивную демонстрацию для инвесторов: покажите, как меняется прогноз продаж при разных темпах роста и сезонных коэффициентах. Интерактивные виджеты превращают статичный график в панель управления. Реализуйте @dataclass class PlotState: growth: float = 0.05; seasonality: float = 0.2 и два Slider — «темп роста» (0.01–0.20) и «сезонность» (0.0–1.0). В callback def update(_): state.growth = slider_growth.val; state.seasonality = slider_season.val; y = base * (1 + state.growth) ** months * (1 + state.seasonality * np.sin(2 * np.pi * months / 12)); line.set_ydata(y); fig.canvas.draw_idle(). Расположите слайдеры через fig.subplots_adjust(bottom=0.25) и fig.add_axes([0.15, 0.15, 0.7, 0.03]) (и второй на [0.15, 0.05, ...]). Ожидаемый вывод: слайдеры внизу, график перестраивается в реальном времени. В комментариях объясните: зачем PlotState (отделить состояние от вида — упрощает тестирование); почему обязательно fig.canvas.draw_idle() (без него данные обновятся, но график не перерисуется); что произойдёт без subplots_adjust (слайдеры перекроют график); как blitting ускоряет перерисовку (перерисовывается только линия, а не вся фигура); как valfmt="%.2f" форматирует отображение значения (0.05 → "0.05"); что будет при valstep=0.01 (значения квантуются — удобно для «шага 1%»).
"""
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider

HERE = Path(__file__).parent


# PlotState хранит ТОЛЬКО параметры модели (без matplotlib). Логику расчёта можно
# тестировать без графики: forecast(state) -> массив. Вид (Line2D, виджеты) отделён от данных.
@dataclass
class PlotState:
    growth: float = 0.05
    seasonality: float = 0.2


months = np.arange(0, 36)
base = 100.0


def forecast(state: PlotState) -> np.ndarray:
    return base * (1 + state.growth) ** months * (1 + state.seasonality * np.sin(2 * np.pi * months / 12))


state = PlotState()
fig, ax = plt.subplots(figsize=(11, 7))
# Без subplots_adjust(bottom=...) оси занимают почти всю фигуру, и слайдеры,
# добавленные через add_axes внизу, наложатся на сам график. Освобождаем 25% снизу.
fig.subplots_adjust(bottom=0.25)

line, = ax.plot(months, forecast(state), lw=2)
ax.set(title="Прогноз продаж", xlabel="Месяц", ylabel="Продано, шт.")
ax.grid(alpha=0.3)

# add_axes([left, bottom, width, height]) - в долях фигуры, ось под каждый слайдер
ax_g = fig.add_axes([0.15, 0.15, 0.7, 0.03])
ax_s = fig.add_axes([0.15, 0.05, 0.7, 0.03])
# valfmt="%.2f": как показывать число справа от слайдера (0.05 -> "0.05").
# valstep=0.01: значения квантуются с шагом 0.01 - ползунок «щёлкает» по целым процентам.
slider_growth = Slider(ax_g, "Темп роста", 0.01, 0.20, valinit=state.growth, valfmt="%.2f", valstep=0.01)
slider_season = Slider(ax_s, "Сезонность", 0.0, 1.0, valinit=state.seasonality, valfmt="%.2f", valstep=0.05)


def update(_):
    state.growth = slider_growth.val
    state.seasonality = slider_season.val
    line.set_ydata(forecast(state))      # меняем только данные, объект линии тот же
    ax.relim()
    ax.autoscale_view()
    # draw_idle() ПОМЕЧАЕТ холст «грязным» - перерисовка произойдёт в ближайший цикл
    # событий (не блокируя UI и не чаще, чем нужно). Без него set_ydata обновит данные,
    # но картинка на экране останется старой.
    fig.canvas.draw_idle()


slider_growth.on_changed(update)
slider_season.on_changed(update)

# Blitting: вместо перерисовки всей фигуры сохраняется «фон» (оси, сетка, подписи),
# а на каждом кадре перерисовывается только анимируемый артист (линия, animated=True) -
# в разы быстрее на сложных графиках. Widgets Slider поддерживают это на уровне
# backend'а (useblit=True у некоторых виджетов: RangeSlider/Cursor/SpanSelector).

if __name__ == "__main__":
    # Имитация движения слайдеров (в обычной сессии - перетаскиваем мышью)
    slider_growth.set_val(0.12)
    slider_season.set_val(0.6)
    print(f"growth={state.growth:.2f}, seasonality={state.seasonality:.2f}, last y={line.get_ydata()[-1]:.0f}")
    fig.savefig(HERE / "43.png", dpi=120)
    plt.show()
