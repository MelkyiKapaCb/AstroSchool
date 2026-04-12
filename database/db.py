import sqlite3

from app.security import hash_password

DB_PATH = "database.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _migrate(conn):
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(students)")
    student_cols = {row[1] for row in cur.fetchall()}
    if "user_id" not in student_cols:
        cur.execute("ALTER TABLE students ADD COLUMN user_id INTEGER UNIQUE")

    cur.execute("PRAGMA table_info(items)")
    item_cols = {row[1] for row in cur.fetchall()}
    if "price" not in item_cols:
        cur.execute("ALTER TABLE items ADD COLUMN price INTEGER NOT NULL DEFAULT 10")
    if "description" not in item_cols:
        cur.execute("ALTER TABLE items ADD COLUMN description TEXT NOT NULL DEFAULT ''")

    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            display_name TEXT NOT NULL,
            is_admin INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS group_members (
            group_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            PRIMARY KEY (group_id, student_id),
            FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        );
        """
    )


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            coins INTEGER DEFAULT 0,
            class TEXT,
            data TEXT,
            user_id INTEGER UNIQUE
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
            price INTEGER NOT NULL DEFAULT 10,
            description TEXT NOT NULL DEFAULT ''
        );
        """
    )
    conn.commit()
    _migrate(conn)
    conn.commit()
    _seed_admin(conn)
    conn.commit()
    conn.close()


def _seed_admin(conn):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS c FROM users")
    if cur.fetchone()["c"] > 0:
        return
    cur.execute(
        """
        INSERT INTO users (email, password_hash, display_name, is_admin)
        VALUES (?, ?, ?, 1)
        """,
        ("admin@local", hash_password("admin"), "Администратор"),
    )


# --- users ---


def get_user_by_id(user_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row


def get_user_by_email(email: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE lower(email) = lower(?)", (email.strip(),))
    row = cur.fetchone()
    conn.close()
    return row


def create_user(email: str, password: str, display_name: str, *, is_admin: bool = False):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO users (email, password_hash, display_name, is_admin)
        VALUES (?, ?, ?, ?)
        """,
        (email.strip().lower(), hash_password(password), display_name.strip(), int(is_admin)),
    )
    uid = cur.lastrowid
    conn.commit()
    conn.close()
    return uid


def register_user_with_student(email: str, password: str, display_name: str):
    """Новый пользователь + запись студента с монетами (профиль магазина)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO users (email, password_hash, display_name, is_admin)
        VALUES (?, ?, ?, 0)
        """,
        (email.strip().lower(), hash_password(password), display_name.strip()),
    )
    uid = cur.lastrowid
    cur.execute(
        """
        INSERT INTO students (name, coins, class, user_id)
        VALUES (?, 100, NULL, ?)
        """,
        (display_name.strip(), uid),
    )
    conn.commit()
    conn.close()
    return uid


def get_student_by_user_id(user_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM students WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row


# --- students ---


def create_student(name, class_name, *, user_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO students (name, class, user_id) VALUES (?, ?, ?)",
        (name, class_name, user_id),
    )
    conn.commit()
    conn.close()


def get_all_students():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students ORDER BY name")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_student(student_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM students WHERE id = ?", (student_id,))
    row = cur.fetchone()
    conn.close()
    return row


def delete_student(student_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()
    conn.close()


def add_coins(student_id, amount):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE students SET coins = coins + ? WHERE id = ?", (amount, student_id)
    )
    conn.commit()
    conn.close()


def delete_coins(student_id, amount):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE students SET coins = coins - ? WHERE id = ?", (amount, student_id)
    )
    conn.commit()
    conn.close()


# --- teachers ---


def create_teacher(name_teacher, class_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO teachers (name, class) VALUES (?, ?)", (name_teacher, class_name)
    )
    conn.commit()
    conn.close()


def get_all_teachers():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM teachers")
    rows = cursor.fetchall()
    conn.close()
    return rows


def delete_teachers(teacher_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM teachers WHERE id = ?", (teacher_id,))
    conn.commit()
    conn.close()


# --- items ---


def create_item(name: str, price: int = 10, description: str = ""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO items (name, price, description) VALUES (?, ?, ?)",
        (name.strip(), int(price), description.strip()),
    )
    conn.commit()
    conn.close()


def get_all_items():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items ORDER BY name")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_item(item_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    row = cur.fetchone()
    conn.close()
    return row


def delete_item(item_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()


# --- groups ---


def create_group(name: str, description: str = ""):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO groups (name, description) VALUES (?, ?)",
        (name.strip(), description.strip()),
    )
    gid = cur.lastrowid
    conn.commit()
    conn.close()
    return gid


def get_all_groups():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM groups ORDER BY name")
    rows = cur.fetchall()
    conn.close()
    return rows


def get_group(group_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM groups WHERE id = ?", (group_id,))
    row = cur.fetchone()
    conn.close()
    return row


def get_students_in_group(group_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT s.* FROM students s
        JOIN group_members gm ON gm.student_id = s.id
        WHERE gm.group_id = ?
        ORDER BY s.name
        """,
        (group_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_student_ids_in_group(group_id: int) -> set:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT student_id FROM group_members WHERE group_id = ?", (group_id,)
    )
    ids = {r["student_id"] for r in cur.fetchall()}
    conn.close()
    return ids


def add_student_to_group(group_id: int, student_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT OR IGNORE INTO group_members (group_id, student_id)
        VALUES (?, ?)
        """,
        (group_id, student_id),
    )
    conn.commit()
    conn.close()


def remove_student_from_group(group_id: int, student_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM group_members WHERE group_id = ? AND student_id = ?",
        (group_id, student_id),
    )
    conn.commit()
    conn.close()


# backwards-compatible name
get_all_item = get_all_items
