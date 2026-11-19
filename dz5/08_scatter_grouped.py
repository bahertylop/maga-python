"""Задача 8. Scatterplot с группировкой по кузову (hue вручную)."""
import pandas as pd
import matplotlib.pyplot as plt
# Для запуска без исходного CSV используем небольшой демонстрационный набор.
if __import__('pathlib').Path("cars.csv").exists():
    df = pd.read_csv("cars.csv")
else:
    df = pd.DataFrame({"body_type": ["Sedan", "SUV", "Hatchback", "Coupe", "Wagon"]*4,
                      "horsepower": [110, 180, 90, 220, 140, 130, 200, 100, 240, 150, 120, 190, 95, 230, 145, 125, 210, 105, 250, 160],
                      "price": [1.2, 2.5, .9, 3.1, 1.8, 1.5, 2.8, 1.0, 3.4, 2.0, 1.3, 2.6, .95, 3.3, 1.9, 1.4, 2.9, 1.1, 3.6, 2.2]})
fig, ax = plt.subplots(layout="constrained")
for body, g in df.groupby("body_type"):
    # dropna синхронно удаляет строки, где horsepower или price пропущены
    g = g.dropna(subset=["horsepower", "price"])
    ax.scatter(g["horsepower"], g["price"], label=body, s=50, alpha=.7, edgecolors="black")
ax.set(xlabel="Мощность (л.с.)", ylabel="Цена (млн ₽)", title="Мощность и цена по типу кузова")
ax.legend(title="Кузов")
# plot соединяет точки линией; scatter — независимые точки, размеры/цвет можно варьировать.
# s — площадь маркера в pt², не диаметр. Для удвоения диаметра s увеличивают в 4 раза.
# alpha снижает визуальную плотность при наложении; чёрная обводка отделяет маркеры от фона.
# На тёмном фоне может быть лучше белая обводка. groupby — срез по каждому body_type.
# Пропуски лучше удалить совместно по x и y: несинхронные удаления могут дать разные длины.
plt.show()
