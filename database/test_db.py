from db import init_db, create_item, get_all_item

init_db()
create_item("тестовая игрушка", 10)
items = get_all_item()
for row in items:
    print(row["id"], row["name"], row["price"])
