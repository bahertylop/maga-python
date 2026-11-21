"""
Задача 54 (LearningCurveAnalyzer — автоматическая диагностика). Автосалон обучает модели прогноза покупки для 5 марок и хочет автоматически получать диагноз «переобучение / недообучение / хорошо». Кривые обучения мощны, но интерпретировать их вручную утомительно. Реализуйте class LearningCurveAnalyzer с методами fit() (вызывает learning_curve и сохраняет train_mean, val_mean, train_std, val_std), diagnose() -> str (пороги: gap = train_mean[-1] - val_mean[-1] > 0.1 → overfitting; val_mean[-1] < 0.7 → underfitting; иначе good), plot(ax=None) (рисует с fill_between), compare(others: list) (сравнивает несколько моделей на одной фигуре). Обучите три модели, сравните, постройте три learning curves с диагнозами в заголовках. Ожидаемый вывод: 3 графика с диагнозами. В комментариях объясните: зачем diagnose (автоматизация — не нужно каждый раз смотреть на график); как пороги gap > 0.1 и val_mean < 0.7 определяют диагноз (эмпирические — зависят от задачи); зачем fit() возвращает self (fluent API — LearningCurveAnalyzer(...).fit().plot()); как логировать результаты в pd.DataFrame для отчёта (pd.DataFrame({"model": ..., "diagnosis": ..., "val_mean": ...})); как связать с ML-дашбордом (задача 56) — learning curves как дополнение к метрикам; когда compare полезнее одиночного plot (сравнение моделей одной серии).
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import learning_curve
from sklearn.tree import DecisionTreeClassifier

HERE = Path(__file__).parent


class LearningCurveAnalyzer:
    def __init__(self, model, X, y, name=None, cv=5, scoring="accuracy"):
        self.model, self.X, self.y, self.cv, self.scoring = model, X, y, cv, scoring
        self.name = name or type(model).__name__

    def fit(self):
        self.sizes, tr, va = learning_curve(self.model, self.X, self.y, cv=self.cv, scoring=self.scoring,
                                            train_sizes=np.linspace(0.1, 1.0, 8), n_jobs=1, shuffle=True,
                                            random_state=42)
        self.train_mean, self.train_std = tr.mean(axis=1), tr.std(axis=1)
        self.val_mean, self.val_std = va.mean(axis=1), va.std(axis=1)
        # return self: fluent API - LearningCurveAnalyzer(...).fit().plot() одной цепочкой
        return self

    # Пороги ЭМПИРИЧЕСКИЕ: gap > 0.1 (разрыв train-val) = модель «запомнила» обучающие
    # данные; val < 0.7 = даже на валидации плохо (модель слишком проста). Для другой
    # задачи/метрики (F1, редкий класс) границы подбирают под предметную область.
    # Порядок проверок важен: сначала переобучение, затем недообучение.
    def diagnose(self, gap_thr=0.1, val_thr=0.7) -> str:
        gap = self.train_mean[-1] - self.val_mean[-1]
        if gap > gap_thr:
            return "overfitting"
        if self.val_mean[-1] < val_thr:
            return "underfitting"
        return "good"

    def plot(self, ax=None):
        ax = ax or plt.subplots(figsize=(6, 4))[1]
        for mean, std, label, c in ((self.train_mean, self.train_std, "train", "C0"),
                                    (self.val_mean, self.val_std, "validation", "C1")):
            ax.plot(self.sizes, mean, "o-", color=c, label=label)
            ax.fill_between(self.sizes, mean - std, mean + std, alpha=0.2, color=c)
        ax.set(title=f"{self.name}: {self.diagnose()}", xlabel="Размер обучающей выборки", ylabel=self.scoring)
        ax.legend(loc="lower right")
        ax.grid(alpha=0.3)
        return ax

    def compare(self, others):
        # Все модели на ОДНОЙ оси - валидационные кривые рядом (удобно выбрать лучшую)
        fig, ax = plt.subplots(figsize=(8, 5), layout="constrained")
        for a in [self, *others]:
            ax.plot(a.sizes, a.val_mean, "o-", label=f"{a.name} ({a.diagnose()})")
        ax.set(title="Сравнение моделей (validation)", xlabel="Размер выборки", ylabel=self.scoring)
        ax.legend()
        ax.grid(alpha=0.3)
        return fig

    def summary(self):
        return {"model": self.name, "diagnosis": self.diagnose(), "train": self.train_mean[-1], "val_mean": self.val_mean[-1]}


if __name__ == "__main__":
    X, y = make_classification(n_samples=1000, n_features=20, n_informative=5, flip_y=0.15, random_state=42)
    an = [LearningCurveAnalyzer(DecisionTreeClassifier(random_state=0), X, y, "Tree(глубокое)").fit(),
          LearningCurveAnalyzer(DecisionTreeClassifier(max_depth=1, random_state=0), X, y, "Tree(depth=1)").fit(),
          LearningCurveAnalyzer(LogisticRegression(max_iter=1000, C=0.5), X, y, "LogReg").fit()]
    fig, axes = plt.subplots(1, 3, figsize=(17, 4.5), layout="constrained")
    for a, ax in zip(an, axes):
        a.plot(ax)
    fig.savefig(HERE / "54.png", dpi=130)
    an[0].compare(an[1:]).savefig(HERE / "54_compare.png", dpi=130)
    # Лог результатов для отчёта - DataFrame
    print(pd.DataFrame([a.summary() for a in an]).round(3).to_string(index=False))
    # Связь с дашбордом (задача 56): кривые обучения дополняют метрики confusion/ROC/PR -
    # показывают, поможет ли ДОБАВЛЕНИЕ данных (val ещё растёт) или нужна другая модель.
    # compare полезнее одиночного plot, когда выбираем между моделями одной серии на тех же данных.
