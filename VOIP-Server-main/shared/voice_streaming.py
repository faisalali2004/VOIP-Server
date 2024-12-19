import socket
import pyaudio
import time

def send_audio(client_socket, addr, is_calling):
    audio_stream = pyaudio.PyAudio()
    stream = audio_stream.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)

    while is_calling:
        data = stream.read(1024)  # Read raw audio data from the microphone
        try:
            client_socket.sendto(data, addr)  # Send raw audio data without encoding
        except Exception as e:
            print(f"Error sending audio: {e}")
            break
    stream.stop_stream()
    stream.close()

def receive_audio(client_socket, addr):
    audio_stream = pyaudio.PyAudio()
    stream = audio_stream.open(format=pyaudio.paInt16, channels=1, rate=16000, output=True, frames_per_buffer=1024)

    while True:
        try:
            data, _ = client_socket.recvfrom(1024)  # Receiving raw audio data from the socket
            stream.write(data)  # Play the received raw audio data
        except Exception as e:
            print(f"Error receiving audio: {e}")
            break
    stream.stop_stream()
    stream.close()
