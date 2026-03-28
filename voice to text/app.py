from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import os
import tempfile
import speech_recognition as sr
from pydub import AudioSegment
from gtts import gTTS

app = Flask(__name__)
CORS(app)

# --------------------------
# Home page
# --------------------------
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

    # Save webm file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp:
        audio_file.save(temp.name)
        webm_path = temp.name

    wav_path = webm_path.replace('.webm', '.wav')

    try:
        # Convert webm → wav
        audio_segment = AudioSegment.from_file(webm_path)
        audio_segment = audio_segment.set_channels(1)
        audio_segment = audio_segment.set_frame_rate(16000)
        audio_segment.export(wav_path, format='wav')

        # Recognize speech
        with sr.AudioFile(wav_path) as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.record(source)

        text = recognizer.recognize_google(audio)
        return jsonify({'text': text})

    except sr.UnknownValueError:
        return jsonify({'error': 'Could not understand, please speak clearly'}), 400

    except sr.RequestError as e:
        return jsonify({'error': 'Internet needed: ' + str(e)}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        try:
            os.remove(webm_path)
            os.remove(wav_path)
        except:
            pass

# --------------------------
# 🔊 Text → Voice using gTTS
# --------------------------
from gtts import gTTS
import tempfile
from flask import send_file, jsonify, request

@app.route('/text-to-voice', methods=['POST'])
def text_to_voice():
    data = request.get_json()
    text = data.get('text', '')

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    try:
        # gTTS generates speech from text
        tts = gTTS(text=text, lang='en', slow=False)  # slow=False = normal speed
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp:
            tts.save(temp.name)
            temp_path = temp.name

        return send_file(temp_path, mimetype="audio/mpeg")

    except Exception as e:
        return jsonify({'error': str(e)}), 500
# --------------------------
# Run Flask app
# --------------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)