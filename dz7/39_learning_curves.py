"""
Задача 39 (learning curves и диагностика переобучения).
Сравнить DecisionTree(max_depth=3), DecisionTree(max_depth=20), RandomForest.

Объяснения:
- Переобучение: train score высок, validation ниже, gap большой.
- Недообучение: обе кривые низкие — модель слишком простая/признаки недостаточны.
- Хорошая модель: кривые близки и высоки.
- Заливка mean±std показывает разброс качества между CV-фолдами.
- Если обе кривые ещё растут, дополнительная выборка может помочь.
- train_sizes=[1.0] даст одну точку; тренд не виден.
- CV=5 — компромисс между оценкой стабильности и затратами.
"""
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_classification
from sklearn.model_selection import learning_curve
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

X, y = make_classification(n_samples=1000, n_features=12, n_informative=7,
                         n_redundant=2, random_state=39)
models = {
    "Tree depth=3 (underfit)": DecisionTreeClassifier(max_depth=3, random_state=39),
    "Tree depth=20 (overfit)": DecisionTreeClassifier(max_depth=20, random_state=39),
    "RandomForest": RandomForestClassifier(n_estimators=120, random_state=39),
}
sizes = np.linspace(0.1, 1.0, 10)
fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), layout="constrained")
for ax, (name, model) in zip(axes, models.items()):
    n, train_scores, val_scores = learning_curve(model, X, y, train_sizes=sizes,
        cv=5, scoring="accuracy", n_jobs=-1)
    tr_mean, tr_std = train_scores.mean(axis=1), train_scores.std(axis=1)
    va_mean, va_std = val_scores.mean(axis=1), val_scores.std(axis=1)
    ax.plot(n, tr_mean, marker="o", label="Train")
    ax.fill_between(n, tr_mean-tr_std, tr_mean+tr_std, alpha=0.15)
    ax.plot(n, va_mean, marker="o", label="Validation")
    ax.fill_between(n, va_mean-va_std, va_mean+va_std, alpha=0.15)
    ax.set_title(name)
    ax.set_xlabel("Размер train")
    ax.set_ylabel("Accuracy")
    ax.legend()
plt.show()
