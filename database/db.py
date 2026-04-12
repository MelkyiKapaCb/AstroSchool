import sqlite3
DB_PATH = 'database.db'

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            coins INTEGER DEFAULT 0,
            name TEXT
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
            class_name TEXT
        );

        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        );
    ''')
    conn.commit()
    conn.close()

# add student
def create_student(name, class_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO students (name, class) VALUES (?, ?)',
        (name, class_name)
    )
    conn.commit()
    conn.close()

# read students
def get_all_students():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students')
    students = cursor.fetchall()
    conn.close()
    return students

# add money
def add_coins(student_id, amount):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE students SET coins = coins + ? WHERE id = ?',
        (amount, student_id)
    )
    conn.commit()
    conn.close()

# delete student
def delete_student(student_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM  students WHERE id = ?', (student_id,))
    conn.commit()
    conn.close()

# add teacher
def create_teacher(name_teacher, class_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO teachers (name, class) VALUES (?, ?)',
        (name_teacher, class_name)
    )
    conn.commit()
    conn.close()

# read teachers
def get_all_teachers():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM teachers')
    teachers = cursor.fetchall()
    conn.close()
    return teachers

# delete money
def delete_coins(student_id, amount):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE students SET coins = coins - ? WHERE id = ?',
        (amount, student_id)
    )
    conn.commit()
    conn.close()

# delete teachers
def delete_teachers(teacher_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM  teachers WHERE id = ?', (teacher_id,))
    conn.commit()
    conn.close()

# add item
def create_item(name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO items (name) VALUES (?)',
        (name,)
    )
    conn.commit()
    conn.close()

# read item
def get_all_item():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM items')
    items = cursor.fetchall()
    conn.close()
    return items

# delete item
def delete_item(item_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM items WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()