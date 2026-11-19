"""
Задача 41 (Feature importance: MDI vs permutation).
RandomForest, встроенная MDI и permutation importance, два barh.

Объяснения:
- MDI основана на уменьшении impurity в узлах дерева; permutation — падение метрики
  на отложенных данных после случайного перемешивания столбца.
- n_repeats=10 усредняет эффект нескольких перемешиваний.
- barh удобен для длинных названий признаков.
- Importance 0.15 не означает +15% accuracy; это относительная оценка вклада.
- Цветовой градиент Viridis отображает относительную величину важности.
- Дополнительные методы: SHAP; permutation importance можно считать с scoring='roc_auc'.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.inspection import permutation_importance

X, y = make_classification(n_samples=1200, n_features=8, n_informative=5,
                         n_redundant=1, random_state=41)
names = ["возраст", "средний_чек_за_год", "стаж", "регион", "число_визитов",
         "тип_клиента", "рекламный_канал", "скидка"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25,
                                                    random_state=41, stratify=y)
model = RandomForestClassifier(n_estimators=150, random_state=41)
model.fit(X_train, y_train)
mdi = pd.Series(model.feature_importances_, index=names).sort_values()
perm_result = permutation_importance(model, X_test, y_test, n_repeats=10,
                                     random_state=41, scoring="accuracy")
perm = pd.Series(perm_result.importances_mean, index=names).sort_values()

fig, axes = plt.subplots(1, 2, figsize=(13, 5), layout="constrained")
for ax, series, title in [(axes[0], mdi, "MDI"), (axes[1], perm, "Permutation")]:
    values = series.values
    vmax = max(values.max(), 1e-12)
    ax.barh(series.index, values, color=plt.cm.viridis(values/vmax))
    ax.set_title(title)
    ax.set_xlabel("Importance")
plt.show()
