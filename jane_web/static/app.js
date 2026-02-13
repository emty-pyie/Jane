const cmd = document.getElementById('cmd');
const send = document.getElementById('send');
const approve = document.getElementById('approve');
const deny = document.getElementById('deny');
const voice = document.getElementById('voice');
const statusEl = document.getElementById('status');
const logbox = document.getElementById('logbox');
const queue = document.getElementById('queue');

const synth = window.speechSynthesis;

function setStatus(msg) { statusEl.textContent = msg; }

function speak(text) {
  if (!synth || !text) return;
  const u = new SpeechSynthesisUtterance(text);
  u.rate = 1;
  synth.speak(u);
}

async function refresh() {
  const res = await fetch('/api/state');
  const data = await res.json();
  logbox.textContent = data.logs.join('\n');
  queue.innerHTML = '';
  data.pending.forEach((p) => {
    const li = document.createElement('li');
    li.textContent = `${p.action} :: ${p.raw}`;
    queue.appendChild(li);
  });
}

async function post(url, body = null) {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : null
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || 'Request failed');
  return data;
}

send.onclick = async () => {
  const text = cmd.value.trim();
  if (!text) return;
  try {
    const result = await post('/api/command', { text });
    setStatus(result.message);
    speak(result.message);
    cmd.value = '';
    await refresh();
  } catch (e) {
    setStatus(`Error: ${e.message}`);
  }
};

approve.onclick = async () => {
  try {
    const result = await post('/api/approve');
    setStatus(result.message);
    speak(result.message);
    await refresh();
  } catch (e) {
    setStatus(`Approve failed: ${e.message}`);
  }
};

deny.onclick = async () => {
  try {
    const result = await post('/api/deny');
    setStatus(result.message);
    speak(result.message);
    await refresh();
  } catch (e) {
    setStatus(`Deny failed: ${e.message}`);
  }
};

voice.onclick = () => {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) {
    setStatus('Voice recognition unsupported in this browser.');
    return;
  }
  const rec = new SR();
  rec.lang = 'en-US';
  rec.onresult = async (ev) => {
    const text = ev.results[0][0].transcript;
    cmd.value = text;
    setStatus(`Heard: ${text}`);
  };
  rec.onerror = (ev) => setStatus(`Voice error: ${ev.error}`);
  rec.start();
};

setInterval(refresh, 2500);
refresh();
