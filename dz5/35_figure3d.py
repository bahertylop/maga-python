"""
Задача 35 (Figure3D — класс-обёртка для 3D).
Реализовать helix(n), cloud(n), view(elev, azim); показать спираль и облако.

Объяснения:
- Обёртка объединяет создание 3D-осей и методы визуализации, упрощает повторное использование.
- projection='3d' создаёт Axes3D, расширяющий обычные Axes.
- elev — угол подъёма, azim — азимутальный поворот камеры.
- depthshade=True (дефолт scatter) затеняет точки с учётом глубины.
- 3D хуже читается из-за перспективы и перекрытия; полезно дополнять 2D проекциями.
- PNG сохраняет только статичный выбранный ракурс, вращение доступно в интерактивном окне.
"""
import numpy as np
import matplotlib.pyplot as plt

class Figure3D:
    def __init__(self):
        self.fig = plt.figure(figsize=(9, 7))
        self.ax = self.fig.add_subplot(111, projection="3d")

    def helix(self, n=200):
        t = np.linspace(0, 8*np.pi, n)
        self.ax.plot(np.cos(t), np.sin(t), t, label="Спираль")
        return self

    def cloud(self, n=500):
        rng = np.random.default_rng(35)
        x, y, z = rng.normal(size=(3, n))
        self.ax.scatter(x, y, z, c=z, cmap="viridis", s=20, depthshade=True, label="Облако")
        return self

    def view(self, elev=30, azim=-60):
        self.ax.view_init(elev=elev, azim=azim)
        return self

scene = Figure3D().helix().cloud().view(20, -45)
scene.ax.set_xlabel("X")
scene.ax.set_ylabel("Y")
scene.ax.set_zlabel("Z")
scene.ax.legend()
plt.show()
