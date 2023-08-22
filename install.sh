#create python env
python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip

brew install ffmpeg
pip install -r requirements.txt
# pip install -U openai-whisper