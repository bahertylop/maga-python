import math

x = int(input("Введите x:"))
y = int(input("Введите y:"))
z = int(input("Введите z:"))

w = (3 + math.e ** (y-1)) / (1 + x ** 2 * abs(y - math.tan(z)))

print(w)