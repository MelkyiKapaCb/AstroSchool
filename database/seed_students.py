"""
Запуск из папки проекта AstroSchool:
    python database/seed_students.py
Добавляет несколько тестовых студентов в database.db
"""
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# чтобы находился пакет database при запуске файла напрямую
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import init_db, add_student  # noqa: E402


def main():
    init_db()

    test_students = [
        ("Анна Петрова", "5А", 120, ""),
        ("Борис Смирнов", "5Б", 80, "староста"),
        ("Вера Козлова", "6А", 200, ""),
    ]

    for name, class_name, coins, data in test_students:
        add_student(name, class_name, coins, data)
        print("добавлен студент:", name)

    print("готово")


if __name__ == "__main__":
    main()
