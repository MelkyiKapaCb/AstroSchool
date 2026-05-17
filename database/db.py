import sqlite3
import hashlib

DB_PATH = "database.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            coins INTEGER DEFAULT 0,
            class TEXT,
            data TEXT
        );
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            amount INTEGER NOT NULL,
            reason TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id)
        );
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            class TEXT
        );
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'teacher', 'student')),
            teacher_id INTEGER,
            student_id INTEGER,
            FOREIGN KEY (teacher_id) REFERENCES teachers(id),
            FOREIGN KEY (student_id) REFERENCES students(id)
        );
        """
    )
    # Добавляем колонку price если её нет
    cols = [row[1] for row in conn.execute("PRAGMA table_info(items)").fetchall()]
    if "price" not in cols:
        conn.execute("ALTER TABLE items ADD COLUMN price INTEGER DEFAULT 0")
    
    # Создаём админа по умолчанию (если нет)
    admin = conn.execute(
        "SELECT * FROM users WHERE username = 'admin'"
    ).fetchone()
    if not admin:
        hashed_password = hashlib.sha256("admin123".encode()).hexdigest()
        conn.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ("admin", hashed_password, "admin"),
        )
    
    conn.commit()
    conn.close()


def create_user(username, password, role, teacher_id=None, student_id=None):
    conn = get_connection()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    conn.execute(
        "INSERT INTO users (username, password, role, teacher_id, student_id) VALUES (?, ?, ?, ?, ?)",
        (username, hashed_password, role, teacher_id, student_id),
    )
    conn.commit()
    conn.close()


def get_user(username):
    conn = get_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()
    conn.close()
    return user


def verify_user(username, password):
    user = get_user(username)
    if user:
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        if user["password"] == hashed_password:
            return dict(user)
    return None


def get_all_users():
    conn = get_connection()
    users = conn.execute("SELECT * FROM users").fetchall()
    conn.close()
    return users


def delete_user(user_id):
    conn = get_connection()
    conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()


def get_teacher_by_id(teacher_id):
    conn = get_connection()
    teacher = conn.execute(
        "SELECT * FROM teachers WHERE id = ?", (teacher_id,)
    ).fetchone()
    conn.close()
    return teacher


def get_students_by_class(class_name):
    conn = get_connection()
    students = conn.execute(
        "SELECT * FROM students WHERE class = ?", (class_name,)
    ).fetchall()
    conn.close()
    return students


# Старые функции оставляем без изменений
def create_student(name, class_name):
    conn = get_connection()
    conn.execute(
        "INSERT INTO students (name, class) VALUES (?, ?)", (name, class_name)
    )
    conn.commit()
    conn.close()


def add_student(name: str, class_name: str, coins: int = 0, data: str = ""):
    conn = get_connection()
    conn.execute(
        "INSERT INTO students (name, coins, class, data) VALUES (?, ?, ?, ?)",
        (name, coins, class_name, data),
    )
    conn.commit()
    conn.close()


def get_all_students():
    conn = get_connection()
    res = conn.execute("SELECT * FROM students").fetchall()
    conn.close()
    return res


def add_coins(student_id, amount):
    conn = get_connection()
    conn.execute(
        "UPDATE students SET coins = coins + ? WHERE id = ?", (amount, student_id)
    )
    conn.commit()
    conn.close()


def delete_student(student_id):
    conn = get_connection()
    conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()
    conn.close()


def create_teacher(name_teacher, class_name):
    conn = get_connection()
    conn.execute(
        "INSERT INTO teachers (name, class) VALUES (?, ?)", (name_teacher, class_name)
    )
    conn.commit()
    conn.close()


def get_all_teachers():
    conn = get_connection()
    res = conn.execute("SELECT * FROM teachers").fetchall()
    conn.close()
    return res


def delete_coins(student_id, amount):
    conn = get_connection()
    conn.execute(
        "UPDATE students SET coins = coins - ? WHERE id = ?", (amount, student_id)
    )
    conn.commit()
    conn.close()


def delete_teachers(teacher_id):
    conn = get_connection()
    conn.execute("DELETE FROM teachers WHERE id = ?", (teacher_id,))
    conn.commit()
    conn.close()


def create_item(name, price=0):
    conn = get_connection()
    conn.execute("INSERT INTO items (name, price) VALUES (?, ?)", (name, price))
    conn.commit()
    conn.close()


def get_all_item():
    conn = get_connection()
    res = conn.execute("SELECT * FROM items").fetchall()
    conn.close()
    return res


def delete_item(item_id):
    conn = get_connection()
    conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()


def get_student_by_id(student_id: int):
    conn = get_connection()
    res = conn.execute(
        "SELECT * FROM students WHERE id = ?", (student_id,)
    ).fetchone()
    conn.close()
    return res


def update_student(student_id: int, name: str, class_name: str):
    conn = get_connection()
    conn.execute(
        "UPDATE students SET name = ?, class = ? WHERE id = ?",
        (name, class_name, student_id),
    )
    conn.commit()
    conn.close()


def get_transactions_by_student(student_id: int, limit: int = 50):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM transactions WHERE student_id = ? ORDER BY created_at DESC LIMIT ?",
        (student_id, limit),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]