"""
Задача 38 (ROC, PR и калибровочная кривая).
Несбалансированная бинарная классификация: ROC, precision-recall и calibration.

Объяснения:
- TPR (recall) = доля найденных положительных; FPR = доля отрицательных, ошибочно названных положительными.
- PR-кривая информативнее ROC при дисбалансе, потому что фокусируется на позитивном классе.
- AUC=0.5 означает случайное ранжирование.
- Калибровка: точки ниже диагонали указывают на завышенные предсказанные вероятности.
- Average precision — агрегирование precision по изменяющимся порогам recall.
- При инверсии бинарных меток ROC-AUC может поменяться на 1-AUC, если инвертировать именно score/порядок классов.
"""
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_curve, roc_auc_score, precision_recall_curve, average_precision_score
from sklearn.calibration import calibration_curve

X, y = make_classification(n_samples=2500, n_features=10, weights=[0.95, 0.05],
                         random_state=38, flip_y=0.02)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3,
                                                    stratify=y, random_state=38)
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)
y_proba = model.predict_proba(X_test)[:, 1]

fig, axes = plt.subplots(1, 3, figsize=(15, 4.8), layout="constrained")
fpr, tpr, _ = roc_curve(y_test, y_proba)
auc = roc_auc_score(y_test, y_proba)
axes[0].plot(fpr, tpr, label=f"ROC AUC={auc:.3f}")
axes[0].plot([0, 1], [0, 1], "k--")
axes[0].set(xlabel="FPR", ylabel="TPR", title="ROC")
axes[0].legend()

precision, recall, _ = precision_recall_curve(y_test, y_proba)
ap = average_precision_score(y_test, y_proba)
axes[1].plot(recall, precision, label=f"AP={ap:.3f}")
axes[1].axhline(y_test.mean(), color="gray", linestyle="--", label="Baseline")
axes[1].set(xlabel="Recall", ylabel="Precision", title="Precision–Recall")
axes[1].legend()

prob_true, prob_pred = calibration_curve(y_test, y_proba, n_bins=10)
axes[2].plot(prob_pred, prob_true, marker="o", label="Модель")
axes[2].plot([0, 1], [0, 1], "k--", label="Идеальная калибровка")
axes[2].set(xlabel="Предсказанная вероятность", ylabel="Реальная доля", title="Calibration")
axes[2].legend()
plt.show()
