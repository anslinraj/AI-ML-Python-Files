from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import speech_recognition as sr
import pyttsx3
import os
import tempfile
import threading

app = Flask(__name__)
CORS(app)

# Text to speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1.0)

# ─── ROUTES ───────────────────────────────────────

# Home page
@app.route('/')
def home():
    return render_template('index.html')


# Voice → Text
@app.route('/voice-to-text', methods=['POST'])
def voice_to_text():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file sent'}), 400

    audio_file = request.files['audio']
    recognizer = sr.Recognizer()

    # Save as webm
    with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp:
        audio_file.save(temp.name)
        webm_path = temp.name

    wav_path = webm_path.replace('.webm', '.wav')

    try:
        # Convert webm to wav
        from pydub import AudioSegment
        audio_segment = AudioSegment.from_file(webm_path)
        audio_segment = audio_segment.set_channels(1)
        audio_segment = audio_segment.set_frame_rate(16000)
        audio_segment.export(wav_path, format='wav')

        # Now read the wav file
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
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Conversion error: ' + str(e)}), 500

    finally:
        try:
            os.remove(webm_path)
        except:
            pass
        try:
            os.remove(wav_path)
        except:
            pass

# Text → Voice
@app.route('/text-to-voice', methods=['POST'])
def text_to_voice():
    data = request.get_json()
    text = data.get('text', '')

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp:
        temp_path = temp.name

    def speak():
        engine.save_to_file(text, temp_path)
        engine.runAndWait()

    t = threading.Thread(target=speak)
    t.start()
    t.join()

    return send_file(temp_path, mimetype='audio/mpeg',
                     as_attachment=False,
                     download_name='output.mp3')


# ─── RUN ──────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True)