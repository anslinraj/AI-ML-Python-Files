# 🎙️ VoiceForge — AI Voice Web App

A full-stack web application that converts **voice to text** and **text to voice** using Python and Flask.

---

## 🚀 Features

- 🎙️ Record live voice and convert to text
- 📁 Upload any audio file (MP3, WAV, WEBM, OGG, M4A)
- 🔊 Convert any text to speech
- ⬇️ Download generated audio
- 🌐 Clean landing page with live demo

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Speech to Text | SpeechRecognition + Google API |
| Text to Speech | pyttsx3 |
| Audio Conversion | pydub + ffmpeg |
| Frontend | HTML, CSS, JavaScript |

---

## 📁 Project Structure
```
voiceforge/
│
├── app.py                  ← Flask backend
├── requirements.txt        ← All dependencies
├── README.md               ← You are here
│
├── templates/
│   └── index.html          ← Landing page + App UI
│
└── static/
    ├── style.css           ← Styling
    └── script.js           ← Frontend logic
```

---

## ⚙️ Setup Instructions

### 1. Clone the repo
```
git clone https://github.com/yourusername/voiceforge.git
cd voiceforge
```

### 2. Install Python libraries
```
pip install -r requirements.txt
```

### 3. Install ffmpeg (required for audio conversion)
```
winget install ffmpeg
```

### 4. Run the app
```
python app.py
```

### 5. Open in browser
```
http://127.0.0.1:5000
```

---

## 🎯 How It Works

### Voice → Text
1. User records voice or uploads audio file
2. Browser sends audio to Flask backend
3. pydub converts audio to WAV format
4. SpeechRecognition sends to Google API
5. Text is returned and displayed

### Text → Voice
1. User types or edits text
2. Flask receives text
3. pyttsx3 converts text to speech
4. Audio file is sent back to browser
5. User can play or download it

---

## 📦 Requirements
```
flask
flask-cors
SpeechRecognition
pyttsx3
pyaudio
pydub
```

---

## 🏗️ Architecture Decisions

- **Flask** chosen for simplicity and quick setup
- **pyttsx3** used for offline text to speech — no API key needed
- **SpeechRecognition** with Google backend for best accuracy
- **pydub + ffmpeg** handles all audio format conversions
- **Vanilla JS** keeps frontend lightweight with no frameworks

---

## 👨‍💻 Built By

Built as part of AI Product Developer assessment at GenLab.