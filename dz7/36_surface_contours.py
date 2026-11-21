"""
Задача 36 (3D-поверхность и проекции контуров).
Построить Z=sin(sqrt(X²+Y²)); контуры на нижнюю плоскость и боковую стену.

Объяснения:
- antialiased=True сглаживает визуальные границы полигонов.
- rstride/cstride задают шаг сетки поверхности; увеличение шага уменьшает число полигонов
  и ускоряет рендеринг, но снижает детализацию.
- zdir выбирает направление проекции, offset — координату плоскости проекции.
- box aspect (1,1,0.6) делает вертикальную ось визуально менее вытянутой.
- Сетка 1000x1000 слишком тяжела для интерактивной отрисовки; уменьшайте плотность.
- Поверхность передаёт форму, контуры помогают сравнивать значения.
"""
import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(-5, 5, 120)
y = np.linspace(-5, 5, 120)
X, Y = np.meshgrid(x, y)
Z = np.sin(np.sqrt(X**2 + Y**2))

fig = plt.figure(figsize=(13, 6), layout="constrained")
ax1 = fig.add_subplot(121, projection="3d")
surf1 = ax1.plot_surface(X, Y, Z, cmap="viridis", linewidth=0, antialiased=True,
                        rstride=2, cstride=2, alpha=0.9)
ax1.contour(X, Y, Z, zdir="z", offset=-1.5, levels=15, cmap="viridis")
ax1.set_zlim(-1.5, 1)
ax1.set_title("Контуры на нижней плоскости")
ax1.set_box_aspect((1, 1, 0.6))

ax2 = fig.add_subplot(122, projection="3d")
ax2.plot_surface(X, Y, Z, cmap="viridis", linewidth=0, antialiased=True,
                rstride=2, cstride=2, alpha=0.9)
ax2.contour(X, Y, Z, zdir="x", offset=-5, levels=15, cmap="viridis")
ax2.set_xlim(-5, 5)
ax2.set_title("Контуры на боковой стене")
ax2.set_box_aspect((1, 1, 0.6))
plt.show()
