import sounddevice as sd
import numpy as np
import wavio
import os
import logging
import boto3
from torch import tensor, no_grad, argmax, float
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
from torchaudio.transforms import Resample
import librosa
from pydub import AudioSegment


# Setup logging
logging.basicConfig(level=logging.INFO)

# Constants for recording
RATE = 44100
CHANNELS = 1
SECONDS_PER_CHUNK = 5
DTYPE = np.int16

s3_bucket_name = 'audiobucket-infusion'
s3_audio_key = 'audio/output.wav'
model_name = "facebook/wav2vec2-base-960h"

# Initialize AWS S3 client
s3 = boto3.client('s3', aws_access_key_id='YOUR_ACCESS_KEY', aws_secret_access_key='YOUR_SECRET_KEY')

# Initialize pre-trained model and processor
processor = Wav2Vec2Processor.from_pretrained(model_name)
model = Wav2Vec2ForCTC.from_pretrained(model_name)


def concatenate_wav_files(filenames):
    """Concatenate multiple WAV files into one."""
    combined = AudioSegment.empty()
    for filename in filenames:
        audio_segment = AudioSegment.from_wav(filename)
        combined += audio_segment
    return combined


def record_and_save_chunk(filename):
    print(f"Recording chunk: {filename}")
    audio_chunk = sd.rec(int(SECONDS_PER_CHUNK * RATE), samplerate=RATE, channels=CHANNELS, dtype=DTYPE)
    sd.wait()
    wavio.write(filename, audio_chunk, RATE)
    return filename

def transcribe_audio(filename):
    # The transcription logic goes here, similar to your handler() function
    try:
        waveform, original_sampling_rate = librosa.load(filename, sr=None)
        waveform = tensor(waveform, dtype=float)
        target_sampling_rate = 16000
        resampler = Resample(orig_freq=original_sampling_rate, new_freq=target_sampling_rate)
        resampled_waveform = resampler(waveform)
        inputs = processor(resampled_waveform.numpy(), sampling_rate=target_sampling_rate, return_tensors="pt")

        with no_grad():
            logits = model(input_values=inputs.input_values).logits
        predicted_ids = argmax(logits, dim=-1)
        predicted_text = processor.batch_decode(predicted_ids)
        return predicted_text[0]
    except Exception as e:
        logging.error(f"Error processing audio: {e}")
        return None


if __name__ == "__main__":
    print(f"Recording chunks of {SECONDS_PER_CHUNK} seconds each.")
    print("Press Ctrl+C to stop recording.")
    
    chunk_counter = 1
    recorded_files = []
    try:
        while True:
            filename = f"chunk_{chunk_counter}.wav"
            recorded_chunk_filename = record_and_save_chunk(filename)
            recorded_files.append(recorded_chunk_filename)
            transcription = transcribe_audio(recorded_chunk_filename)
            if transcription:
                print(f"Transcription for {filename}: {transcription}")
            chunk_counter += 1
    except KeyboardInterrupt:
        print("\nRecording stopped.")

        # Combine all recorded chunks into one WAV file
        print("Combining all WAV chunks...")
        combined_audio = concatenate_wav_files(recorded_files)
        combined_filename = "combined_audio.wav"
        combined_audio.export(combined_filename, format="wav")

        # Now you can transcribe the combined_audio if needed
        transcription = transcribe_audio(combined_filename)
        if transcription:
            print(f"Transcription for the combined audio: {transcription}")