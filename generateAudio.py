from flask import Flask, request, jsonify
import json
import boto3
from gtts import gTTS
import os

app = Flask(__name__)

# Initialize the Boto3 S3 client
s3 = boto3.client('s3', aws_access_key_id='AKIA5B6GM6M7NNHMUQNU',
                  aws_secret_access_key='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')

@app.route('/generate-audio', methods=['POST'])
def generate_audio():
    try:
        data = request.json  # Get JSON payload from the incoming request
        if 'text' not in data:
            return jsonify({"error": "No text provided"}), 400

        text = data['text']
        print(text)
        # return jsonify({"text": text}), 200

        # # Generate the audio
        tts = gTTS(text=text, lang='en')
        tts.volume = 2.0  # Increase the volume to create high-amplitude audio
        audio_path = "output.wav"
        
        # print(audio_path)
        tts.save("./" + audio_path)
        # # Upload 'output.wav' to S3 bucket
        s3_bucket_name = 'audiobucket-infusion'
        s3_audio_key = 'audio/output.wav'
        print(s3_bucket_name)
        s3.upload_file(audio_path, s3_bucket_name, s3_audio_key)

        # # Return the S3 URL of the uploaded audio file as a response
        s3_audio_url = f"https://{s3_bucket_name}.s3.amazonaws.com/{s3_audio_key}"
        return jsonify({"audio_url": s3_audio_url}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
