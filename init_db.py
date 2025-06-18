from database.models import create_tables, seed_users
from database.queries import add_user

if __name__ == "__main__":
    create_tables()
    seed_users()

    #add_user("@alexwf0f", "Алекс Богатский", "ege_1")  # ← подставь нужную группу
