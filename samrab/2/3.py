a = float(input("a = "))
b = float(input("b = "))
c = float(input("c = "))

if a >= b >= c:
    a = a * 2
    b = b * 2
    c = c * 2
else:
    a = abs(a)
    b = abs(b)
    c = abs(c)

print(a, b, c)