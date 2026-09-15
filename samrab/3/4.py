n = int(input("N = "))

product = 1

for i in range(n):
    x = float(input())

    fractional = x - int(x)

    print(f"{fractional:.6f}")

    product *= fractional

print("Произведение:", product)