let audioContext = null;
let mediaStream = null;
let scriptProcessor = null;
let audioWebSocket = null;
let speechRecognizer = null;
let isCallActive = false;
let currentCumulativeRisk = 0.0;
let currentTurn = 0;

// Language priority: try kn-IN first, fall back to en-IN if not supported
// (Windows often lacks Kannada voice pack; en-IN still catches Kanglish keywords)
const LANG_PRIORITY = ["kn-IN", "en-IN"];
let activeLang = LANG_PRIORITY[0];

const SpeechRecClass = window.SpeechRecognition || window.webkitSpeechRecognition;

function setupSpeechRecognition(lang) {
    if (!SpeechRecClass) {
        sttInterimDisplay.innerHTML = `<span style="color:#f87171;">
            ⚠️ Speech recognition NOT supported. Please use Chrome or Edge.
        </span>`;
        return null;
    }

    const recognizer = new SpeechRecClass();
    recognizer.continuous = true;
    recognizer.interimResults = true;
    recognizer.maxAlternatives = 1;
    recognizer.lang = lang;

    sttInterimDisplay.innerHTML = `<span style="color:#60a5fa; font-size:0.78rem;">
        🔄 Starting recognition (${lang})...
    </span>`;

    recognizer.onstart = () => {
        activeLang = lang;
        audioStatusText.innerText = `Listening (${lang})`;
        sttInterimDisplay.innerHTML = `<span style="color:#94a3b8; font-size:0.8rem;">
            🎤 Mic active — speak in Kannada or Kanglish now...
        </span>`;
        document.getElementById("sttLangBadge").innerText = lang;
    };

    recognizer.onresult = (event) => {
        let interimText = "";
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                const finalTurn = transcript.trim();
                if (finalTurn) {
                    sttInterimDisplay.innerHTML = `<span style="color:#34d399; font-weight:600;">
                        ✔ [Analyzing] ${finalTurn}
                    </span>`;
                    sendTurnForAnalysis(finalTurn);
                }
            } else {
                interimText += transcript;
            }
        }
        if (interimText) {
            sttInterimDisplay.innerHTML = `<span style="color:#cbd5e1; font-style:italic;">
                🎤 ${interimText}
            </span>`;
            audioStatusText.innerText = "Hearing speech...";
        }
    };

    recognizer.onend = () => {
        // Auto-restart if still active (browser stops after silence)
        if (isCallActive) {
            setTimeout(() => {
                if (isCallActive) {
                    try { recognizer.start(); }
                    catch(e) { console.warn("Recognizer restart skipped:", e.message); }
                }
            }, 200);
        }
    };

    recognizer.onerror = (e) => {
        console.warn(`Speech recognition error (${lang}):`, e.error);

        if (e.error === "language-not-supported" || e.error === "not-allowed") {
            if (lang === "kn-IN" && isCallActive) {
                // kn-IN not installed on this system — fall back to en-IN
                sttInterimDisplay.innerHTML = `<span style="color:#fbbf24; font-size:0.78rem;">
                    ⚠️ kn-IN not available on this device. Switching to en-IN (Kanglish keywords still detected)...
                </span>`;
                speechRecognizer = setupSpeechRecognition("en-IN");
                if (speechRecognizer) {
                    try { speechRecognizer.start(); } catch(e2) {}
                }
            } else if (e.error === "not-allowed") {
                sttInterimDisplay.innerHTML = `<span style="color:#f87171;">
                    ❌ Microphone permission denied. Allow mic access and retry.
                </span>`;
            }
            return;
        }

        if (e.error === "network") {
            sttInterimDisplay.innerHTML = `<span style="color:#fbbf24; font-size:0.78rem;">
                ⚠️ Network error on speech API. Retrying...
            </span>`;
        }
        // For no-speech / audio-capture / aborted — just let onend restart handle it
    };

    return recognizer;
}

// DOM Elements
const riskScoreVal = document.getElementById("riskScoreVal");
const riskProgressBar = document.getElementById("riskProgressBar");
const alertBox = document.getElementById("alertBox");
const alertIcon = document.getElementById("alertIcon");
const alertTitle = document.getElementById("alertTitle");
const alertAdvice = document.getElementById("alertAdvice");
const callStateTag = document.getElementById("callStateTag");
const currentTurnCount = document.getElementById("currentTurnCount");
const transcriptFeed = document.getElementById("transcriptFeed");
const pillsContainer = document.getElementById("pillsContainer");
const btnStartMic = document.getElementById("btnStartMic");
const btnStopCall = document.getElementById("btnStopCall");
const audioStatusText = document.getElementById("audioStatusText");
const sttInterimDisplay = document.getElementById("sttInterimDisplay");
const buzzerSound = document.getElementById("buzzerSound");
const waveformCanvas = document.getElementById("waveformCanvas");
const canvasCtx = waveformCanvas.getContext("2d");

