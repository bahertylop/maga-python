n = int(input("Введите двузначное число: "))

tens = n // 10
units = n % 10

result = units * 10 + tens

print("Результат:", result)