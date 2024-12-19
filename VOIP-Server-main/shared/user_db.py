import sqlite3

# Path to your SQLite database
DATABASE_PATH = 'users.db'

def create_table():
    """Create the users table if it doesn't exist"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL
    );
    ''')

    conn.commit()
    conn.close()

def authenticate_user(username, password):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Ensure the users table exists before executing the query
    create_table()

    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        return True
    else:
        return False

def create_user(username, password):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Ensure the users table exists before creating the user
    create_table()

    # Insert a new user
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()
