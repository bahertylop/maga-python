"""
Задача 57 (интерактивный EDA через RadioButtons). Автосалон хочет интерактивный инструмент для быстрого знакомства с данными клиентов: RadioButtons переключает признак (age, income, avg_check, credit_score), CheckButtons — показывать распределение по полу или общее, на графике — гистограмма. Реализуйте def draw(feature, show_sex): ax.cla(); if show_sex: for sex, g in df.groupby("gender"): ax.hist(g[feature].dropna(), alpha=0.5, label=sex, bins=20); ax.legend() else: ax.hist(df[feature].dropna(), bins=20); ax.set_title(feature); fig.canvas.draw_idle(). Привяжите через radio.on_clicked(lambda label: draw(label, check.get_status()[0])) и check.on_clicked(lambda label: draw(radio.value_selected, not check.get_status()[0])). Ожидаемый вывод: 2 виджета + интерактивная гистограмма. В комментариях объясните: зачем ax.cla() перед перерисовкой (иначе графики накладываются); как radio.value_selected даёт текущий выбор; почему draw_idle лучше draw (асинхронная перерисовка — не блокирует UI); как CheckButtons взаимодействует с draw (передаёт текущее состояние); что произойдёт без cla (графики накапливаются — визуальная каша); как добавить третий признак (например, hue по марке) через ещё одни CheckButtons.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.widgets import CheckButtons, RadioButtons

HERE = Path(__file__).parent
rng = np.random.default_rng(57)
n = 800
df = pd.DataFrame({
    "gender": rng.choice(["М", "Ж"], n),
    "age": rng.normal(38, 10, n).clip(18, 80),
    "income": rng.lognormal(11, 0.5, n),
    "avg_check": rng.normal(2.3e6, 6e5, n),
    "credit_score": rng.normal(650, 80, n).clip(300, 850),
})
FEATURES = ["age", "income", "avg_check", "credit_score"]

fig, ax = plt.subplots(figsize=(11, 6))
fig.subplots_adjust(left=0.25)
radio = RadioButtons(fig.add_axes([0.02, 0.5, 0.18, 0.3]), FEATURES)
check = CheckButtons(fig.add_axes([0.02, 0.25, 0.18, 0.15]), ["По полу"], [False])


def draw(feature, show_sex):
    # cla() очищает оси. Без него каждый вызов hist ДОРИСОВЫВАЕТ столбцы поверх старых:
    # графики накапливаются, масштаб и легенда превращаются в кашу.
    ax.cla()
    if show_sex:
        for sex, g in df.groupby("gender"):
            ax.hist(g[feature].dropna(), alpha=0.5, label=sex, bins=20)
        ax.legend()
    else:
        ax.hist(df[feature].dropna(), bins=20, color="C0")
    ax.set_title(feature)
    ax.grid(alpha=0.3)
    # draw_idle() - ОТЛОЖЕННАЯ перерисовка (в ближайший цикл событий): не блокирует UI и
    # объединяет серию быстрых вызовов в одну отрисовку. draw() рисует немедленно и синхронно.
    fig.canvas.draw_idle()


# В callback CheckButtons к моменту вызова состояние флажка УЖЕ переключено, поэтому
# get_status()[0] - это уже НОВОЕ значение. (Вариант из условия `not get_status()[0]`
# инвертировал бы его второй раз - гистограмма показывала бы обратное.)
# radio.value_selected - текущая выбранная метка (строка).
radio.on_clicked(lambda label: draw(label, check.get_status()[0]))
check.on_clicked(lambda label: draw(radio.value_selected, check.get_status()[0]))
draw(FEATURES[0], False)
# Третий переключатель (например, hue по марке): ещё один CheckButtons ["По марке"] -
# его состояние тоже передаётся в draw(feature, show_sex, show_brand), где groupby
# выбирается по "gender" или "brand".

if __name__ == "__main__":
    radio.set_active(2)                       # имитация клика: avg_check
    check.set_active(0)                       # включить «по полу»
    print("выбор:", radio.value_selected, "| по полу:", check.get_status()[0], "| серий:", len(ax.patches) // 20)
    fig.savefig(HERE / "57.png", dpi=120)
    plt.show()
