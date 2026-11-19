"""
Задача 40 (training curves и early stopping).
Смоделировать 50 эпох train/validation loss и accuracy; отметить лучшую эпоху.

Объяснения:
- Train loss падает, validation loss после некоторого момента может расти: переобучение.
- Early stopping прекращает обучение при отсутствии улучшения validation-метрики,
  и сохраняет веса на лучшей эпохе.
- argmin даёт индекс минимума; +1 переводит индекс (с нуля) в номер эпохи (с единицы).
- При нестабильном/взрывающемся loss проверьте learning rate, нормализацию и регуляризацию.
- history удобен для накопления метрик и построения графиков после обучения.
- np.argmin пустого массива вызывает ValueError.
"""
import numpy as np
import matplotlib.pyplot as plt

rng = np.random.default_rng(40)
epochs = np.arange(1, 51)
train_loss = 1.5*np.exp(-epochs/15) + 0.1 + rng.normal(0, 0.02, 50)
val_loss = 1.5*np.exp(-epochs/15) + 0.15 + rng.normal(0, 0.03, 50)
val_loss[25:] += (epochs[25:] - 25) * 0.01
best_epoch = int(np.argmin(val_loss) + 1)

fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), layout="constrained")
axes[0].plot(epochs, train_loss, label="Train loss")
axes[0].plot(epochs, val_loss, label="Validation loss")
axes[0].axvline(best_epoch, color="green", linestyle="--", label=f"Best = {best_epoch}")
axes[0].annotate("Начало переобучения", xy=(best_epoch, val_loss[best_epoch-1]),
                 xytext=(best_epoch+5, val_loss[best_epoch-1]+0.3),
                 arrowprops=dict(arrowstyle="->", color="green"))
axes[0].set(xlabel="Эпоха", ylabel="Loss", title="Loss")
axes[0].legend()

axes[1].plot(epochs, 1-train_loss/2, label="Train accuracy (условная)")
axes[1].plot(epochs, 1-val_loss/2, label="Validation accuracy (условная)")
axes[1].set(xlabel="Эпоха", ylabel="Accuracy", title="Accuracy")
axes[1].legend()
plt.show()
