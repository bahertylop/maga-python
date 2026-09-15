n = int(input("Введите размер матриц: "))

A = []
B = []
C = []

print("Введите матрицу A:")
for i in range(n):
    A.append(list(map(float, input().split())))

print("Введите матрицу B:")
for i in range(n):
    B.append(list(map(float, input().split())))

print("Введите матрицу C:")
for i in range(n):
    C.append(list(map(float, input().split())))


def norm(matrix):
    maximum = 0

    for row in matrix:
        for element in row:
            if abs(element) > maximum:
                maximum = abs(element)

    return maximum


norm_A = norm(A)
norm_B = norm(B)
norm_C = norm(C)

if norm_A <= norm_B and norm_A <= norm_C:
    print("Матрица A:")
    for row in A:
        print(row)
elif norm_B <= norm_A and norm_B <= norm_C:
    print("Матрица B:")
    for row in B:
        print(row)
else:
    print("Матрица C:")
    for row in C:
        print(row)