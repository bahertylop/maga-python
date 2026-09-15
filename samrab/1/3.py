import math

a = float(input("Введите первое число: "))
b = float(input("Введите второе число: "))

arithmetic_mean = (a ** 3 + b ** 3) / 2
geometric_mean = math.sqrt(abs(a) * abs(b))

print("Среднее арифметическое кубов:", arithmetic_mean)
print("Среднее геометрическое модулей:", geometric_mean)