import sqlite3

# Initialize the database
def init_db():
    conn = sqlite3.connect('voip.db')
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL)''')

    # Create contacts table
    cursor.execute('''CREATE TABLE IF NOT EXISTS contacts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        contact_name TEXT NOT NULL,
                        FOREIGN KEY(user_id) REFERENCES users(id))''')

    conn.commit()
    conn.close()

# Register a new user
def register_user(username, password):
    try:
        conn = sqlite3.connect('voip.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        # Username already exists
        return False

# Authenticate an existing user
def authenticate_user(username, password):
    conn = sqlite3.connect('voip.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    conn.close()
    return user  # Returns user ID if credentials are valid, otherwise None

# Add a new contact
def add_contact(user_id, contact_name):
    conn = sqlite3.connect('voip.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO contacts (user_id, contact_name) VALUES (?, ?)', (user_id, contact_name))
    conn.commit()
    conn.close()

# Remove an existing contact
def remove_contact(user_id, contact_name):
    conn = sqlite3.connect('voip.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM contacts WHERE user_id = ? AND contact_name = ?', (user_id, contact_name))
    conn.commit()
    conn.close()

# Retrieve contacts for a specific user
def get_contacts(user_id):
    conn = sqlite3.connect('voip.db')
    cursor = conn.cursor()
    cursor.execute('SELECT contact_name FROM contacts WHERE user_id = ?', (user_id,))
    contacts = cursor.fetchall()
    conn.close()
    return [contact[0] for contact in contacts]  # Return a list of contact names
