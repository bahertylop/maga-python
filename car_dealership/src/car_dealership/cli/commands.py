"""
Обработчики команд CLI.

Класс Commands связывает команды из парсера с сервисами
проекта. Каждый метод cmd_* выполняет одну команду и возвращает
True при успехе и False при ошибке (по нему cli.py выбирает код выхода).
"""

from ..patterns import CarFactory
from ..services import (
    CarStorage,
    DealService,
    RentalService,
    NotificationService,
    ReportService,
    EmailNotifier,
    PercentCommission,
)
from ..database import (
    DatabaseManager,
    CarRepository,
    ClientRepository,
    DealRepository,
)
from ..models import Client, Engine
from ..exceptions import DealershipError
from ..utils import CarUtils

# Ошибки, которые обработчики показывают пользователю как «✗ Ошибка».
_USER_ERRORS = (DealershipError, TypeError, ValueError)


def _convert(value: str):
    """Превращает строку из командной строки в int / float / str."""
    for caster in (int, float):
        try:
            return caster(value)
        except ValueError:
            continue
    return value


class Commands:
    """
    Обработчики команд командной строки.

    Создаёт все сервисы проекта и вызывает их в соответствующих
    методах. Если autosave=True, изменения сразу записываются в БД,
    а при создании данные загружаются из неё — так состояние
    переживает отдельные запуски `python cli.py ...`.
    """

    def __init__(self, db_path: str = "data/dealership.db",
                 autosave: bool = False):
        self.db_path = db_path
        self.autosave = autosave
        self.storage = CarStorage()
        self.notifier = NotificationService()
        self.email = EmailNotifier()
        self.reports = ReportService()
        self.deals = DealService(
            self.storage, self.email, PercentCommission(),
            publisher=self.notifier,
        )
        self.rentals = RentalService(self.storage, self.email)
        self.clients: list = []
        if autosave:
            self._autoload()

    def _get_db(self) -> DatabaseManager:
        """Возвращает контекстный менеджер для работы с БД."""
        return DatabaseManager(self.db_path)

    # ─── вспомогательные методы ───

    def _autoload(self) -> None:
        """Тихо загружает данные из БД (если она уже создана)."""
        from pathlib import Path
        if self.db_path != ":memory:" and not Path(self.db_path).exists():
            return
        try:
            self._load_from_db()
        except DealershipError as e:
            print(f"✗ Не удалось загрузить БД: {e}")

    def _load_from_db(self) -> int:
        """Загружает автомобили и клиентов; возвращает число новых машин."""
        loaded = 0
        with self._get_db() as db:
            for item in CarRepository(db).find_all():
                if all(i.vin != item.vin for i in self.storage):
                    self.storage.add(item)
                    loaded += 1
            for client in ClientRepository(db).find_all():
                if all(c.name != client.name for c in self.clients):
                    self.clients.append(client)
                    self.notifier.subscribe(client)
        return loaded

    def _persist(self, *items, client=None, deal=None) -> None:
        """Записывает изменения в БД (только при autosave)."""
        if not self.autosave:
            return
        with self._get_db() as db:
            cars = CarRepository(db)
            for item in items:
                cars.save(item)
            if client is not None:
                ClientRepository(db).save(client)
            if deal is not None:
                DealRepository(db).save_deal_for(
                    deal["item"], deal["buyer"], deal["commission"]
                )

    @staticmethod
    def _build_engine(spec: str) -> Engine:
        """Разбирает строку «вид:мощность:объём»."""
        parts = spec.split(":")
        if len(parts) != 3:
            raise ValueError('Двигатель задаётся как "вид:мощность:объём"')
        return Engine(parts[0], int(parts[1]), float(parts[2]))

    # ─── add ───
    def cmd_add(self, args) -> bool:
        """Добавляет новый объект."""
        try:
            kwargs = {
                "vin": args.vin,
                "brand": args.brand,
                "model": args.model,
                "price": args.price,
                "year": args.year,
                "mileage": args.mileage,
            }
            for pair in args.extras:
                if "=" not in pair:
                    raise ValueError(f"Ожидалось КЛЮЧ=ЗНАЧЕНИЕ, получено {pair!r}")
                key, value = pair.split("=", 1)
                kwargs[key.strip()] = _convert(value.strip())
            if args.engine:
                kwargs["engine"] = self._build_engine(args.engine)
            item = CarFactory.create(args.type, **kwargs)
            self.storage.add(item)
            self._persist(item)
            print(f"✓ Добавлено: {item.get_info()}")
            return True
        except _USER_ERRORS as e:
            print(f"✗ Ошибка: {e}")
            return False

    # ─── list ───
    def cmd_list(self, args) -> bool:
        """Показывает все объекты в хранилище."""
        if len(self.storage) == 0:
            print("Хранилище пусто")
            return True

        print(f"Всего объектов: {len(self.storage)}")
        for i, item in enumerate(self.storage, start=1):
            print(f"  {i}. {item.get_info()}")
        return True

    # ─── find ───
    def cmd_find(self, args) -> bool:
        """Ищет объект по VIN."""
        try:
            item = self.storage.find_by_vin(args.vin)
            print(f"Найдено: {item.get_info()}")
            return True
        except DealershipError as e:
            print(f"✗ Ошибка: {e}")
            return False

    # ─── sell ───
    def cmd_sell(self, args) -> bool:
        """Продаёт объект по VIN."""
        try:
            result = self.deals.sell(args.vin, args.buyer)
            self._persist(result["item"], deal=result)
            print(f"✓ Продано: {result['item'].title} → {args.buyer}")
            print(f"  Комиссия: {CarUtils.format_price(result['commission'])}")
            return True
        except _USER_ERRORS as e:
            print(f"✗ Ошибка: {e}")
            return False

    # ─── rent ───
    def cmd_rent(self, args) -> bool:
        """Выдаёт объект в прокат."""
        try:
            result = self.rentals.rent(args.vin, args.tenant, args.days)
            self._persist(result["item"])
            print(
                f"✓ Выдано в прокат: {result['item'].title} → {args.tenant} "
                f"на {result['days']} дн., стоимость "
                f"{CarUtils.format_price(result['cost'])}"
            )
            return True
        except _USER_ERRORS as e:
            print(f"✗ Ошибка: {e}")
            return False

    # ─── return ───
    def cmd_return(self, args) -> bool:
        """Принимает объект из проката."""
        try:
            result = self.rentals.return_item(args.vin)
            self._persist(result["item"])
            print(f"✓ Принято из проката: {result['item'].title}")
            return True
        except _USER_ERRORS as e:
            print(f"✗ Ошибка: {e}")
            return False

    # ─── subscribe ───
    def cmd_subscribe(self, args) -> bool:
        """Подписывает клиента на уведомления."""
        client = Client(args.name, args.budget)
        self.notifier.subscribe(client)
        self.clients.append(client)
        self._persist(client=client)
        print(f"✓ Подписан: {client.describe()}")
        print(f"  Подписчиков: {self.notifier.count()}")
        return True

    # ─── report ───
    def cmd_report(self, args) -> bool:
        """Генерирует отчёт по хранилищу и сделкам."""
        print(self.reports.generate(self.storage, "АвтоМир"))
        print()
        print(self.reports.generate_stats(self.storage))
        print()
        print(self.reports.generate_sales_report(self._all_deals()))
        return True

    def _all_deals(self) -> list:
        """Сделки для отчёта: из БД (при autosave) или из текущего сеанса."""
        if not self.autosave:
            return self.deals.history
        try:
            with self._get_db() as db:
                rows = DealRepository(db).find_all()
        except DealershipError:
            return self.deals.history
        deals = []
        for row in rows:
            try:
                item = self.storage.find_by_vin(row["vin"])
            except DealershipError:
                continue
            deals.append({"item": item, "buyer": row["buyer"],
                          "commission": row["commission"]})
        return deals

    # ─── save ───
    def cmd_save(self, args) -> bool:
        """Сохраняет объекты и клиентов из хранилища в базу."""
        if len(self.storage) == 0 and not self.clients:
            print("Нечего сохранять")
            return True

        try:
            with self._get_db() as db:
                cars = CarRepository(db)
                for item in self.storage:
                    cars.save(item)
                clients = ClientRepository(db)
                for client in self.clients:
                    clients.save(client)
            print(
                f"✓ Сохранено объектов: {len(self.storage)}, "
                f"клиентов: {len(self.clients)}"
            )
            return True
        except DealershipError as e:
            print(f"✗ Ошибка: {e}")
            return False

    # ─── load ───
    def cmd_load(self, args) -> bool:
        """Загружает объекты из базы в хранилище (дубликаты по VIN пропускаются)."""
        try:
            loaded = self._load_from_db()
            print(f"✓ Загружено новых объектов: {loaded}")
            return True
        except DealershipError as e:
            print(f"✗ Ошибка: {e}")
            return False
