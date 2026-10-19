import math


class Circle:
    ALLOWED_COLORS = {"red", "green", "blue", "yellow", "black", "white"}

    def __init__(self, radius, color="black"):
        self.__radius = None
        self.__color = None
        self.set_radius(radius)
        self.set_color(color)

    # --- радиус ---
    def get_radius(self):
        return self.__radius

    def set_radius(self, radius):
        if not isinstance(radius, (int, float)) or isinstance(radius, bool):
            raise TypeError("Радиус должен быть числом")
        if radius <= 0:
            raise ValueError("Радиус должен быть больше нуля")
        self.__radius = radius

    # --- цвет ---
    def get_color(self):
        return self.__color

    def set_color(self, color):
        if not isinstance(color, str):
            raise TypeError("Цвет должен быть строкой")
        color = color.strip().lower()
        if color not in self.ALLOWED_COLORS:
            raise ValueError(
                f"Недопустимый цвет '{color}'. "
                f"Доступные: {', '.join(sorted(self.ALLOWED_COLORS))}"
            )
        self.__color = color

    def get_area(self):
        return math.pi * self.__radius ** 2

    def __str__(self):
        return f"Circle(radius={self.__radius}, color={self.__color})"


# Пример использования
c = Circle(3, "red")
print(c)                        # Circle(radius=3, color=red)

c.set_radius(5)
c.set_color("Blue")
print(c)                        # Circle(radius=5, color=blue)
print(f"Площадь: {c.get_area():.2f}")  # Площадь: 78.54

# Проверка недопустимых значений
for action in (lambda: c.set_radius(-2),
               lambda: c.set_color("purple"),
               lambda: c.set_radius("abc")):
    try:
        action()
    except (ValueError, TypeError) as e:
        print("Ошибка:", e)

# Прямой доступ к приватному полю невозможен
try:
    print(c.__radius)
except AttributeError:
    print("Нет прямого доступа к __radius")