// Dynamic Backend Config (supports localhost and GitHub Pages deployment)
function getBackendConfig() {
    const isGhPages = window.location.hostname.endsWith("github.io");
    if (isGhPages) {
        const stored = localStorage.getItem("rakshak_backend_url") || "http://localhost:8080";
        try {
            const parsed = new URL(stored);
            const wsProto = parsed.protocol === "https:" ? "wss:" : "ws:";
            return {
                http: stored.replace(/\/$/, ""),
                ws: `${wsProto}//${parsed.host}`
            };
        } catch(e) {
            return { http: stored, ws: "ws://localhost:8080" };
        }
    }
    const protocol = window.location.protocol === "https:" ? "https:" : "http:";
    const wsProto = window.location.protocol === "https:" ? "wss:" : "ws:";
    return {
        http: `${protocol}//${window.location.host}`,
        ws: `${wsProto}//${window.location.host}`
    };
}

// Check Engine Status on startup
async function checkEngineStatus() {
    try {
        const res = await fetch(`${getBackendConfig().http}/api/status`);
        const data = await res.json();
        const badge = document.getElementById("engineStatusBadge");
        if (data.trained_models_loaded) {
            badge.innerText = "✅ Colab Models Loaded";
            badge.style.color = "#34d399";
        } else {
            badge.innerText = "🔵 Smart Stacking Ready";
            badge.style.color = "#38bdf8";
        }
    } catch (e) {
        console.warn("Status check failed:", e);
        if (window.location.hostname.endsWith("github.io")) {
            const badge = document.getElementById("engineStatusBadge");
            if (badge) {
                badge.innerText = "⚙️ Configure Backend URL";
                badge.style.cursor = "pointer";
                badge.onclick = () => {
                    const current = localStorage.getItem("rakshak_backend_url") || "http://localhost:8080";
                    const entered = prompt("Enter your RakshakAI backend URL (e.g. Render / local URL):", current);
                    if (entered) {
                        localStorage.setItem("rakshak_backend_url", entered.trim());
                        window.location.reload();
                    }
                };
            }
        }
    }
}
checkEngineStatus();

// Initialize Audio Waveform Visualizer
function drawIdleWaveform() {
    canvasCtx.fillStyle = "#080c14";
    canvasCtx.fillRect(0, 0, waveformCanvas.width, waveformCanvas.height);
    canvasCtx.strokeStyle = "#1e293b";
    canvasCtx.lineWidth = 1.5;
    canvasCtx.beginPath();
    canvasCtx.moveTo(0, waveformCanvas.height / 2);
    canvasCtx.lineTo(waveformCanvas.width, waveformCanvas.height / 2);
    canvasCtx.stroke();
}
drawIdleWaveform();

