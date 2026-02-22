import sqlite3

def check_db():
    try:
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check table schema
        cursor.execute("PRAGMA table_info(journals)")
        columns = cursor.fetchall()
        print("Table Schema:")
        for col in columns:
            print(f"  {col['name']} ({col['type']})")
            
        # Check last 5 entries
        cursor.execute("SELECT id, author_name, department, paper_title, journal_name FROM journals ORDER BY id DESC LIMIT 5")
        rows = cursor.fetchall()
        print("\nLast 5 Records:")
        for row in rows:
            print(f"  ID: {row['id']}")
            print(f"    Author: {repr(row['author_name'])}")
            print(f"    Dept: {repr(row['department'])}")
            print(f"    Title: {repr(row['paper_title'])}")
            print(f"    Journal: {repr(row['journal_name'])}")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    check_db()
