def sum_min_max(a, b, c):
    return min(a, b, c) + max(a, b, c)


a = float(input("a = "))
b = float(input("b = "))
c = float(input("c = "))

result = sum_min_max(a, b, c)

print("Сумма:", result)