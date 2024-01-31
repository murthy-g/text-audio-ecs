# 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
import os
import logging
import boto3
from flask import Flask, request, jsonify
from torch import tensor, no_grad, argmax, float
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
from torchaudio.transforms import Resample
import librosa

# Setup logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# Constants
s3_bucket_name = 'audiobucket-infusion'
s3_audio_key = 'audio/output.wav'
s3_local_filename = "./downloaded_file.wav"
model_name = "facebook/wav2vec2-base-960h"

# Initialize AWS S3 client
s3 = boto3.client('s3', 
                  aws_access_key_id='',
                  aws_secret_access_key='')

# Initialize pre-trained model and processor
processor = Wav2Vec2Processor.from_pretrained(model_name)
model = Wav2Vec2ForCTC.from_pretrained(model_name)

@app.route('/whisper', methods=['POST'])
def handler():
    try:
        logging.info(f"Attempting to download from {s3_bucket_name}/{s3_audio_key} to {s3_local_filename}")
        s3.download_file(s3_bucket_name, s3_audio_key, s3_local_filename)
    except Exception as e:
        logging.error(f"Error downloading from S3: {e}")
        return jsonify({"error": "Error downloading from S3"}), 500

    if not os.path.exists(s3_local_filename):
        logging.error(f"File {s3_local_filename} does not exist.")
        return jsonify({"error": "File does not exist"}), 400

    try:
        # torchaudio.load(s3_local_filename)
        waveform, original_sampling_rate = librosa.load(s3_local_filename, sr=None)
        print(waveform, original_sampling_rate)
        # waveform, original_sampling_rate = torchaudio.load(s3_local_filename)

        waveform = tensor(waveform, dtype=float)
        print(waveform)
        target_sampling_rate = 16000
        resampler = Resample(orig_freq=original_sampling_rate, new_freq=target_sampling_rate)
        resampled_waveform = resampler(waveform)
        print(resampled_waveform)
        inputs = processor(resampled_waveform.numpy(), sampling_rate=target_sampling_rate, return_tensors="pt")
        print(inputs.input_values)
        with no_grad():
            try:
                logging.info("Starting model inference...")
                logits = model(input_values=inputs.input_values).logits
                logging.info("Ended model inference...")
                # model.eval()
                logging.info("Model inference completed.")
            except Exception as e:
                logging.error(f"Error running model inference: {e}")
                return jsonify({"error": "Error running model inference"}), 500

        # print(logits)
        predicted_ids = argmax(logits, dim=-1)
        print(predicted_ids)
        predicted_text = processor.batch_decode(predicted_ids)
        print(predicted_text)
        
        return jsonify({"transcription": predicted_text[0]})
        # return "success"
    except Exception as e:
        logging.error(f"Error processing audio: {e}")
        return jsonify({"error": "Error processing audio"}), 500


# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000)

handler()
