def min(x):
    def min1(k):
        if k == len(x) - 1:
            return x[k]

        m = min1(k + 1)

        if x[k] < m:
            return x[k]
        else:
            return m

    return min1(0)


x = list(map(float, input("Введите элементы массива: ").split()))

print("Минимальный элемент:", min(x))