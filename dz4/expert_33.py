"""
Задача 33 (контекстный менеджер: __enter__ и __exit__). В автосалоне есть
операции, которые нужно выполнять «аккуратно»: например, при работе с базой
данных автомобилей её нужно открыть в начале и обязательно закрыть в конце —
даже если произошла ошибка. Реализуйте класс CarDatabase как контекстный
менеджер: методы __enter__ (открывает базу и возвращает её) и __exit__
(закрывает базу, даже если было исключение). Продемонстрируйте использование
через with CarDatabase() as db:. Дополнительно покажите, что происходит, если
внутри with возникнет исключение, — база всё равно закроется. Объясните,
зачем нужны контекстные менеджеры, как они связаны с конструкцией
try/finally, что делают аргументы exc_type, exc_value, traceback в __exit__ и
что нужно вернуть, чтобы «проглотить» исключение.
"""


class CarDatabase:
    def __init__(self, name="cars.db", suppress=None):
        self.name = name
        self.is_open = False
        self._cars = []
        # Исключения, которые менеджер «проглотит» (для демонстрации)
        self.suppress = suppress or ()

    def __enter__(self):
        print(f"  🔓 База «{self.name}» открыта")
        self.is_open = True
        return self  # именно этот объект попадёт в переменную после as

    def __exit__(self, exc_type, exc_value, traceback):
        # Вызывается ВСЕГДА при выходе из with: и при нормальном завершении,
        # и при исключении.
        self.is_open = False
        print(f"  🔒 База «{self.name}» закрыта")
        if exc_type is None:
            print("     (блок with завершился без ошибок)")
            return False
        print(f"     (выход из-за {exc_type.__name__}: {exc_value})")
        # True — исключение «проглочено», дальше не пойдёт.
        # False/None — исключение пробросится наружу.
        return issubclass(exc_type, self.suppress)

    def add(self, car):
        if not self.is_open:
            raise RuntimeError("база закрыта")
        self._cars.append(car)
        print(f"     добавлен: {car}")

    def all(self):
        return list(self._cars)


print("1) Обычная работа:")
with CarDatabase() as db:
    db.add("Toyota Camry")
    db.add("Kia Rio")
print("   db.is_open после with:", db.is_open)

print("\n2) Исключение внутри with — база всё равно закрывается:")
try:
    with CarDatabase() as db:
        db.add("BMW X5")
        raise ValueError("ошибка записи в базу")
        db.add("Lada Vesta")  # до этой строки дело не дойдёт
except ValueError as e:
    print("   исключение дошло до внешнего кода:", e)
print("   db.is_open:", db.is_open)

print("\n3) __exit__ возвращает True — исключение «проглочено»:")
with CarDatabase(suppress=(KeyError,)) as db:
    db.add("Haval Jolion")
    raise KeyError("VIN не найден")
print("   программа продолжила работу, исключение не вышло наружу")

print("\n4) То же самое без with — через try/finally:")
db = CarDatabase()
db.__enter__()
try:
    db.add("Toyota Corolla")
finally:
    db.__exit__(None, None, None)

# Зачем нужны контекстные менеджеры:
# многие ресурсы надо обязательно «вернуть»: закрыть файл или соединение
# с БД, отпустить блокировку, завершить транзакцию. Если забыть или если
# случится исключение до закрытия, ресурс «утечёт». with гарантирует, что
# освобождение произойдёт, и делает это одной строкой, без шаблонного кода.
# Примеры из стандартной библиотеки: with open(...) as f, with lock:,
# with sqlite3.connect(...) as conn (транзакция), with
# decimal.localcontext(), with unittest.mock.patch(...).
#
# Связь с try/finally: конструкция
#     with CarDatabase() as db:
#         работа(db)
# по сути равна
#     manager = CarDatabase()
#     db = manager.__enter__()
#     try:
#         работа(db)
#     finally:
#         manager.__exit__(тип, значение, traceback)  # или None, None, None
# with — это try/finally, «упакованный» в класс и переиспользуемый.
#
# Аргументы __exit__:
# - exc_type — класс исключения (ValueError) или None, если ошибок не было;
# - exc_value — сам объект исключения (с текстом сообщения);
# - traceback — объект трассировки: где именно произошла ошибка.
# По ним можно, например, откатить транзакцию при ошибке и
# зафиксировать при успехе.
#
# Чтобы «проглотить» исключение, __exit__ должен вернуть True (истинное
# значение). Тогда выполнение продолжится после блока with, как будто
# ошибки не было. Если вернуть False или None (ничего не вернуть) —
# исключение пробросится дальше. Глотать ошибки стоит осознанно и только
# конкретные типы, как в примере 3, иначе можно скрыть настоящую проблему.
