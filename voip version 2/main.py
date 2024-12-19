import socket
import pyaudio
import threading

# Constants
HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 12346  # Use the same port as the client
BUFF_SIZE = 1024  # Buffer size for audio chunks


def handle_client(conn, addr):
    print(f"Connected by {addr}")

    p = pyaudio.PyAudio()  # Create a pyaudio instance
    stream_in = p.open(format=pyaudio.paInt16, channels=1, rate=44100, output=True, frames_per_buffer=BUFF_SIZE)
    stream_out = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=BUFF_SIZE)

    # Create two-way communication
    while True:
        data = stream_out.read(BUFF_SIZE)
        conn.sendall(data)

        received_data = conn.recv(BUFF_SIZE)
        stream_in.write(received_data)

    stream_out.stop_stream()
    stream_out.close()
    stream_in.stop_stream()
    stream_in.close()
    p.terminate()
    conn.close()


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"Server listening on {HOST}:{PORT}")

    while True:
        conn, addr = server_socket.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

    server_socket.close()


if __name__ == "__main__":
    start_server()
