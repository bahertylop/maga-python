"""
Задача 47 (собственный .mplstyle и комбинирование). Автосалон хочет, чтобы все отчёты выглядели в фирменном стиле (синий цвет бренда, шрифт DejaVu Sans, без верхней и правой рамки). Создайте report.mplstyle с настройками: figure.figsize: 10, 6, font.family: DejaVu Sans, axes.titlesize: 14, axes.spines.top: False, axes.spines.right: False, axes.grid: True, grid.alpha: 0.4, legend.fontsize: 11, axes.unicode_minus: False, axes.prop_cycle: cycler('color', ['#1f77b4', '#ff7f0e', ...]) (фирменные цвета). Загрузите plt.style.use(["seaborn-v0_8", "report.mplstyle"]). Дополнительно создайте dark.mplstyle с figure.facecolor: black, axes.facecolor: black, text.color: white. Постройте три графика в трёх стилях. Ожидаемый вывод: 3 разных внешних вида. В комментариях объясните: как .mplstyle работает с plt.style.use (парсит файл и применяет к rcParams); зачем порядок в списке (второй стиль переопределяет первый); как положить стиль в ~/.config/matplotlib/stylelib/ для загрузки по имени (plt.style.use("report")); как комбинировать с rc_context для временного применения; что произойдёт при ошибке в .mplstyle (ValueError: Invalid rcparameter — отладить через plt.style.use("default") + mpl.rcdefaults()); как использовать axes.prop_cycle для автоматической палитры бренда.
"""
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).parent

# Файлы стилей создаём рядом со скриптом. Формат: «ключ: значение», # - комментарий.
(HERE / "report.mplstyle").write_text("""\
# Фирменный стиль автосалона
figure.figsize: 10, 6
font.family: DejaVu Sans
axes.titlesize: 14
axes.spines.top: False
axes.spines.right: False
axes.grid: True
grid.alpha: 0.4
legend.fontsize: 11
axes.unicode_minus: False
# prop_cycle - автоматическая палитра: n-я линия без явного color получает n-й цвет бренда.
# ВАЖНО: в .mplstyle символ '#' начинает комментарий, поэтому hex-цвета пишем БЕЗ '#'.
axes.prop_cycle: cycler('color', ['0b5cad', 'ff7f0e', '2ca02c', 'd62728', '9467bd'])
""", encoding="utf-8")

(HERE / "dark.mplstyle").write_text("""\
figure.facecolor: black
axes.facecolor: black
savefig.facecolor: black
text.color: white
axes.labelcolor: white
axes.edgecolor: white
xtick.color: white
ytick.color: white
grid.color: gray
""", encoding="utf-8")

x = np.linspace(0, 10, 100)


def demo(title):
    fig, ax = plt.subplots()
    for k in range(4):
        ax.plot(x, np.sin(x + k) + k * 0.3, label=f"Марка {k + 1}")   # цвета - из prop_cycle
    ax.set(title=title, xlabel="Время", ylabel="Значение")
    ax.legend()
    return fig


# plt.style.use парсит файл и записывает значения в mpl.rcParams (глобально).
# Порядок в списке важен: стили применяются слева направо, и ПОЗДНИЙ переопределяет
# ранний. Здесь report.mplstyle идёт после seaborn и перебивает его палитру/рамки.
# Чтобы вызывать по имени plt.style.use("report"), положите файл в
# <конфиг matplotlib>/stylelib/report.mplstyle (путь: mpl.get_configdir()).
plt.style.use(["seaborn-v0_8", str(HERE / "report.mplstyle")])
demo("1. seaborn-v0_8 + report").savefig(HERE / "47_report.png", dpi=110)

# rc_context - ВРЕМЕННОЕ применение: настройки действуют только внутри with, потом
# rcParams возвращаются как были (удобно для одного графика в чужом процессе/ноутбуке).
with plt.style.context(str(HERE / "dark.mplstyle")):
    demo("2. dark (через style.context)").savefig(HERE / "47_dark.png", dpi=110)
with mpl.rc_context({"axes.prop_cycle": mpl.cycler(color=["crimson", "gold"]), "lines.linewidth": 3}):
    demo("3. rc_context: точечная правка").savefig(HERE / "47_rc.png", dpi=110)

# Ошибка в .mplstyle: в Matplotlib 3.x невалидная строка даёт предупреждение «Bad value in file ...» (Matplotlib
# пропускает строку; в старых версиях/в rcParams[...] = ... - ValueError: Key ... Отладка: сбросить
# состояние (plt.style.use("default"); mpl.rcdefaults()) и подключать строки по одной.
(HERE / "bad.mplstyle").write_text("axes.grid: maybe\n")
try:
    plt.style.use(str(HERE / "bad.mplstyle"))
except Exception as e:
    print("Ошибка в стиле:", type(e).__name__)
finally:
    plt.style.use("default")
    mpl.rcdefaults()
    (HERE / "bad.mplstyle").unlink()
print("Файлы:", *(p.name for p in HERE.glob("47_*.png")))
