from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import torchaudio
import numpy as np
import os
from flask_cors import CORS
import subprocess
import whisper

# Set audio backend to soundfile
torchaudio.set_audio_backend("soundfile")

app = Flask(__name__)
CORS(app)

ALLOWED_EXTENSIONS = {'mp3', 'wav', 'webm'}

UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_to_wav(mp3_data):
    # Save the webm audio data to a file
    mp3_path = os.path.join(app.config['UPLOAD_FOLDER'], 'audio.mp3')
    with open(mp3_path, 'wb') as webm_file:
        webm_file.write(mp3_data)

    # Use ffmpeg to convert the webm audio to wav format
    wav_path = os.path.join(app.config['UPLOAD_FOLDER'], 'audio.wav')
    subprocess.run(['ffmpeg', '-i', mp3_path, wav_path])

    # Read the converted wav data
    with open(wav_path, 'rb') as wav_file:
        wav_data = wav_file.read()

    # Clean up temporary files
    os.remove(mp3_path)
    os.remove(wav_path)

    return wav_data

def transcribe(audio_data):
    try:
        model = whisper.load_model("base")
        converted_audio_data = convert_to_wav(audio_data)
        
        audio_np = np.frombuffer(converted_audio_data, dtype=np.int16)
        audio_float32 = audio_np.astype(np.float32) / np.iinfo(np.int16).max
        transcription = model.transcribe(audio_float32)
        print(transcription)
        return transcription
    except Exception as e:
        print(f"Error in transcription: {e}")
        raise

@app.route('/whisper_transcription', methods=['POST'])
def whisper_transcription():
    if 'file' not in request.files:
        return jsonify({"type": "POST", "message": "No file part in the request"}), 400

    file = request.files['file']

    if not file.filename:
        return jsonify({"type": "POST", "message": "No file selected for uploading"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        audio_data = file.read()

        try:
            transcription = transcribe(audio_data)
            result = jsonify({
                "type": "POST",
                "transcription": transcription,
                "audioFileName": filename
            })
            result.headers.add('Access-Control-Allow-Origin', '*')
            return result
        except Exception as e:
            return jsonify({"type": "POST", "message": str(e)}), 500

    return jsonify({"type": "POST", "message": "File format not allowed"}), 400

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)
