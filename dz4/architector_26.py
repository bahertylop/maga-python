"""
Задача 26 (паттерн Observer). Покупатели автосалона хотят получать
уведомления, когда поступает новая модель или начинается распродажа.
Реализуйте паттерн «Наблюдатель»: класс Dealership хранит список подписчиков
(Buyer) и при поступлении нового автомобиля уведомляет всех через метод
notify(). Продемонстрируйте, что при добавлении автомобиля все покупатели
получают уведомление. Дополнительно реализуйте unsubscribe() и покажите,
что после отписки покупатель больше не получает уведомлений. Объясните, где
в реальных проектах используется этот паттерн (GUI, событийные системы,
мессенджеры, pub/sub) и как он помогает избежать жёсткой связи между
объектами.
"""


class Buyer:
    """Наблюдатель (подписчик)."""

    def __init__(self, name):
        self.name = name

    def update(self, message):
        print(f"  📩 Уведомление для {self.name}: {message}")


class Dealership:
    """Издатель (субъект): хранит подписчиков и рассылает им события."""

    def __init__(self, name):
        self.name = name
        self.cars = []
        self._subscribers = []

    def subscribe(self, subscriber):
        if subscriber not in self._subscribers:
            self._subscribers.append(subscriber)

    def unsubscribe(self, subscriber):
        if subscriber in self._subscribers:
            self._subscribers.remove(subscriber)

    def notify(self, message):
        # Издатель знает о подписчиках только одно: у них есть update().
        for subscriber in self._subscribers:
            subscriber.update(message)

    def add_car(self, car):
        self.cars.append(car)
        print(f"[{self.name}] Поступил автомобиль: {car}")
        self.notify(f"в салоне «{self.name}» новинка — {car}")

    def start_sale(self, percent):
        print(f"[{self.name}] Старт распродажи")
        self.notify(f"распродажа в «{self.name}»: скидки до {percent}%")


# Подписчиком может быть любой объект с update() — не только Buyer
class SmsGateway:
    def update(self, message):
        print(f"  📱 SMS-рассылка: {message}")


salon = Dealership("АвтоМир")
ivan, anna, oleg = Buyer("Иван"), Buyer("Анна"), Buyer("Олег")

for s in (ivan, anna, oleg, SmsGateway()):
    salon.subscribe(s)

salon.add_car("Toyota Camry")
salon.start_sale(15)

print("\nАнна отписалась.")
salon.unsubscribe(anna)
salon.add_car("Haval Jolion")  # Анна больше ничего не получает

# Где используется паттерн:
# - GUI: кнопка хранит обработчики «on_click», окно подписывается на
#   события клавиатуры и мыши (tkinter, Qt — сигналы и слоты);
# - событийные системы: сигналы Django (post_save — «объект сохранён»),
#   хуки и плагины;
# - мессенджеры и соцсети: подписка на канал, уведомления о новых постах;
# - pub/sub и очереди сообщений (Redis Pub/Sub, Kafka, RabbitMQ) — тот же
#   принцип, но издатель и подписчики могут жить в разных программах;
# - реактивные интерфейсы: обновление экрана при изменении данных.
#
# Как помогает избежать жёсткой связи:
# Dealership не знает, кто подписан и что подписчик сделает с сообщением:
# покажет на экране, отправит SMS или запишет в журнал. Ему достаточно,
# что у подписчика есть метод update(). Поэтому новые виды подписчиков
# (SmsGateway) добавляются без изменения кода салона, а подписаться или
# отписаться можно прямо во время работы программы.
