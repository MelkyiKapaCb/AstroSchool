"""
Запуск из папки проекта AstroSchool:
    python database/seed_products.py
Добавляет несколько товаров в database.db (таблица items — магазин)
"""
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import init_db, create_item  # noqa: E402


def main():
    init_db()

    test_items = [
        ("Ручка с пером", 15),
        ("Книга заклинаний", 50),
        ("Свиток опыта", 100),
    ]

    for name, price in test_items:
        create_item(name, price)
        print("добавлен товар:", name, "цена:", price)

    print("готово")


if __name__ == "__main__":
    main()
