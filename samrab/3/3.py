import math

eps = 10**-3

n = 0
a = 1
s = 0

while a >= eps:
    s += a
    n += 1
    a = 10**n / math.factorial(n)

print("Сумма:", s)