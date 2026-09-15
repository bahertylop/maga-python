import math

r = float(input("Радиус круга = "))
a = float(input("Сторона квадрата = "))

circle_area = math.pi * r ** 2
square_area = a ** 2

if circle_area > square_area:
    print("Площадь круга больше")
elif square_area > circle_area:
    print("Площадь квадрата больше")
else:
    print("Площади равны")