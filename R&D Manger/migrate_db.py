import sqlite3
import os

def migrate():
    db_path = 'database.db'
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found. Skipping migration.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if columns already exist
    cursor.execute("PRAGMA table_info(journals)")
    columns = [row[1] for row in cursor.fetchall()]

    if 'publication_type' not in columns:
        print("Adding 'publication_type' column...")
        cursor.execute("ALTER TABLE journals ADD COLUMN publication_type TEXT DEFAULT 'Journal'")
    
    if 'status' not in columns:
        print("Adding 'status' column...")
        cursor.execute("ALTER TABLE journals ADD COLUMN status TEXT DEFAULT 'Published'")

    conn.commit()
    conn.close()
    print("Migration completed successfully!")

if __name__ == '__main__':
    migrate()
