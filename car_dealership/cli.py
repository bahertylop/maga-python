"""
Точка входа для командной строки.

Запуск (состояние хранится в data/dealership.db между запусками):

    python cli.py add --vin XTA210930Y2765432 --brand Toyota --model Camry --price 3000000
    python cli.py list
    python cli.py sell --vin XTA210930Y2765432 --buyer Иванов
    python cli.py report
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# На Windows вывод в файл/IDE может идти в cp1251 и не знать символов ₽ ✓ →.
# Просим стандартный вывод работать в UTF-8 (в консоли это уже так).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import config
from src.car_dealership.cli import create_parser, Commands


def main(argv=None) -> int:
    """Точка входа CLI. Возвращает код выхода (0 — успех, 1 — ошибка)."""
    parser = create_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    db_path = args.db or str(Path(__file__).parent / config.DB_PATH)
    commands = Commands(db_path=db_path, autosave=True)
    handler = getattr(commands, f"cmd_{args.command}", None)

    if handler is None:
        print(f"✗ Неизвестная команда: {args.command}")
        parser.print_help()
        return 1

    return 0 if handler(args) else 1


if __name__ == "__main__":
    sys.exit(main())
