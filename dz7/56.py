"""
Задача 56 (MLDashboard — комплексный ML-дашборд). Автосалон обучает модель прогноза покупки и хочет «одностраничный отчёт» для руководства: confusion matrix, ROC, PR, feature importance. Реализуйте class MLDashboard с методами _confusion(ax), _roc(ax), _pr(ax), _importance(ax) и build() (создаёт fig, axes = plt.subplots(2, 2, figsize=(14, 10), layout="constrained"), вызывает все 4 метода, добавляет fig.suptitle(f"ML Dashboard: {type(self.model).__name__}")). Соберите дашборд, сохраните в ml_dashboard.png с dpi=300 и bbox_inches="tight". Ожидаемый вывод: 4 графика на одной фигуре. В комментариях объясните: как приватные методы (_confusion) организуют код (каждый метод — одна ответственность); как suptitle не обрезается благодаря bbox_inches="tight"; как расширить (_calibration, _lift, _learning_curve); как dataclass DashboardConfig улучшил бы API (цвета, размеры шрифтов, dpi); когда такой класс — овер-инжиниринг (для одноразового скрипта проще 4 раза plt.subplots); как логировать дашборд в MLflow (сохранять в mlflow.log_artifact("ml_dashboard.png")).
"""
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (ConfusionMatrixDisplay, PrecisionRecallDisplay, RocCurveDisplay,
                             average_precision_score, roc_auc_score)
from sklearn.model_selection import train_test_split

HERE = Path(__file__).parent


@dataclass
class DashboardConfig:
    """Конфиг сделал бы API гибче: цвета, шрифты, dpi, размер - в одном объекте, а не в
    разбросанных константах и **kwargs методов."""
    figsize: tuple = (14, 10)
    dpi: int = 300
    color: str = "tab:blue"


class MLDashboard:
    def __init__(self, model, X_test, y_test, feature_names, config=DashboardConfig()):
        self.model, self.X, self.y, self.names, self.cfg = model, X_test, y_test, feature_names, config
        self.proba = model.predict_proba(X_test)[:, 1]
        self.pred = model.predict(X_test)

    # Каждый приватный метод = ОДНА ответственность: нарисовать одну панель на переданной
    # оси. Их легко читать, тестировать по отдельности, менять местами и расширять.
    def _confusion(self, ax):
        ConfusionMatrixDisplay.from_predictions(self.y, self.pred, ax=ax, cmap="Blues", colorbar=False)
        ax.set_title("Confusion matrix")

    def _roc(self, ax):
        RocCurveDisplay.from_predictions(self.y, self.proba, ax=ax, name=f"AUC={roc_auc_score(self.y, self.proba):.3f}")
        ax.plot([0, 1], [0, 1], "k--", alpha=0.5)
        ax.set_title("ROC")

    def _pr(self, ax):
        PrecisionRecallDisplay.from_predictions(self.y, self.proba, ax=ax,
                                                name=f"AP={average_precision_score(self.y, self.proba):.3f}")
        ax.set_title("Precision-Recall")

    def _importance(self, ax):
        imp = self.model.feature_importances_
        order = np.argsort(imp)[-10:]                       # топ-10 признаков
        ax.barh(np.array(self.names)[order], imp[order], color=self.cfg.color)
        ax.set_title("Feature importance (топ-10)")

    # Расширение: _calibration (calibration_curve), _lift (кумулятивный выигрыш),
    # _learning_curve (см. задачу 54) - достаточно добавить метод и вызвать его в build().
    def build(self):
        fig, axes = plt.subplots(2, 2, figsize=self.cfg.figsize, layout="constrained")
        self._confusion(axes[0, 0]); self._roc(axes[0, 1]); self._pr(axes[1, 0]); self._importance(axes[1, 1])
        fig.suptitle(f"ML Dashboard: {type(self.model).__name__}", fontsize=16)
        return fig


if __name__ == "__main__":
    X, y = make_classification(n_samples=2000, n_features=15, n_informative=6, flip_y=0.05, random_state=42)
    names = [f"feature_{i}" for i in range(15)]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
    model = RandomForestClassifier(n_estimators=150, random_state=42).fit(Xtr, ytr)
    fig = MLDashboard(model, Xte, yte, names).build()
    # bbox_inches="tight" обрезает холст по реальному содержимому (включая suptitle и
    # подписи, вышедшие за поля), поэтому заголовок не режется
    fig.savefig(HERE / "ml_dashboard.png", dpi=300, bbox_inches="tight")
    print("saved ml_dashboard.png")
    # MLflow: после обучения  mlflow.log_artifact("ml_dashboard.png")  внутри with mlflow.start_run():
    # Овер-инжиниринг: для одноразового ноутбука хватит 4 вызовов Display.from_predictions на subplots.
