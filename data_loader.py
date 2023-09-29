import sqlite3
import csv

DATABASE_NAME = "emails.db"
TESTING = True
def create_tables():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS target_emails (
        id INTEGER PRIMARY KEY,
        email TEXT NOT NULL,
        name TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sender_emails (
        id INTEGER PRIMARY KEY,
        email TEXT NOT NULL,
        password TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sent_log (
        sender_id INTEGER,
        target_id INTEGER,
        FOREIGN KEY(sender_id) REFERENCES sender_emails(id),
        FOREIGN KEY(target_id) REFERENCES target_emails(id)
    )
    """)

    conn.commit()
    conn.close()

def insert_csv_to_table(filename, table_name):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    with open(filename, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row
        for row in reader:
            if table_name == 'target_emails':
                cursor.execute("INSERT INTO target_emails (email, name) VALUES (?, ?)", (row[0],row[1]))
            else:
                cursor.execute("INSERT INTO sender_emails (email, password) VALUES (?, ?)", (row[0], row[1]))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()
    if not TESTING:
        insert_csv_to_table('target_emails.csv', 'target_emails')
        insert_csv_to_table('sender_emails.csv', 'sender_emails')
    else:
        insert_csv_to_table('test_target_emails.csv', 'target_emails')
        insert_csv_to_table('test_sender_emails.csv', 'sender_emails')

