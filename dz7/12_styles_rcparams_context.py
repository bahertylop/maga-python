"""Задача 12. Временные стили, rcParams и сброс параметров."""
from contextlib import contextmanager
import matplotlib as mpl
import matplotlib.pyplot as plt
@contextmanager
def style_ctx(name):
    with plt.style.context(name):
        yield
x = [1, 2, 3, 4, 5]
y = [10, 13, 11, 17, 15]
with style_ctx("ggplot"):
    fig1, ax1 = plt.subplots()
    ax1.plot(x, y, marker="o")
    ax1.set_title("Стиль ggplot")
with style_ctx("seaborn-v0_8-darkgrid"):
    fig2, ax2 = plt.subplots()
    ax2.plot(x, y, marker="s")
    ax2.set_title("Darkgrid")
plt.rcParams.update({"font.size": 12, "axes.grid": True, "grid.alpha": .3})
fig3, ax3 = plt.subplots()
ax3.plot(x, y)
ax3.set_title("После rcParams")
mpl.rcdefaults()  # Полный возврат к параметрам по умолчанию.
fig4, ax4 = plt.subplots()
ax4.plot(x, y)
ax4.set_title("После rcdefaults")
# plt.style.use меняет стиль глобально; plt.style.context временно — настройки откатываются
# после блока, особенно удобно в ноутбуках и при генерации разных отчётов подряд.
# rcParams — централизованные параметры визуального оформления Matplotlib.
# Стили применяются по порядку: в списке поздний стиль перекрывает конфликтующие параметры.
# plt.style.use('default') возвращает стиль, но не всегда сбрасывает вручную изменённые rcParams;
# mpl.rcdefaults() сбрасывает к базовым настройкам библиотеки.
# Пользовательские .mplstyle обычно кладут в ~/.config/matplotlib/stylelib/ (путь может
# отличаться в зависимости от ОС); файл можно применить по пути или имени после установки.
# plt.style.available возвращает доступные стили; print(plt.style.available) их перечислит.
print("Available styles:", plt.style.available)
plt.show()
