"""
Задача 44 (Button, RadioButtons, CheckButtons в одном дашборде). Автосалон показывает инвесторам интерактивный дашборд с 4 виджетами: слайдер темпа роста, радио-кнопки для выбора марки (Toyota / Hyundai / Kia), чекбоксы для включения/отключения сетки и легенды, кнопка «Сброс». Реализуйте class InteractivePlot с методами _update, _change_brand, _toggle_grid, _reset. Используйте RadioButtons.on_clicked(callback) (принимает метку выбранного варианта), CheckButtons.on_clicked(callback) (принимает метку кликнутого флажка), Button.on_clicked(callback) (принимает event, но обычно игнорируется). Ожидаемый вывод: 4 виджета работают совместно; кнопка сброса возвращает исходные значения. В комментариях объясните: чем RadioButtons отличается от CheckButtons (первый — один активный, второй — много независимых); как Button.on_clicked(callback) отличается от Slider.on_changed(callback) (первый по клику, второй при изменении); зачем хранить ссылки на виджеты (self.slider = Slider(...) — иначе GC удалит); как set_active(index) у RadioButtons программно выбирает вариант; почему activecolor улучшает UX (выделяет активный вариант); что произойдёт при двух активных RadioButtons (это не «галочки», нельзя выбрать два — попытка вызовет set_active и сбросит первый).
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button, CheckButtons, RadioButtons, Slider

HERE = Path(__file__).parent
BRANDS = ["Toyota", "Hyundai", "Kia"]
BASE = {"Toyota": 100, "Hyundai": 80, "Kia": 70}


class InteractivePlot:
    def __init__(self):
        self.months = np.arange(36)
        self.brand = "Toyota"
        self.growth0 = 0.05
        self.fig, self.ax = plt.subplots(figsize=(12, 7))
        self.fig.subplots_adjust(left=0.25, bottom=0.22)
        self.line, = self.ax.plot([], [], lw=2, label="Прогноз")
        self.ax.set(xlabel="Месяц", ylabel="Продано, шт.")

        # ВАЖНО хранить ссылки на виджеты в self: у виджета нет «владельца» кроме нашей
        # переменной. Если создать Slider(...) в локальной переменной функции, она уйдёт
        # из области видимости, сборщик мусора удалит объект и callbacks перестанут
        # работать (виджет станет «мёртвым»).
        self.slider = Slider(self.fig.add_axes([0.25, 0.08, 0.6, 0.03]), "Рост",
                             0.01, 0.20, valinit=self.growth0, valfmt="%.2f")
        # RadioButtons: ОДИН активный вариант из нескольких (взаимоисключающие).
        # activecolor - цвет выбранной точки: пользователь сразу видит активный вариант.
        self.radio = RadioButtons(self.fig.add_axes([0.02, 0.55, 0.17, 0.2]), BRANDS,
                                  activecolor="tab:green")
        # CheckButtons: НЕСКОЛЬКО независимых флажков (каждый вкл/выкл сам по себе).
        self.check = CheckButtons(self.fig.add_axes([0.02, 0.32, 0.17, 0.15]),
                                  ["Сетка", "Легенда"], [True, True])
        self.button = Button(self.fig.add_axes([0.02, 0.15, 0.17, 0.07]), "Сброс")

        # Slider.on_changed срабатывает при ЛЮБОМ изменении значения (в т.ч. при
        # перетаскивании); Button.on_clicked - только по клику; callback получает event
        # (обычно игнорируем). Radio/Check передают в callback МЕТКУ (строку).
        self.slider.on_changed(self._update)
        self.radio.on_clicked(self._change_brand)
        self.check.on_clicked(self._toggle_grid)
        self.button.on_clicked(self._reset)
        self._update(None)

    def _y(self):
        return BASE[self.brand] * (1 + self.slider.val) ** self.months

    def _update(self, _):
        self.line.set_data(self.months, self._y())
        self.line.set_label(self.brand)
        self.ax.set_title(f"Прогноз: {self.brand}, рост {self.slider.val:.0%}/мес")
        self.ax.relim()
        self.ax.autoscale_view()
        self._apply_flags()
        self.fig.canvas.draw_idle()

    def _change_brand(self, label):
        self.brand = label
        self._update(None)

    def _apply_flags(self):
        status = dict(zip(["Сетка", "Легенда"], self.check.get_status()))
        # grid(False, alpha=...) даёт предупреждение (свойства при выключенной сетке), поэтому
        # alpha задаём только при включении
        if status["Сетка"]:
            self.ax.grid(True, alpha=0.3)
        else:
            self.ax.grid(False)
        leg = self.ax.get_legend()
        if leg:
            leg.remove()
        if status["Легенда"]:
            self.ax.legend(loc="upper left")

    def _toggle_grid(self, label):          # label - метка кликнутого флажка
        self._apply_flags()
        self.fig.canvas.draw_idle()

    def _reset(self, event):
        # set_active(index) программно выбирает вариант (и вызывает on_clicked-callback)
        self.radio.set_active(0)
        self.slider.reset()                 # возвращает valinit
        for i, v in enumerate(self.check.get_status()):
            if not v:
                self.check.set_active(i)    # включаем выключенные флажки
        # Два активных RadioButtons невозможны по построению: set_active(k) снимает
        # предыдущий выбор - это не галочки, а переключатель с единственным значением.


if __name__ == "__main__":
    ip = InteractivePlot()
    ip.radio.set_active(2)                  # имитация кликов
    ip.slider.set_val(0.15)
    ip.check.set_active(0)                  # выключили сетку
    print("до сброса:", ip.brand, round(ip.slider.val, 2), ip.check.get_status())
    ip._reset(None)
    print("после сброса:", ip.brand, round(ip.slider.val, 2), ip.check.get_status())
    ip.fig.savefig(HERE / "44.png", dpi=120)
    plt.show()
