from collections import deque


class Queue:
    """Очередь (FIFO): первым пришёл — первым ушёл."""

    def __init__(self):
        self.__items = deque()

    def enqueue(self, item):
        """Добавляет элемент в конец очереди."""
        self.__items.append(item)

    def dequeue(self):
        """Удаляет и возвращает первый элемент очереди."""
        if self.is_empty():
            raise IndexError("dequeue из пустой очереди")
        return self.__items.popleft()

    def peek(self):
        """Возвращает первый элемент, не удаляя его."""
        if self.is_empty():
            raise IndexError("peek из пустой очереди")
        return self.__items[0]

    def is_empty(self):
        """Проверяет, пуста ли очередь."""
        return len(self.__items) == 0

    def __len__(self):
        return len(self.__items)

    def __str__(self):
        return f"Queue({list(self.__items)})"


# Пример использования
q = Queue()
print(q.is_empty())     # True

q.enqueue(10)
q.enqueue(20)
q.enqueue(30)
print(q)                # Queue([10, 20, 30])

print(q.peek())         # 10
print(q.dequeue())      # 10
print(q)                # Queue([20, 30])
print(len(q))           # 2

q.dequeue()
q.dequeue()
print(q.is_empty())     # True

try:
    q.dequeue()
except IndexError as e:
    print("Ошибка:", e) # Ошибка: dequeue из пустой очереди