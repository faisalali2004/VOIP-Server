import socket
import pyaudio
import opus
import time

def send_audio(client_socket, addr, is_calling):
    audio_stream = pyaudio.PyAudio()
    stream = audio_stream.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)

    while is_calling:
        data = stream.read(1024)
        try:
            encoded_data = opus.encode(data)  # Compress audio using Opus codec
            client_socket.sendto(encoded_data, addr)
        except Exception as e:
            print(f"Error encoding audio: {e}")
            break
    stream.stop_stream()
    stream.close()

def receive_audio(client_socket, addr):
    audio_stream = pyaudio.PyAudio()
    stream = audio_stream.open(format=pyaudio.paInt16, channels=1, rate=16000, output=True, frames_per_buffer=1024)

    while True:
        try:
            data, _ = client_socket.recvfrom(1024)  # Receiving data from another client
            decoded_data = opus.decode(data)  # Decompress the audio data
            stream.write(decoded_data)
        except Exception as e:
            print(f"Error receiving audio: {e}")
            break
    stream.stop_stream()
    stream.close()
