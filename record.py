import sounddevice as sd
import numpy as np
import wavio

# Parameters
RATE = 44100  # Sample rate
CHANNELS = 1  # Stereo
SECONDS_PER_CHUNK = 5  # Duration of each chunk
DTYPE = np.int16  # Data type for audio

def record_and_save_chunk(filename):
    """Record and save a chunk of audio."""
    print(f"Recording chunk: {filename}")
    audio_chunk = sd.rec(int(SECONDS_PER_CHUNK * RATE), samplerate=RATE, channels=CHANNELS, dtype=DTYPE)
    sd.wait()  # Wait for the recording to finish
    wavio.write(filename, audio_chunk, RATE)

if __name__ == "__main__":
    print(f"Recording chunks of {SECONDS_PER_CHUNK} seconds each.")
    print("Press Ctrl+C to stop recording.")
    
    chunk_counter = 1
    while True:
        try:
            filename = f"chunk_{chunk_counter}.wav"
            record_and_save_chunk(filename)
            chunk_counter += 1
        except KeyboardInterrupt:
            print("\nRecording stopped.")
            break
