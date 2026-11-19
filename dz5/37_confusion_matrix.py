"""
Задача 37 (confusion matrix).
Построить абсолютную и нормированную матрицы ошибок для трёх классов.

Объяснения:
- Строки — реальные классы, столбцы — предсказанные.
- Нормировка по строкам позволяет сравнивать классы при дисбалансе.
- ax.text(j, i): x соответствует столбцу, y — строке imshow.
- Диагональ — корректные классификации.
- При большом количестве классов подписи перегружают график; можно оставить цветовую карту.
"""
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, accuracy_score, f1_score

rng = np.random.default_rng(37)
y_test = rng.choice([0, 1, 2], size=240, p=[0.5, 0.3, 0.2])
y_pred = y_test.copy()
noise = rng.random(len(y_pred)) < 0.22
y_pred[noise] = rng.choice([0, 1, 2], size=noise.sum())
labels = ["Купит", "Не купит", "Отложит"]
cm = confusion_matrix(y_test, y_pred, labels=[0, 1, 2])
cm_norm = cm.astype(float) / np.maximum(cm.sum(axis=1, keepdims=True), 1)

fig, axes = plt.subplots(1, 2, figsize=(12, 5), layout="constrained")
for ax, matrix, title, fmt in zip(axes, [cm, cm_norm], ["Абсолютная", "Нормированная"], ["d", ".2f"]):
    im = ax.imshow(matrix, cmap="Blues")
    ax.set_xticks(range(3), labels=labels, rotation=30, ha="right")
    ax.set_yticks(range(3), labels=labels)
    ax.set_xlabel("Предсказание")
    ax.set_ylabel("Истина")
    ax.set_title(title)
    for i, j in np.ndindex(matrix.shape):
        value = format(matrix[i, j], fmt)
        color = "white" if matrix[i, j] > matrix.max()/2 else "black"
        ax.text(j, i, value, ha="center", va="center", color=color)
    fig.colorbar(im, ax=ax)
fig.suptitle(f"Acc={accuracy_score(y_test, y_pred):.2f}, F1={f1_score(y_test, y_pred, average='macro'):.2f}")
plt.show()
