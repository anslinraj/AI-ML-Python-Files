let mediaRecorder;
let audioChunks = [];
let audioBlob = null;

// ── VOICE TO TEXT ──────────────────────────────

async function startRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    // Check supported formats
    let mimeType = 'audio/webm';
    if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
      mimeType = 'audio/webm;codecs=opus';
    } else if (MediaRecorder.isTypeSupported('audio/ogg;codecs=opus')) {
      mimeType = 'audio/ogg;codecs=opus';
    }

    mediaRecorder = new MediaRecorder(stream, { mimeType });
    audioChunks = [];

    mediaRecorder.ondataavailable = e => {
      if (e.data.size > 0) audioChunks.push(e.data);
    };

    mediaRecorder.onstop = async () => {
      audioBlob = new Blob(audioChunks, { type: mimeType });
      console.log('Audio blob size:', audioBlob.size, 'type:', mimeType);
      await sendAudioToServer(audioBlob, mimeType);
    };

    // Collect data every 250ms for better quality
    mediaRecorder.start(250);

    document.getElementById('startBtn').disabled = true;
    document.getElementById('stopBtn').disabled = false;
    document.getElementById('rec-status').textContent = '🔴 Recording... speak now!';

  } catch (err) {
    document.getElementById('rec-status').textContent = '❌ Mic error: ' + err.message;
  }
}

function stopRecording() {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop();
    mediaRecorder.stream.getTracks().forEach(track => track.stop());
  }
  document.getElementById('startBtn').disabled = false;
  document.getElementById('stopBtn').disabled = true;
  document.getElementById('rec-status').textContent = '⏳ Processing... please wait';
}

async function sendAudioToServer(blob, mimeType) {
  // Pick correct file extension
  let ext = 'webm';
  if (mimeType.includes('ogg')) ext = 'ogg';
  else if (mimeType.includes('mp4')) ext = 'mp4';

  const formData = new FormData();
  formData.append('audio', blob, 'recording.' + ext);

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
    document.getElementById('rec-status').textContent = '❌ Server error: ' + err.message;
  }
}

// ── UPLOAD AUDIO FILE ──────────────────────────

async function uploadAudioFile(event) {
  const file = event.target.files[0];
  if (!file) return;

  document.getElementById('upload-status').textContent = '⏳ Uploading... please wait';

  const formData = new FormData();
  formData.append('audio', file, file.name);

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
    document.getElementById('upload-status').textContent = '❌ Server error!';
  }
}

// ── TEXT TO VOICE ──────────────────────────────

async function speakText() {
  const text = document.getElementById('tts-input').value.trim();
  if (!text) { alert('Please type something first!'); return; }

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

    document.getElementById('downloadBtn').disabled = false;
    document.getElementById('downloadBtn').dataset.url = url;

  } catch (err) {
    alert('Error generating speech!');
  }
}

function downloadAudio() {
  const url = document.getElementById('downloadBtn').dataset.url;
  const a = document.createElement('a');
  a.href = url;
  a.download = 'voiceforge_output.mp3';
  a.click();
}