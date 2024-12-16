import opuslib
import numpy as np

# Set Opus codec parameters
SAMPLE_RATE = 16000
FRAME_SIZE = 1024

def encode(audio_data):
    """
    Encodes raw audio data using Opus codec.
    :param audio_data: The raw audio data (bytes)
    :return: Encoded audio data
    """
    encoder = opuslib.Encoder(SAMPLE_RATE, 1, opuslib.APPLICATION_VOIP)
    # Convert audio to numpy array
    audio_np = np.frombuffer(audio_data, dtype=np.int16)
    encoded_data = encoder.encode(audio_np, FRAME_SIZE)
    return encoded_data

def decode(encoded_data):
    """
    Decodes Opus encoded audio data.
    :param encoded_data: The encoded audio data
    :return: Decoded raw audio data
    """
    decoder = opuslib.Decoder(SAMPLE_RATE, 1)
    decoded_audio = decoder.decode(encoded_data, FRAME_SIZE)
    return decoded_audio.tobytes()
