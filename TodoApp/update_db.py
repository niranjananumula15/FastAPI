
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "todosapp.db"

conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

# Get existing users table columns
cursor.execute("PRAGMA table_info(users)")
existing_columns = {row[1] for row in cursor.fetchall()}

# Add missing columns
required_columns = {
    "email": "VARCHAR",
    "username": "VARCHAR",
    "first_name": "VARCHAR",
    "last_name": "VARCHAR",
    "hashed_password": "VARCHAR",
    "is_active": "BOOLEAN DEFAULT 1",
    "role": "VARCHAR",
}

for column, column_type in required_columns.items():
    if column not in existing_columns:
        cursor.execute(
            f"ALTER TABLE users ADD COLUMN {column} {column_type}"
        )
        print(f"Added column: {column}")
    else:
        print(f"Already exists: {column}")

# Check todos table
cursor.execute("PRAGMA table_info(todos)")
todo_columns = {row[1] for row in cursor.fetchall()}

if "owner_id" not in todo_columns:
    cursor.execute(
        "ALTER TABLE todos ADD COLUMN owner_id INTEGER REFERENCES users(id)"
    )
    print("Added column: owner_id")
else:
    print("Already exists: owner_id")

conn.commit()
conn.close()

print(f"Database update completed: {DATABASE_PATH}")
