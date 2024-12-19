import socket
import pyaudio
import threading

# Constants
SERVER_HOST = '127.0.0.1'  # Server IP
SERVER_PORT = 12346  # Use the same port as the server
BUFF_SIZE = 1024  # Buffer size for audio chunks


def audio_capture(sock):
    p = pyaudio.PyAudio()  # Create a pyaudio instance
    stream_out = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=BUFF_SIZE)
    stream_in = p.open(format=pyaudio.paInt16, channels=1, rate=44100, output=True, frames_per_buffer=BUFF_SIZE)

    while True:
        data = stream_out.read(BUFF_SIZE)
        sock.sendall(data)

        received_data = sock.recv(BUFF_SIZE)
        stream_in.write(received_data)

    stream_out.stop_stream()
    stream_out.close()
    stream_in.stop_stream()
    stream_in.close()
    p.terminate()


def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))
    print(f"Connected to server {SERVER_HOST}:{SERVER_PORT}")

    threading.Thread(target=audio_capture, args=(client_socket,)).start()


if __name__ == "__main__":
    start_client()
