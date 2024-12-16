import socket
import threading
import sqlite3
import logging
import ssl
import pyaudio
import opus
import time

# Setup logging
logging.basicConfig(level=logging.INFO)

# Database Setup (SQLite for simplicity)
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, status TEXT)''')
    conn.commit()
    conn.close()

def store_user(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (username, password, status) VALUES (?, ?, ?)', (username, password, 'offline'))
    conn.commit()
    conn.close()

def authenticate_user(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
    result = cursor.fetchone()
    conn.close()
    return result

# Voice streaming setup using UDP
def handle_audio_stream(client_socket, addr, is_calling):
    audio_stream = pyaudio.PyAudio()
    stream = audio_stream.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, output=True, frames_per_buffer=1024)
    
    while is_calling:
        data = stream.read(1024)
        try:
            client_socket.sendto(data, addr)  # Sending audio over UDP
        except Exception as e:
            logging.error(f"Error sending audio data: {e}")
            break
    stream.stop_stream()
    stream.close()

def handle_client(client_socket, addr):
    try:
        client_socket.send(b"Welcome to VOIP Server. Please authenticate.\n")
        # Simple authentication
        client_socket.send(b"Enter username: ")
        username = client_socket.recv(1024).decode().strip()
        client_socket.send(b"Enter password: ")
        password = client_socket.recv(1024).decode().strip()

        user = authenticate_user(username, password)
        if user:
            client_socket.send(b"Login successful.\n")
            # Update user status to online
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET status=? WHERE username=?', ('online', username))
            conn.commit()
            conn.close()
            
            is_calling = True  # Set the flag for call ongoing
            while is_calling:
                handle_audio_stream(client_socket, addr, is_calling)  # Handle the audio streaming during a call

        else:
            client_socket.send(b"Invalid credentials.\n")
    except Exception as e:
        logging.error(f"Error handling client {addr}: {e}")
    finally:
        client_socket.close()

def start_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))
    logging.info(f"Server started at {host}:{port}")

    while True:
        data, addr = server_socket.recvfrom(1024)
        logging.info(f"Received connection from {addr}")
        threading.Thread(target=handle_client, args=(server_socket, addr)).start()

if __name__ == "__main__":
    init_db()  # Initialize DB
    start_server('localhost', 5000)
