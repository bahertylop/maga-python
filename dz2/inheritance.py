import math
from abc import ABC, abstractmethod


class Shape(ABC):
    """Базовый класс для геометрических фигур."""

    @abstractmethod
    def getArea(self):
        """Возвращает площадь фигуры."""
        pass


class Circle(Shape):
    """Круг, заданный радиусом."""

    def __init__(self, radius):
        if radius < 0:
            raise ValueError("Радиус не может быть отрицательным")
        self.radius = radius

    def getArea(self):
        return math.pi * self.radius ** 2


circle = Circle(5)
print(f"Площадь круга с радиусом {circle.radius}: {circle.getArea():.2f}")