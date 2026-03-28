from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import os
import tempfile
import speech_recognition as sr
from pydub import AudioSegment
from gtts import gTTS


app = Flask(__name__)
CORS(app)

last_voice_type = "male"

from deepmultilingualpunctuation import PunctuationModel

punct_model = PunctuationModel()


# --------------------------
# Home page
# --------------------------

def improve_text(text):
    try:
        result = punct_model.restore_punctuation(text)
        return result
    except:
        return text

def detect_voice_type(wav_path):
    import wave
    import numpy as np

    with wave.open(wav_path, "rb") as wf:
        frames = wf.readframes(wf.getnframes())
        audio = np.frombuffer(frames, dtype=np.int16)

    energy = np.mean(np.abs(audio))

    if energy > 1200:
        return "female"
    else:
        return "male"

@app.route('/')
def home():
    return render_template('index.html')

# --------------------------
# 🎤 Voice → Text
# --------------------------
@app.route('/voice-to-text', methods=['POST'])
def voice_to_text():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file sent'}), 400

    audio_file = request.files['audio']
    recognizer = sr.Recognizer()

    # Save file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp:
        audio_file.save(temp.name)
        webm_path = temp.name

    wav_path = webm_path.replace('.webm', '.wav')

    try:
        print("Step 1: File received")

        # 🔥 Use FFmpeg (NO pydub)
        import subprocess
        subprocess.run(
            ["ffmpeg", "-y", "-i", webm_path, "-ac", "1", "-ar", "16000", wav_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        print("Step 2: Converted")

        global last_voice_type
        last_voice_type = detect_voice_type(wav_path)
        print("Detected voice:", last_voice_type)

        # 🔥 Read small audio only (NO hanging)
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)

# 🔥 Split into chunks
        chunk_length = 5000  # 5 seconds
        audio_array = audio_data.get_raw_data()

        import math

        sample_rate = audio_data.sample_rate
        sample_width = audio_data.sample_width

        chunk_size = int(sample_rate * sample_width * (chunk_length / 1000))

        chunks = [
            audio_array[i:i + chunk_size]
            for i in range(0, len(audio_array), chunk_size)
        ]

        full_text = ""

        for chunk in chunks:
            try:
                chunk_audio = sr.AudioData(chunk, sample_rate, sample_width)
                text = recognizer.recognize_google(chunk_audio, language='en-IN')
                full_text += text + " "
            except:
                pass

        text = full_text.strip()
        text = improve_text(text)

        print("Step 4: Done")

        return jsonify({'text': text})

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({'error': str(e)}), 500

    finally:
        try:
            os.remove(webm_path)
            os.remove(wav_path)
        except:
            pass

# --------------------------
# 🔊 Text → Voice
# --------------------------
@app.route('/text-to-voice', methods=['POST'])
def text_to_voice():
    global last_voice_type

    data = request.get_json()
    text = data.get('text', '')

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    try:
        import edge_tts
        import asyncio

        # 🔥 Smart voice selection
        if last_voice_type == "female":
            voice = "en-IN-NeerjaNeural"
        else:
            voice = "en-IN-PrabhatNeural"

        temp_path = tempfile.mktemp(suffix=".mp3")

        async def generate():
            communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate="+5%",      # speed (natural)
            pitch="+2Hz"     # tone (human feel)
            )
            await communicate.save(temp_path)

        asyncio.run(generate())

        return send_file(temp_path, mimetype="audio/mpeg")

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --------------------------
# Run Flask app
# --------------------------
if __name__ == '__main__':
    app.run(debug=True)