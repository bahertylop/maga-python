for rabbits in range(33):
    legs = 4 * rabbits

    if legs <= 64:
        geese = (64 - legs) // 2

        if 2 * geese + 4 * rabbits == 64:
            print("Кроликов:", rabbits, "Гусей:", geese)