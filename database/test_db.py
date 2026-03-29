from db import init_db, create_student, get_all_students, delete_student

init_db()
# create_student('Артём', '10A')
# create_student('Мадина', '10B')

delete_student(6)
delete_student(5)
delete_student(4)
delete_student(3)
students = get_all_students()
for s in students:
    print(s['id'],s['name'], s['coins'])
