x = float(input("x = "))
y = float(input("y = "))

if x == 0 and y == 0:
    print("Начало координат")
elif y == 0:
    print("Ось OX")
elif x == 0:
    print("Ось OY")
elif x > 0 and y > 0:
    print("I координатный угол")
elif x < 0 and y > 0:
    print("II координатный угол")
elif x < 0 and y < 0:
    print("III координатный угол")
else:
    print("IV координатный угол")