from db import init_db, create_student, get_all_students, delete_student, create_teacher, get_all_teachers, delete_teachers, get_all_item, create_item, delete_item, DATATIME

init_db()
# create_student('Артём', '10A')
# create_student('Мадина', '10B')
# create_teacher('Павел', 'Python')
create_item('игрушки')
delete_teachers(6)
delete_teachers(5)
delete_teachers(4)
delete_teachers(3)
delete_teachers(2)
delete_teachers(7)
delete_teachers(6)
delete_student(6)
delete_student(7)
students = get_all_students()
teachers = get_all_teachers()
items = get_all_item()
for s in students:
    print(s['id'],s['name'], s['coins'])
for s in teachers:
    print(s['id'],s['name'], s['class'])
for s in items:
    print(s['id'],s['name'])
print(DATATIME)
