import socket
import threading
import pyaudio

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 12346
BUFF_SIZE = 1024
SAMPLE_RATE = 44100
CHANNELS = 1


def audio_stream(conn):
    # Handle real-time audio streaming during a call.
    audio = pyaudio.PyAudio()

    # Create audio streams
    audiostream_out = audio.open(
        format=pyaudio.paInt16,
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=BUFF_SIZE,
    )
    audiostream_in = audio.open(
        format=pyaudio.paInt16,
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        output=True,
        frames_per_buffer=BUFF_SIZE,
    )

    def send_audio():
        while True:
            try:
                data = audiostream_out.read(BUFF_SIZE, exception_on_overflow=False)
                conn.sendall(data)
            except Exception:
                break

    def receive_audio():
        while True:
            try:
                data = conn.recv(BUFF_SIZE)
                if not data:
                    break
                audiostream_in.write(data)
            except Exception:
                break

    # Start audio streams in separate threads
    send_thread = threading.Thread(target=send_audio)
    receive_thread = threading.Thread(target=receive_audio)
    send_thread.start()
    receive_thread.start()

    send_thread.join()
    receive_thread.join()

    # Close streams
    audiostream_out.stop_stream()
    audiostream_out.close()
    audiostream_in.stop_stream()
    audiostream_in.close()
    audio.terminate()


def handle_server_responses(conn):
    # Listen to messages from the server
    while True:
        try:
            message = str(conn.recv(BUFF_SIZE).decode("utf-8"))
            if message:
                print(message)
                if 'Type "yes" to accept' in message:
                    response = input("Your response: ").strip()
                    conn.send(response.encode("utf-8"))
                elif "Call started" in message:
                    print("Call initiated. Streaming audio...")
                    audio_stream(conn)
                    print("Call ended.")
            else:
                break
        except ConnectionResetError:
            print("Disconnected from server.")
            break


def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))
    print(f"Connected to server {SERVER_HOST}:{SERVER_PORT}")

    # Start a thread to handle server responses
    threading.Thread(
        target=handle_server_responses, args=(client_socket,), daemon=True
    ).start()

    while True:
        try:
            user_input = input().strip()
            if user_input.lower() == "exit":
                client_socket.send(user_input.encode("utf-8"))
                print("Exiting...")
                break
            client_socket.send(user_input.encode("utf-8"))
        except KeyboardInterrupt:
            print("Exiting...")
            client_socket.send(b"exit")
            break
        except ConnectionResetError:
            print("Connection lost.")
            break

    client_socket.close()


if __name__ == "__main__":
    main()
