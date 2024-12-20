import socket
import threading
import sqlite3

HOST = "0.0.0.0"
PORT = 12346
BUFF_SIZE = 1024
USER_DB = "users.db"

clients = {}
user_sessions = {}


def initialize_database():
    # Initialize the SQLite database
    conn = sqlite3.connect(USER_DB)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                      username TEXT PRIMARY KEY,
                      password TEXT NOT NULL)""")
    conn.commit()
    conn.close()


def authenticate_user(username, password):
    # Check if username and password match in the database
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?", (username, password)
    )
    result = cursor.fetchone()
    conn.close()
    return result is not None


def register_user(username, password):
    # Register a new user in the database
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)", (username, password)
        )
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    conn.close()
    return success


def notify_disconnection(username):
    # Notify other users that a user has disconnected
    for user, session in user_sessions.items():
        if user != username:
            try:
                session["connection"].send(
                    f"{username} has disconnected.".encode("utf-8")
                )
            except Exception:
                pass


def handle_client(conn, addr):
    conn.send(b'Welcome! Type "login" to log in or "register" to create an account: ')
    while True:
        try:
            choice = conn.recv(BUFF_SIZE).decode("utf-8").strip()
            if choice == "login":
                conn.send(b"Username: ")
                username = conn.recv(BUFF_SIZE).decode("utf-8").strip()
                conn.send(b"Password: ")
                password = conn.recv(BUFF_SIZE).decode("utf-8").strip()

                if authenticate_user(username, password):
                    conn.send(
                        b'Login successful. You are idle. Type a username to communicate or "exit" to logout: '
                    )
                    user_sessions[username] = {
                        "ip": addr[0],
                        "port": addr[1],
                        "status": "online",
                        "connection": conn,
                    }
                    clients[conn] = username
                    break
                else:
                    conn.send(b"Invalid credentials. Try again: ")
            elif choice == "register":
                conn.send(b"Choose a username: ")
                username = conn.recv(BUFF_SIZE).decode("utf-8").strip()
                conn.send(b"Choose a password: ")
                password = conn.recv(BUFF_SIZE).decode("utf-8").strip()

                if register_user(username, password):
                    conn.send(b'Registration successful! Type "login" to log in: ')
                else:
                    conn.send(b"Username already exists. Try again: ")
            else:
                conn.send(b'Invalid option. Type "login" or "register": ')

        except ConnectionResetError:
            break

    username = clients.get(conn)
    while True:
        try:
            message = conn.recv(BUFF_SIZE).decode("utf-8").strip()
            if message == "exit":
                conn.send(b"Goodbye!")
                notify_disconnection(username)
                break
            elif (
                message in user_sessions
                and user_sessions[message]["status"] == "online"
            ):
                conn.send(
                    f"Request sent to {message}. Waiting for response...".encode(
                        "utf-8"
                    )
                )
                target_conn = user_sessions[message]["connection"]
                target_conn.send(
                    f'{username} wants to communicate. Type "yes" to accept or "no" to decline: '.encode(
                        "utf-8"
                    )
                )

                response = target_conn.recv(BUFF_SIZE).decode("utf-8").strip()
                if response == "yes":
                    conn.send(b'Call started. Type "exit" to end the call.')
                    target_conn.send(b'Call started. Type "exit" to end the call.')

                    def relay_data(source, target):
                        while True:
                            try:
                                data = source.recv(BUFF_SIZE)
                                if (
                                    data.decode("utf-8", errors="ignore").strip()
                                    == "exit"
                                ):
                                    source.send(b"Call ended.")
                                    target.send(b"Call ended.")
                                    break
                                target.sendall(data)
                            except Exception:
                                break

                    # Create threads for bidirectional communication
                    thread1 = threading.Thread(
                        target=relay_data, args=(conn, target_conn)
                    )
                    thread2 = threading.Thread(
                        target=relay_data, args=(target_conn, conn)
                    )
                    thread1.start()
                    thread2.start()
                    thread1.join()
                    thread2.join()

                else:
                    conn.send(f"{message} declined the request.".encode("utf-8"))
            else:
                conn.send(b"No such user online. Try again: ")
        except ConnectionResetError:
            break

    # Cleanup after disconnection
    if username in user_sessions:
        user_sessions.pop(username)
    if conn in clients:
        clients.pop(conn)
    notify_disconnection(username)
    conn.close()


def main():
    initialize_database()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"Server listening on {HOST}:{PORT}")

    while True:
        conn, addr = server_socket.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

    server_socket.close()


if __name__ == "__main__":
    main()
