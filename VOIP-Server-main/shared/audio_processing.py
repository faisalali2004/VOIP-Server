import socket
import threading
import logging
import pyaudio

# Setup logging
logging.basicConfig(level=logging.INFO)

# Constants
SAMPLE_RATE = 16000
CHANNELS = 1
FORMAT = pyaudio.paInt16  # 16-bit audio format
FRAMES_PER_BUFFER = 1024

# Function to handle incoming audio stream from the client
def handle_audio_stream(client_socket, addr, is_calling):
    audio_stream = pyaudio.PyAudio()
    stream = audio_stream.open(format=FORMAT, channels=CHANNELS, rate=SAMPLE_RATE, input=True, output=True, frames_per_buffer=FRAMES_PER_BUFFER)

    while is_calling:
        data = stream.read(FRAMES_PER_BUFFER)  # Read raw PCM data from input stream (microphone)
        try:
            client_socket.sendto(data, addr)  # Sending raw audio over UDP
        except Exception as e:
            logging.error(f"Error sending audio data: {e}")
            break

    stream.stop_stream()
    stream.close()

def handle_client(client_socket, addr):
    try:
        client_socket.send(b"Welcome to VOIP Server. Please authenticate.\n")
        client_socket.send(b"Enter username: ")
        username = client_socket.recv(1024).decode().strip()
        client_socket.send(b"Enter password: ")
        password = client_socket.recv(1024).decode().strip()

        if username == "test" and password == "password":  # Simple mock authentication
            client_socket.send(b"Login successful.\n")
            is_calling = True  # Call flag for handling the audio stream
            while is_calling:
                handle_audio_stream(client_socket, addr, is_calling)
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
    start_server('localhost', 5000)