// ─── START MIC ────────────────────────────────────────────────────────────────
btnStartMic.addEventListener("click", async () => {
    try {
        audioStatusText.innerText = "Requesting mic...";
        mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });

        audioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
        const source = audioContext.createMediaStreamSource(mediaStream);
        const analyser = audioContext.createAnalyser();
        analyser.fftSize = 256;
        source.connect(analyser);

        // Open Backend WebSocket (receives analysis results)
        const wsUrl = `${getBackendConfig().ws}/ws/stream-audio`;
        audioWebSocket = new WebSocket(wsUrl);
        audioWebSocket.binaryType = "arraybuffer";

        audioWebSocket.onopen = () => {
            isCallActive = true;
            resetUIState("LIVE CALL ACTIVE");
            callStateTag.className = "tag tag-live";
            btnStartMic.disabled = true;
            btnStopCall.disabled = false;

            // Start speech recognition — try kn-IN first
            speechRecognizer = setupSpeechRecognition(LANG_PRIORITY[0]);
            if (speechRecognizer) {
                try { speechRecognizer.start(); }
                catch(e) { console.warn("STT start error:", e); }
            }
        };

        audioWebSocket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data && data.type === "turn_update") {
                    currentTurn = data.turn || (currentTurn + 1);
                    renderTurnResult(data);
                }
            } catch(e) {
                console.error("WS message parse error:", e);
            }
        };

        audioWebSocket.onclose = () => {
            if (isCallActive) {
                audioStatusText.innerText = "Connection lost. Click End Call.";
            }
        };

        // Stream PCM audio to backend
        scriptProcessor = audioContext.createScriptProcessor(4096, 1, 1);
        source.connect(scriptProcessor);
        scriptProcessor.connect(audioContext.destination);
        scriptProcessor.onaudioprocess = (e) => {
            if (!isCallActive || !audioWebSocket || audioWebSocket.readyState !== WebSocket.OPEN) return;
            audioWebSocket.send(floatTo16BitPCM(e.inputBuffer.getChannelData(0)).buffer);
        };

        // Live waveform visualizer
        const dataArray = new Uint8Array(analyser.frequencyBinCount);
        function animateWaveform() {
            if (!isCallActive) { drawIdleWaveform(); return; }
            requestAnimationFrame(animateWaveform);
            analyser.getByteFrequencyData(dataArray);
            canvasCtx.fillStyle = "#080c14";
            canvasCtx.fillRect(0, 0, waveformCanvas.width, waveformCanvas.height);
            const barWidth = (waveformCanvas.width / dataArray.length) * 2.2;
            let x = 0;
            for (let i = 0; i < dataArray.length; i++) {
                const h = (dataArray[i] / 255) * waveformCanvas.height;
                canvasCtx.fillStyle = currentCumulativeRisk >= 0.70 ? "#ef4444" :
                                      currentCumulativeRisk >= 0.35 ? "#fbbf24" : "#38bdf8";
                canvasCtx.fillRect(x, waveformCanvas.height - h, barWidth, h);
                x += barWidth + 1;
            }
        }
        animateWaveform();

    } catch (err) {
        if (err.name === "NotAllowedError") {
            sttInterimDisplay.innerHTML = `<span style="color:#f87171;">
                ❌ Microphone permission denied. Allow mic access in browser and retry.
            </span>`;
        } else {
            alert("Microphone Error: " + err.message);
        }
        audioStatusText.innerText = "Mic Error";
    }
});

function floatTo16BitPCM(output) {
    const buffer = new Int16Array(output.length);
    for (let i = 0; i < output.length; i++) {
        const s = Math.max(-1, Math.min(1, output[i]));
        buffer[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
    }
    return buffer;
}

// ─── STOP CALL ────────────────────────────────────────────────────────────────
btnStopCall.addEventListener("click", stopCall);
function stopCall() {
    isCallActive = false;
    if (speechRecognizer) {
        try { speechRecognizer.abort(); } catch(e) {}
        speechRecognizer = null;
    }
    if (mediaStream) { mediaStream.getTracks().forEach(t => t.stop()); mediaStream = null; }
    if (audioContext) { audioContext.close(); audioContext = null; }
    if (audioWebSocket) { audioWebSocket.close(); audioWebSocket = null; }
    callStateTag.innerText = "CALL ENDED";
    callStateTag.className = "tag tag-idle";
    audioStatusText.innerText = "Mic Inactive";
    sttInterimDisplay.innerHTML = `<span class="text-muted" style="font-size:0.8rem;">Waiting for speech...</span>`;
    btnStartMic.disabled = false;
    btnStopCall.disabled = true;
    drawIdleWaveform();
}

// ─── SEND TURN FOR ANALYSIS (REST fallback — works even if WS drops) ─────────
async function sendTurnForAnalysis(text) {
    // Try WebSocket first (lower latency)
    if (audioWebSocket && audioWebSocket.readyState === WebSocket.OPEN) {
        audioWebSocket.send(JSON.stringify({ type: "transcript_turn", text }));
        return;
    }
    // Fall back to REST API directly
    try {
        currentTurn += 1;
        const res = await fetch(`${getBackendConfig().http}/api/analyze-turn`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                text,
                turn_index: currentTurn,
                prev_cumulative_risk: currentCumulativeRisk
            })
        });
        const data = await res.json();
        data.turn = currentTurn;
        data.turn_risk = data.turn_risk || 0;
        renderTurnResult(data);
    } catch (e) {
        console.error("Analysis REST error:", e);
        sttInterimDisplay.innerHTML = `<span style="color:#f87171;">⚠️ Backend error: ${e.message}</span>`;
    }
}

