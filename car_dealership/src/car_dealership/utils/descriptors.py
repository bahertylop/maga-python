"""
Дескриптор для проверки диапазона значений.

Используется для полей, которые должны быть числами
в определённом диапазоне. Один дескриптор может применяться
к нескольким полям разных классов.
"""


class RangeDescriptor:
    """
    Дескриптор диапазона.

    При записи значения проверяет, что оно является числом
    и находится в диапазоне [min_value, max_value].
    Значение хранится в instance.__dict__ под именем поля.
    """

    def __init__(self, min_value, max_value):
        self.min_value = min_value
        self.max_value = max_value
        self.name = "value"

    def __set_name__(self, owner, name):
        """
        Вызывается автоматически при создании класса.

        Python сообщает дескриптору, под каким именем он
        используется в классе. Это позволяет сохранять значение
        в instance.__dict__ под правильным ключом.
        """
        self.name = name

    def __get__(self, instance, owner=None):
        """
        Возвращает значение при чтении атрибута.

        Если обращаются через класс (instance is None),
        возвращается сам дескриптор.
        """
        if instance is None:
            return self
        return instance.__dict__.get(self.name)

    def __set__(self, instance, value):
        """
        Проверяет и сохраняет значение при записи.

        Если значение не число — выбрасывается TypeError.
        Если значение вне диапазона — выбрасывается ValueError.
        """
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"{self.name} должно быть числом")

        if not (self.min_value <= value <= self.max_value):
            raise ValueError(
                f"{self.name} должно быть от {self.min_value} "
                f"до {self.max_value}"
            )

        instance.__dict__[self.name] = value
