"""
Задача 45 (TextBox и RangeSlider с синхронизацией). Автосалон хочет, чтобы менеджер мог ввести точную цену через поле ввода или через слайдер — оба варианта должны синхронизироваться. Реализуйте TextBox для точной цены (on_submit → slider.set_val(float(text))), RangeSlider для выбора диапазона дат (ax.set_xlim(*rslider.val)). Синхронизируйте Slider → TextBox с флагом _updating: def on_slider(val): if _guard["updating"]: return; _guard["updating"] = True; textbox.set_val(f"{val:.2f}"); _guard["updating"] = False; redraw(). Обработайте невалидный ввод через try/except ValueError с ax.set_title("Ошибка: введите число"). Ожидаемый вывод: TextBox ↔ Slider синхронизированы; RangeSlider меняет зум. В комментариях объясните: почему без флага _updating возникает бесконечная рекурсия (TextBox → Slider → TextBox → ...); зачем try/except для TextBox (пользователь может ввести буквы); что делает RangeSlider.val (кортеж (min, max) из двух значений); как blitting ускоряет RangeSlider на больших данных (перерисовывается только область внутри зума); что произойдёт при textbox.set_val внутри callback без флага (бесконечная рекурсия → переполнение стека); как slider.set_val(v) программно устанавливает значение и триггерит on_changed (поэтому и нужен флаг).
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import RangeSlider, Slider, TextBox

HERE = Path(__file__).parent
rng = np.random.default_rng(45)
days = np.arange(365)
sales = 50 + 10 * np.sin(days / 30) + rng.normal(0, 3, 365)

fig, ax = plt.subplots(figsize=(12, 8))
fig.subplots_adjust(bottom=0.32)
ax.plot(days, sales)
ax.set(xlabel="День года", ylabel="Продано, шт.", title="Цена и диапазон")
ax.grid(alpha=0.3)
price_line = ax.axhline(60, color="r", ls="--", label="Цена-порог")

slider = Slider(fig.add_axes([0.15, 0.2, 0.55, 0.03]), "Цена", 30, 90, valinit=60, valfmt="%.2f")
textbox = TextBox(fig.add_axes([0.8, 0.2, 0.12, 0.04]), "", initial="60.00")
rslider = RangeSlider(fig.add_axes([0.15, 0.1, 0.55, 0.03]), "Диапазон", 0, 364, valinit=(0, 364), valfmt="%d")

# Флаг-защита от рекурсии. Цепочка: slider.set_val -> on_changed -> textbox.set_val ->
# (set_val у TextBox вызывает on_submit/on_text_change в зависимости от версии) ->
# slider.set_val -> on_changed -> ... Без флага это бесконечный цикл вплоть до
# RecursionError (переполнение стека). Флаг «я сам сейчас обновляю» разрывает цикл.
_guard = {"updating": False}


def redraw():
    price_line.set_ydata([slider.val, slider.val])
    fig.canvas.draw_idle()


def on_slider(val):
    if _guard["updating"]:
        return
    _guard["updating"] = True
    try:
        textbox.set_val(f"{val:.2f}")
    finally:
        _guard["updating"] = False      # finally - флаг снимется, даже если случится исключение
    redraw()


def on_submit(text):
    if _guard["updating"]:
        return
    # Пользователь может ввести буквы/пустую строку -> float() бросит ValueError.
    # Не даём упасть приложению, сообщаем в заголовке и оставляем прежнее значение.
    try:
        v = float(text.replace(",", "."))
    except ValueError:
        ax.set_title("Ошибка: введите число", color="red")
        fig.canvas.draw_idle()
        return
    ax.set_title("Цена и диапазон", color="black")
    _guard["updating"] = True
    try:
        # set_val программно ставит значение И вызывает on_changed (поэтому нужен флаг:
        # иначе on_slider снова обновит textbox).
        slider.set_val(min(max(v, 30), 90))
    finally:
        _guard["updating"] = False
    redraw()


def on_range(val):
    # RangeSlider.val - кортеж (min, max) двух ползунков. Применяем как границы X-зума.
    ax.set_xlim(*val)
    fig.canvas.draw_idle()


slider.on_changed(on_slider)
textbox.on_submit(on_submit)
rslider.on_changed(on_range)
# Blitting: при большом числе точек перерисовывать всю фигуру на каждый сдвиг дорого;
# blit кэширует статичный фон и обновляет только изменившуюся область (линия/диапазон).

if __name__ == "__main__":
    slider.set_val(75)
    print("textbox после slider:", textbox.text)
    on_submit("42,5")
    print("slider после textbox:", round(slider.val, 2))
    on_submit("abc")
    print("заголовок:", ax.get_title())
    on_submit("60")
    rslider.set_val((100, 200))
    print("xlim:", ax.get_xlim())
    fig.savefig(HERE / "45.png", dpi=120)
    plt.show()
