let mediaRecorder;
let audioChunks = [];

// 🎤 START RECORDING
async function startRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];

    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunks.push(event.data);
      }
    };

    mediaRecorder.onstop = async () => {
      const blob = new Blob(audioChunks, { type: 'audio/webm' });
      await sendAudioToServer(blob);
    };

    mediaRecorder.start();

    document.getElementById('startBtn').disabled = true;
    document.getElementById('stopBtn').disabled = false;
    document.getElementById('rec-status').textContent = '🔴 Recording...';

  } catch (err) {
    console.error(err);
    document.getElementById('rec-status').textContent =
      '❌ Mic error: ' + err.message;
  }
}

// ⏹️ STOP RECORDING
function stopRecording() {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop();
    mediaRecorder.stream.getTracks().forEach(track => track.stop());
  }

  document.getElementById('startBtn').disabled = false;
  document.getElementById('stopBtn').disabled = true;
  document.getElementById('rec-status').textContent = '⏳ Processing...';
}

// 📤 SEND AUDIO TO SERVER
async function sendAudioToServer(blob) {
  const formData = new FormData();
  formData.append('audio', blob, 'recording.webm');

  try {
    const res = await fetch('/voice-to-text', {
      method: 'POST',
      body: formData
    });

    const data = await res.json();

    if (data.text) {
      document.getElementById('transcript').value = data.text;
      document.getElementById('tts-input').value = data.text;
      document.getElementById('rec-status').textContent = '✅ Done!';
    } else {
      document.getElementById('rec-status').textContent = '❌ ' + data.error;
    }

  } catch (err) {
    console.error(err);
    document.getElementById('rec-status').textContent =
      '❌ Server error: ' + err.message;
  }
}

// 📁 UPLOAD AUDIO FILE
async function uploadAudioFile(event) {
  const file = event.target.files[0];
  if (!file) return;

  document.getElementById('upload-status').textContent = '⏳ Uploading...';

  const formData = new FormData();
  formData.append('audio', file);

  try {
    const res = await fetch('/voice-to-text', {
      method: 'POST',
      body: formData
    });

    const data = await res.json();

    if (data.text) {
      document.getElementById('transcript').value = data.text;
      document.getElementById('tts-input').value = data.text;
      document.getElementById('upload-status').textContent = '✅ Done!';
    } else {
      document.getElementById('upload-status').textContent = '❌ ' + data.error;
    }

  } catch (err) {
    document.getElementById('upload-status').textContent = '❌ Upload failed!';
  }
}

// 🔊 TEXT TO VOICE
async function speakText() {
  const text = document.getElementById('tts-input').value.trim();

  if (!text) {
    alert('Please type something first!');
    return;
  }

  try {
    const res = await fetch('/text-to-voice', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });

    const blob = await res.blob();
    const url = URL.createObjectURL(blob);

    const player = document.getElementById('audio-player');
    player.src = url;
    player.style.display = 'block';
    player.play();

  } catch (err) {
    alert('❌ Error generating speech!');
  }
}