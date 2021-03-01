from .models import *

tables_exists = db.get_tables()
for table in all_models:
    if table._meta.table_name not in tables_exists:
        print(f'Create new table {table.__name__}')
        db.create_tables([table, ])
    else:
        print(f'Table {table} existed')
