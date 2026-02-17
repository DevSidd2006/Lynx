const recordBtn = document.getElementById("recordBtn");
const stopBtn = document.getElementById("stopBtn");
const rewriteBtn = document.getElementById("rewriteBtn");
const copyBtn = document.getElementById("copyBtn");
const saveProfileBtn = document.getElementById("saveProfileBtn");

const transcriptEl = document.getElementById("transcript");
const outputEl = document.getElementById("output");
const styleEl = document.getElementById("style");
const contextEl = document.getElementById("context");
const languageEl = document.getElementById("language");
const statusEl = document.getElementById("status");
const historyEl = document.getElementById("history");

const fullNameEl = document.getElementById("fullName");
const roleEl = document.getElementById("role");
const toneEl = document.getElementById("tone");
const dictionaryEl = document.getElementById("dictionary");
const rulesEl = document.getElementById("rules");

let mediaRecorder;
let chunks = [];

/**
 * Tab Navigation Logic
 */
document.querySelectorAll(".nav-link").forEach((link) => {
  link.addEventListener("click", (e) => {
    e.preventDefault();
    const targetPage = link.getAttribute("data-page");

    // Update nav links
    document.querySelectorAll(".nav-link").forEach((l) => l.classList.remove("active"));
    link.classList.add("active");

    // Update pages
    document.querySelectorAll(".page").forEach((p) => p.classList.remove("active"));
    document.getElementById(targetPage).classList.add("active");
  });
});

function setStatus(message, type = "idle") {
  const dot = statusEl.querySelector(".status-dot");
  if (type === "loading") {
    dot.style.backgroundColor = "var(--primary)";
  } else if (type === "error") {
    dot.style.backgroundColor = "var(--danger)";
  } else if (type === "success") {
    dot.style.backgroundColor = "var(--success)";
  } else {
    dot.style.backgroundColor = "var(--success)";
  }
  
  statusEl.childNodes[statusEl.childNodes.length - 1].textContent = " " + message;
}

function linesToArray(value) {
  return value
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);
}

async function loadProfile() {
  const res = await fetch("/api/profile");
  const data = await res.json();
  fullNameEl.value = data.full_name || "";
  roleEl.value = data.role || "";
  toneEl.value = data.preferred_tone || "professional";
  dictionaryEl.value = (data.custom_dictionary || []).join("\n");
  rulesEl.value = (data.writing_rules || []).join("\n");
}

async function saveProfile() {
  setStatus("Saving profile...", "loading");
  const payload = {
    full_name: fullNameEl.value.trim(),
    role: roleEl.value.trim(),
    preferred_tone: toneEl.value.trim() || "professional",
    custom_dictionary: linesToArray(dictionaryEl.value),
    writing_rules: linesToArray(rulesEl.value),
  };
  const res = await fetch("/api/profile", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    setStatus("Profile save failed", "error");
    return;
  }

  setStatus("Profile saved", "success");
}

async function refreshHistory() {
  const res = await fetch("/api/history?limit=25");
  const data = await res.json();
  historyEl.innerHTML = "";

  if (data.length === 0) {
    historyEl.innerHTML = '<p style="color: var(--text-secondary); text-align: center; padding: 20px;">No history items found yet.</p>';
    return;
  }

  for (const item of data) {
    const card = document.createElement("div");
    card.className = "history-card";
    
    const dateStr = new Date(item.created_at).toLocaleString();
    
    card.innerHTML = `
      <div class="history-meta">
        <span>${item.style} • ${item.context}</span>
        <span>${dateStr}</span>
      </div>
      <div class="history-text">${item.rewritten_text || "No content"}</div>
    `;
    
    card.addEventListener("click", () => {
      transcriptEl.value = item.source_text || "";
      outputEl.value = item.rewritten_text || "";
      
      // Switch to dashboard
      document.querySelector('[data-page="dashboard"]').click();
    });
    
    historyEl.appendChild(card);
  }
}

async function rewriteTypedText() {
  const text = transcriptEl.value.trim();
  if (!text) {
    setStatus("Nothing to rewrite", "error");
    return;
  }

  setStatus("Rewriting text...", "loading");
  const res = await fetch("/api/rewrite", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      text,
      style: styleEl.value,
      context: contextEl.value,
      language: languageEl.value || "en",
    }),
  });

  const data = await res.json();
  if (!res.ok) {
    setStatus(data.detail || "Rewrite failed", "error");
    return;
  }

  outputEl.value = data.rewritten_text;
  setStatus("Rewrite complete", "success");
  refreshHistory();
}

async function sendRecording(blob) {
  setStatus("Transcribing audio...", "loading");
  const form = new FormData();
  form.append("audio", blob, "dictation.webm");
  form.append("style", styleEl.value);
  form.append("context", contextEl.value);
  form.append("language", languageEl.value || "en");
  form.append("auto_rewrite", "true");

  const res = await fetch("/api/transcribe", {
    method: "POST",
    body: form,
  });

  const data = await res.json();
  if (!res.ok) {
    setStatus(data.detail || "Transcription failed", "error");
    return;
  }

  transcriptEl.value = data.transcript;
  outputEl.value = data.rewritten_text;
  setStatus("Dictation complete", "success");
  refreshHistory();
}

recordBtn.addEventListener("click", async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/webm" });
    chunks = [];

    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        chunks.push(event.data);
      }
    };

    mediaRecorder.onstop = async () => {
      const blob = new Blob(chunks, { type: "audio/webm" });
      await sendRecording(blob);
    };

    mediaRecorder.start();
    recordBtn.disabled = true;
    stopBtn.disabled = false;
    setStatus("Recording...", "loading");
  } catch {
    setStatus("Microphone access denied", "error");
  }
});

stopBtn.addEventListener("click", () => {
  if (!mediaRecorder) {
    return;
  }
  mediaRecorder.stop();
  mediaRecorder.stream.getTracks().forEach((track) => track.stop());
  recordBtn.disabled = false;
  stopBtn.disabled = true;
});

copyBtn.addEventListener("click", async () => {
  const content = outputEl.value.trim() || transcriptEl.value.trim();
  if (!content) {
    setStatus("Nothing to copy", "error");
    return;
  }
  await navigator.clipboard.writeText(content);
  setStatus("Copied to clipboard", "success");
});

saveProfileBtn.addEventListener("click", saveProfile);
rewriteBtn.addEventListener("click", rewriteTypedText);

(async function init() {
  await Promise.all([loadProfile(), refreshHistory()]);
  setStatus("System Ready", "success");
})();
