"""
Задача 46 (кириллица: FontManager, кэш и fallback). Автосалон готовит отчёт на русском, но на Windows без правильного шрифта вместо «Продажи по маркам» появляются «□□□□□□□□□□». Реализуйте def setup_cyrillic(fonts=("DejaVu Sans", "Liberation Sans", "Arial", "sans-serif")): plt.rcParams.update({"font.family": fonts, "axes.unicode_minus": False, "font.size": 12}). Проверьте доступность через {f.name for f in font_manager.fontManager.ttflist}. Установите свой корпоративный шрифт через font_manager.fontManager.addfont("/path/to/Corporate.ttf") и name = font_manager.FontProperties(fname="/path/to/Corporate.ttf").get_name(). Ожидаемый вывод: корректные буквы и −5 (а не □5) на осях. В комментариях объясните: почему fallback-цепочка важна (на разных ОС разные шрифты — Linux, macOS, Windows); как addfont регистрирует шрифт в Matplotlib (без него findfont его не найдёт); что делать, если DejaVu Sans «не виден» (_load_fontmanager(try_read_cache=False) — пересобрать кэш); почему axes.unicode_minus = False заменяет − (U+2212) на - (ASCII) — иногда единственный способ на старых шрифтах; как в Jupyter %matplotlib inline иногда «ломает» кириллицу (перезапустите ядро + plt.close("all")); как проверить, что шрифт содержит кириллицу (font_manager.findfont("Arial") и визуально открыть .ttf).
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager

HERE = Path(__file__).parent


def setup_cyrillic(fonts=("DejaVu Sans", "Liberation Sans", "Arial", "sans-serif")):
    # font.family принимает СПИСОК: Matplotlib идёт по нему слева направо и берёт первый
    # найденный шрифт. На Linux обычно есть DejaVu/Liberation, на Windows - Arial, на
    # macOS - Helvetica/Arial; цепочка делает один скрипт переносимым между ОС. С версии 3.6
    # при отсутствии глифа (например, кириллицы) fallback работает и по символам.
    # Оставляем только реально установленные шрифты (+ общие семейства вроде sans-serif),
    # иначе на каждый отсутствующий (например, Arial на Linux) идёт предупреждение findfont.
    have = {f.name for f in font_manager.fontManager.ttflist}
    generic = {"sans-serif", "serif", "monospace", "cursive", "fantasy"}
    fonts = [f for f in fonts if f in have or f in generic] or ["sans-serif"]
    plt.rcParams.update({"font.family": list(fonts),
                         # U+2212 (настоящий минус) есть не во всех шрифтах -> вместо него
                         # на старых шрифтах рисуется □. False => обычный дефис "-".
                         "axes.unicode_minus": False,
                         "font.size": 12})


def available(names):
    have = {f.name for f in font_manager.fontManager.ttflist}
    return {n: (n in have) for n in names}


def register_font(path):
    """Регистрирует свой .ttf: без addfont findfont его не увидит (он не лежит в системных
    каталогах, а менеджер шрифтов сканирует только их). Возвращает имя семейства."""
    path = Path(path)
    if not path.exists():
        print(f"[!] {path} не найден - корпоративный шрифт пропущен")
        return None
    font_manager.fontManager.addfont(str(path))
    return font_manager.FontProperties(fname=str(path)).get_name()


if __name__ == "__main__":
    print(available(["DejaVu Sans", "Liberation Sans", "Arial", "Corporate"]))
    # Если шрифт «не виден» (его установили после первого запуска, а кэш старый), кэш
    # можно пересобрать: font_manager._load_fontmanager(try_read_cache=False)
    # (приватный API) либо удалить файл fontlist-*.json из matplotlib.get_cachedir().
    corp = register_font(HERE / "Corporate.ttf")
    fonts = ("DejaVu Sans", "Liberation Sans", "Arial", "sans-serif")
    setup_cyrillic((corp, *fonts) if corp else fonts)
    print("Выбран файл шрифта:", font_manager.findfont("DejaVu Sans"))

    # Проверка, что шрифт содержит кириллицу: ищем глиф 'Ж' (U+0416) в cmap файла
    from matplotlib.ft2font import FT2Font
    f = FT2Font(font_manager.findfont(plt.rcParams["font.family"][0]))
    print("Кириллица есть:", 0x0416 in f.get_charmap())

    fig, ax = plt.subplots(figsize=(8, 5), layout="constrained")
    x = np.linspace(-5, 5, 50)
    ax.plot(x, x ** 2 - 5)
    ax.set(title="Продажи по маркам", xlabel="Отклонение", ylabel="Значение −5…")
    ax.grid(alpha=0.3)
    fig.savefig(HERE / "46.png", dpi=120)
    # Jupyter: если после %matplotlib inline вместо букв квадраты - шрифт выставлен ДО
    # смены бэкенда/кэша; перезапустите ядро, вызовите plt.close("all") и setup_cyrillic()
    # ПОСЛЕ %matplotlib inline.
    plt.close("all")
