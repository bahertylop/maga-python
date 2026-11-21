"""Добавляет корень проекта в sys.path, чтобы примеры запускались откуда угодно."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# На Windows вывод в файл/IDE может идти в cp1251 и не знать символов ₽ ✓ →.
# Просим стандартный вывод работать в UTF-8 (в консоли это уже так).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
