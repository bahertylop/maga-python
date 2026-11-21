"""
Задача 55 (Seaborn PairGrid и кастомизация). Автосалон анализирует данные клиентов (возраст, доход, средний чек, длительность владения предыдущим авто, кредитный рейтинг). sns.pairplot строит матрицу рассеяния для всех пар, но sns.PairGrid даёт полный контроль: разные типы для верхнего треугольника, нижнего и диагонали. Постройте sns.pairplot(iris, hue="species", corner=True, diag_kind="kde") — быстрый вариант, и g = sns.PairGrid(iris, hue="species", height=2.5); g.map_upper(sns.scatterplot, s=20, alpha=0.6); g.map_lower(sns.kdeplot, fill=True, alpha=0.4); g.map_diag(sns.histplot, kde=True); g.add_legend() — кастомный. Добавьте аннотацию через g.axes[0, 0].annotate("Верхний левый", xy=(5.5, 2.5), fontsize=9, color="red"). Ожидаемый вывод: две grid-визуализации. В комментариях объясните: чем pairplot отличается от PairGrid (первый — быстрый с дефолтами, второй — гибкий); что делают map_upper/map_lower/map_diag (разные функции для разных частей матрицы); как g.axes даёт доступ к Matplotlib-Axes для тонкой настройки (g.axes[0, 0].set_xlim(...)); когда pairplot слишком медленный (много признаков — corner=True убирает половину); как g.savefig("pairgrid.png", dpi=200, bbox_inches="tight") — сохраняет всю сетку; что произойдёт при 10+ признаках (матрица 10×10 — нечитаемо, берите топ-5 по важности).
"""
from pathlib import Path

import pandas as pd
import seaborn as sns

HERE = Path(__file__).parent


def load_iris():
    try:
        return sns.load_dataset("iris")
    except Exception:          # без сети: тот же датасет поставляется внутри scikit-learn
        from sklearn.datasets import load_iris as sk
        d = sk()
        df = pd.DataFrame(d.data, columns=["sepal_length", "sepal_width", "petal_length", "petal_width"])
        df["species"] = pd.Categorical.from_codes(d.target, d.target_names)
        return df


iris = load_iris()
sns.set_theme(style="ticks")

# pairplot - БЫСТРЫЙ вариант: готовая обёртка с дефолтами (scatter вне диагонали, hist/kde
# на диагонали). corner=True рисует только нижний треугольник (половина осей - быстрее
# и без дублей, т.к. матрица симметрична).
g1 = sns.pairplot(iris, hue="species", corner=True, diag_kind="kde")
g1.savefig(HERE / "55_pairplot.png", dpi=150, bbox_inches="tight")

# PairGrid - ГИБКИЙ вариант: сетка создаётся пустой, а вы сами выбираете, что рисовать:
g = sns.PairGrid(iris, hue="species", height=2.5)
g.map_upper(sns.scatterplot, s=20, alpha=0.6)      # выше диагонали - точки
g.map_lower(sns.kdeplot, fill=True, alpha=0.4)     # ниже диагонали - плотность
g.map_diag(sns.histplot, kde=True)                 # на диагонали - гистограммы + KDE
g.add_legend()
# g.axes - 2D-массив обычных matplotlib Axes: доступна любая тонкая настройка
# (set_xlim, annotate, axhline...). Здесь - аннотация и пределы в ячейке [0, 0].
g.axes[0, 0].annotate("Верхний левый", xy=(5.5, 2.5), fontsize=9, color="red")
g.axes[0, 1].set_xlim(1.5, 5)
# g.savefig сохраняет ВСЮ сетку (это фигура PairGrid); bbox_inches="tight" не обрежет легенду.
g.savefig(HERE / "55_pairgrid.png", dpi=200, bbox_inches="tight")

# Когда pairplot слишком медленный/нечитаемый: n признаков -> n*n осей (10 признаков = 100
# осей, kde в каждой - очень долго). Тогда corner=True (нужно ~n²/2), vars=[...] - только
# важные признаки (топ-5 по важности/корреляции с целью), либо sample() от данных.
print("оси:", g.axes.shape)
