from db import init_db, get_connection, get_all_students, add_coins, delete_student, \
               create_teacher, get_all_teachers, delete_teachers, create_item, get_all_item, delete_item, update_student, add_student

def safe_int(prompt: str) -> int:
    while True:
        try:
            return int(input(prompt).strip())
        except ValueError:
            print("⚠️ Введите целое число!")

def main():
    init_db()
    print("🚀 Система запущена. Введите 'off' для выхода.\n")
    
    choice = ""
    while choice.lower() != "off":
        print("="*30)
        print("📋 МЕНЮ")
        print("1. Добавить студента (все поля)")
        print("2. Показать студентов")
        print("3. Обновить студента")
        print("4. Удалить студента")
        print("5. Добавить учителя")
        print("6. Показать учителей")
        print("7. Удалить учителя")
        print("8. Добавить предмет")
        print("9. Показать предметы")
        print("10. Удалить предмет")
        print("off - Выход")
        
        choice = input("\n🔹 Команда: ").strip().lower()
        
        if choice == "1":
            ans = input("➕ Добавить студента? (y/n): ").strip().lower()
            if ans in ("y", "yes", "д"):
                name = input("  Имя: ").strip()
                if not name:
                    print("❌ Имя не может быть пустым.")
                    continue
                    
                class_name = input("  Класс: ").strip()
                
                # Безопасный ввод монет
                coins_str = input("  Монеты (по умолч. 0): ").strip()
                coins = int(coins_str) if coins_str else 0
                
                data = input("  Доп. данные (data): ").strip()
                
                # ✅ Вызываем готовую функцию из db.py
                add_student(name, class_name, coins, data)
                print("✅ Студент успешно добавлен!")
            else:
                print("⏸️ Отмена.")
                
        elif choice == "2":
            for s in get_all_students():
                print(f"ID:{s['id']} | {s['name']} | Класс:{s['class']} | 💰{s['coins']} | Data:{s['data']}")
                
        elif choice == "3":
            sid = safe_int("ID студента: ")
            update_student(sid, input("Новое имя: ").strip(), input("Новый класс: ").strip())
            print("✅ Обновлено.")
            
        elif choice == "4":
            delete_student(safe_int("ID студента: "))
            print("✅ Удалён.")
            
        elif choice == "5":
            create_teacher(input("Имя учителя: ").strip(), input("Класс: ").strip())
            print("✅ Учитель добавлен.")
            
        elif choice == "6":
            for t in get_all_teachers():
                print(f"ID:{t['id']} | {t['name']} | Класс:{t['class']}")
                
        elif choice == "7":
            delete_teachers(safe_int("ID учителя: "))
            print("✅ Учитель удалён.")
            
        elif choice == "8":
            create_item(input("Название предмета: ").strip())
            print("✅ Предмет добавлен.")
            
        elif choice == "9":
            for i in get_all_item():
                print(f"ID:{i['id']} | {i['name']}")
                
        elif choice == "10":
            delete_item(safe_int("ID предмета: "))
            print("✅ Предмет удалён.")
            
        elif choice == "off":
            print("👋 Работа завершена.")
            
        else:
            print("⚠️ Неизвестная команда. Попробуйте снова.")

if __name__ == "__main__":
    main()