// ─── RENDER TURN RESULT ───────────────────────────────────────────────────────
function renderTurnResult(turn) {
    currentTurn = turn.turn;
    currentCumulativeRisk = turn.cumulative_risk;
    currentTurnCount.innerText = currentTurn;

    document.querySelectorAll(".step").forEach(s => s.classList.remove("step-active"));
    if (currentTurn <= 2) document.getElementById("step1").classList.add("step-active");
    else if (currentTurn <= 4) document.getElementById("step2").classList.add("step-active");
    else document.getElementById("step3").classList.add("step-active");

    const percent = Math.round(currentCumulativeRisk * 100);
    riskScoreVal.innerText = `${percent}%`;
    riskProgressBar.style.width = `${percent}%`;

    riskProgressBar.className = "progress-bar-fill";
    riskScoreVal.className = "gauge-val";
    alertBox.className = "alert-box";

    if (currentCumulativeRisk < 0.35) {
        riskProgressBar.classList.add("fill-emerald");
        riskScoreVal.classList.add("text-emerald");
        alertBox.classList.add("alert-safe");
        alertIcon.innerText = "🟢";
        alertTitle.innerText = "Call Status: Safe";
    } else if (currentCumulativeRisk < 0.70) {
        riskProgressBar.classList.add("fill-amber");
        riskScoreVal.classList.add("text-amber");
        alertBox.classList.add("alert-warning");
        alertIcon.innerText = "🟡";
        alertTitle.innerText = "ADVISORY: Suspicious Call Detected!";
    } else {
        riskProgressBar.classList.add("fill-rose");
        riskScoreVal.classList.add("text-rose");
        alertBox.classList.add("alert-critical");
        alertIcon.innerText = "🔴";
        alertTitle.innerText = "CRITICAL FRAUD: Active Scam in Progress!";
        try { buzzerSound.play(); } catch(e) {}
    }

    alertAdvice.innerText = turn.advice;

    if (turn.pills && turn.pills.length > 0) {
        pillsContainer.innerHTML = turn.pills.map(p => {
            const cls = p.severity === "critical" ? "pill-critical" : "pill-high";
            return `<span class="pill ${cls}">⚑ ${p.category} (${p.keywords.join(", ")})</span>`;
        }).join("");
    }

    if (document.querySelector(".empty-state")) transcriptFeed.innerHTML = "";

    const itemCls = currentCumulativeRisk >= 0.70 ? "turn-item turn-item-critical" :
                   currentCumulativeRisk >= 0.35 ? "turn-item turn-item-warning" : "turn-item";

    const turnEl = document.createElement("div");
    turnEl.className = itemCls;
    const spokenText = turn.text_kannada || turn.text || "";
    turnEl.innerHTML = `
        <div class="turn-header">
            <span>Turn #${turn.turn}</span>
            <span>Turn Risk: <strong>${Math.round((turn.turn_risk || 0) * 100)}%</strong> | Cumulative: <strong>${percent}%</strong></span>
        </div>
        <div class="turn-kannada">${spokenText}</div>
        ${turn.text_english ? `<div class="turn-english">🌐 "${turn.text_english}"</div>` : ""}
    `;
    transcriptFeed.appendChild(turnEl);
    transcriptFeed.scrollTop = transcriptFeed.scrollHeight;
}

// ─── RESET STATE ──────────────────────────────────────────────────────────────
function resetUIState(stateTitle) {
    currentCumulativeRisk = 0.0;
    currentTurn = 0;
    callStateTag.innerText = stateTitle;
    transcriptFeed.innerHTML = "";
    pillsContainer.innerHTML = `<span class="text-xs text-muted">No red flags detected yet.</span>`;
    riskScoreVal.innerText = "0%";
    riskProgressBar.style.width = "0%";
    riskProgressBar.className = "progress-bar-fill fill-emerald";
    alertBox.className = "alert-box alert-safe";
    alertIcon.innerText = "🟢";
    alertTitle.innerText = "Call Status: Active Monitoring";
    alertAdvice.innerText = "Analyzing live speech turns against Indian fraud patterns...";
    currentTurnCount.innerText = "0";
    document.querySelectorAll(".step").forEach(s => s.classList.remove("step-active"));
    document.getElementById("step1").classList.add("step-active");
}
