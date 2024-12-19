# Configuration for the VOIP Server

# Server Host and Port
HOST = 'localhost'
PORT = 5000

# Audio Streaming Configuration
AUDIO_FORMAT = 'paInt16'  # Format for audio (using 16-bit PCM)
CHANNELS = 1              # Mono channel
RATE = 16000              # Sampling rate (16kHz)
BUFFER_SIZE = 1024        # Frames per buffer

# Database file
DB_FILE = 'users.db'
