from flask import Flask, request, jsonify
import os
import subprocess
from werkzeug.utils import secure_filename
from flask_cors import CORS
import whisper
import logging
import numpy as np  # NumPy for numerical processing

app = Flask(__name__)
CORS(app)

ALLOWED_EXTENSIONS = {'wav', 'mp3'}  # Only allow WAV files
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def transcribe(audio_data):
    try:
        model = whisper.load_model("medium")
        # model = whisper.load_model(model_name)
        result = model.transcribe(audio_data)
        print(result)
        return result["text"]
    except Exception as e:
        logging.error(f"Error processing audio: {e}")
        return None

def convert_to_mp3(wav_data):
    # Save the WAV audio data to a file
    wav_path = os.path.join(app.config['UPLOAD_FOLDER'], 'audio.wav')
    with open(wav_path, 'wb') as wav_file:
        wav_file.write(wav_data)

    # Use FFmpeg to convert WAV to MP3
    mp3_path = os.path.join(app.config['UPLOAD_FOLDER'], 'audio.mp3')
    subprocess.run(['ffmpeg', '-i', wav_path, '-q:a', '0', '-map', 'a', mp3_path])

    # Read the converted MP3 data
    with open(mp3_path, 'rb') as mp3_file:
        mp3_data = mp3_file.read()

    # Clean up temporary files
    os.remove(wav_path)
    os.remove(mp3_path)

    return mp3_data

@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    if 'file' not in request.files:
        return jsonify({"message": "No file part in the request"}), 400

    file = request.files['file']

    if not file.filename:
        return jsonify({"message": "No file selected for uploading"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        wav_data = file.read()

        try:
            mp3_data = convert_to_mp3(wav_data)
            
            # Save the MP3 data to a file
            mp3_path = os.path.join(app.config['UPLOAD_FOLDER'], 'audio_converted.mp3')
            with open(mp3_path, 'wb') as mp3_file:
                mp3_file.write(mp3_data)

            result = transcribe(mp3_path)
            
            return jsonify({"message": "File successfully uploaded", "result": result}), 200
        except Exception as e:
            return jsonify({"message": str(e)}), 500

    return jsonify({"message": "File format not allowed"}), 400

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)
