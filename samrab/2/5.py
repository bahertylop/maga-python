k = int(input("k = "))
d = int(input("d = "))

day = (d + k - 2) % 7 + 1

if day == 1:
    print("Понедельник")
elif day == 2:
    print("Вторник")
elif day == 3:
    print("Среда")
elif day == 4:
    print("Четверг")
elif day == 5:
    print("Пятница")
elif day == 6:
    print("Суббота")
else:
    print("Воскресенье")