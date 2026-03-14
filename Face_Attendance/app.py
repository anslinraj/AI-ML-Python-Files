from flask import Flask, render_template, Response, request, redirect, url_for, session
import os
from flask import send_file
import cv2
import face_recognition
import numpy as np
import os
import pandas as pd
from datetime import datetime


import warnings
warnings.filterwarnings("ignore", category=UserWarning)

import webbrowser

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")


app = Flask(__name__)
app.secret_key = "supersecretkey123"

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "1234"


app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.auto_reload = True


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ATTENDANCE_FILE = os.path.join(BASE_DIR, "Attendance.csv")
KNOWN_FACES_DIR = os.path.join(BASE_DIR, "known_faces")


# Load known faces
known_face_encodings = []
known_face_names = []

for file in os.listdir(KNOWN_FACES_DIR):
    if file.lower().endswith((".jpg", ".jpeg", ".png")):
        path = os.path.join(KNOWN_FACES_DIR, file)
        image = face_recognition.load_image_file(path)
        encodings = face_recognition.face_encodings(image)

        if encodings:
            known_face_encodings.append(encodings[0])
            known_face_names.append(os.path.splitext(file)[0])

# Create attendance file if missing
if not os.path.exists(ATTENDANCE_FILE):
    pd.DataFrame(columns=["Name", "Date", "Time"]).to_csv(ATTENDANCE_FILE, index=False)

camera = cv2.VideoCapture(0)

def mark_attendance(name):
    today = datetime.now().strftime("%Y-%m-%d")
    df = pd.read_csv(ATTENDANCE_FILE)

    already_marked = (
        (df["Name"] == name) & (df["Date"] == today)
    ).any()

    if not already_marked:
        df.loc[len(df)] = [
            name,
            today,
            datetime.now().strftime("%H:%M:%S")
        ]
        df.to_csv(ATTENDANCE_FILE, index=False)
        print("Attendance Marked:", name)


def gen_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for face_encoding, face_location in zip(face_encodings, face_locations):
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            face_distances = face_recognition.face_distance(
                known_face_encodings, face_encoding
            )

            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]

            if name != "Unknown":
                mark_attendance(name)

            top, right, bottom, left = face_location
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left, top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video')
def video():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')



@app.route('/attendance')
def attendance():
    if not session.get('admin'):
        return redirect(url_for('login'))

    df = pd.read_csv(ATTENDANCE_FILE)

    return render_template('attendance.html',
                           table=df.to_html(index=False, classes="attendance-table"),
                           total=len(df))


 

@app.route('/reset')
def reset_attendance():
    pd.DataFrame(columns=["Name", "Date", "Time"]).to_csv(
        ATTENDANCE_FILE, index=False
    )
    return "Attendance cleared successfully!"

@app.route('/download')
def download_file():
    file_path = "Attendance.csv"

    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "No attendance file found!"
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('attendance'))
        else:
            return render_template('login.html', error="Invalid Credentials")

    return render_template('login.html')

    

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('login'))


if __name__ == "__main__":
    open_browser()
    app.run(debug=False, use_reloader=False)




