from flask import Flask, request, jsonify
import os
import logging
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import librosa
from torchaudio.transforms import Resample
from torch import tensor, no_grad, argmax, float

# ... [rest of your imports]

app = Flask(__name__)

# Directory for uploads
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize pre-trained model and processor
model_name = "facebook/wav2vec2-base-960h"
processor = Wav2Vec2Processor.from_pretrained(model_name)
model = Wav2Vec2ForCTC.from_pretrained(model_name)

ALLOWED_EXTENSIONS = {'wav', 'mp3'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def transcribe_audio(filename):
    # The transcription logic
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

@app.route('/transcribe_combined', methods=['POST'])
def transcribe_combined_audio_route():
    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({"type": "POST", "message": "No file part in the request"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"type": "POST", "message": "No file selected for uploading"}), 400

    if file and allowed_file(file.filename):
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)

        try:
            transcription = transcribe_audio(filename)
            print(transcription)
            if transcription:
                response = jsonify({
                    "type": "POST",
                    "transcription": transcription,
                    "audioFileName": file.filename
                })

                response.headers.add("Access-Control-Allow-Origin", "*")
                return response
            else:
                return jsonify({"type": "POST", "message": "Error during transcription"}), 500
        except Exception as e:
            return jsonify({"type": "POST", "message": str(e)}), 500
    else:
        return jsonify({"type": "POST", "message": "File format not allowed"}), 400

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
