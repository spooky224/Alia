import { useState, useRef, useEffect } from "react";

export default function RepPanel({
  setSlides,
  setActiveSlide,
  setCategory,
  setProduct,
  disabled = false,
}) {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);

  const activeAudioRef = useRef(null);
  // ✅ Chat history (UNCHANGED)
  const [messages, setMessages] = useState([]);
  const chatEndRef = useRef(null);

  // 🎙 Mic state (NEW – isolated)
  const [recording, setRecording] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  // ✅ Auto-scroll
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // =====================================================
  // ✅ CORE SEND PIPELINE (UNCHANGED)
  // =====================================================
  const handleSend = async () => {
    if (disabled || !text.trim() || loading) return;
    setLoading(true);

    const userText = text.trim();

    // ✅ Add USER message
    setMessages((prev) => [
      ...prev,
      {
        id: crypto.randomUUID(),
        role: "user",
        text: userText,
      },
    ]);

    try {
      const res = await fetch("http://localhost:8000/process_message", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userText }),
      });

      const data = await res.json();

      if (data.mode === "presentation") {
        setCategory(data.category);
        setProduct(data.product);
      }

      const presentationSlides = data.timeline || [];

      const assistantMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        text: data.speech_text,
      };

      const audioRes = await fetch("http://localhost:8000/speak", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: data.speech_text }),
      });

      const blob = await audioRes.blob();
      const audio = new Audio(URL.createObjectURL(blob));
      activeAudioRef.current = audio;


      audio.onplaying = async () => {
        await fetch("http://localhost:8000/start_lipsync", {
          method: "POST",
        });

        setMessages((prev) => [...prev, assistantMessage]);
        setSlides(presentationSlides);
        setActiveSlide(0);
      };

      audio.ontimeupdate = () => {
        if (!presentationSlides.length) return;
        for (let i = presentationSlides.length - 1; i >= 0; i--) {
          if (audio.currentTime >= presentationSlides[i].start) {
            setActiveSlide(i);
            break;
          }
        }
      };

      audio.play();
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
      setText("");
    }
  };

  const handleObjection = async () => {
    console.log("🚨 Objection pressed");
  
    // 1️⃣ Stop audio immediately
    if (activeAudioRef.current) {
      activeAudioRef.current.pause();
      activeAudioRef.current.currentTime = 0;
      activeAudioRef.current = null;
    }
  
    // 2️⃣ Tell backend to stop lipsync + gestures
    try {
      await fetch("http://localhost:8000/interrupt", {
        method: "POST",
      });
    } catch (e) {
      console.error("Interrupt failed", e);
    }
  
    // 3️⃣ Play static interruption audio (frontend controlled)
    const objectionAudio = new Audio(
      "http://localhost:8000/objection/objection.wav"
    );
    objectionAudio.play();
  };

  // =====================================================
  // 🎙 MIC LOGIC (NEW, NON-INTRUSIVE)
  // =====================================================
  const startRecording = async () => {
    if (recording || loading) return;

    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const recorder = new MediaRecorder(stream);

    mediaRecorderRef.current = recorder;
    audioChunksRef.current = [];

    recorder.ondataavailable = (e) => {
      if (e.data.size > 0) audioChunksRef.current.push(e.data);
    };

    recorder.onstop = async () => {
      const audioBlob = new Blob(audioChunksRef.current, {
        type: "audio/webm",
      });

      const formData = new FormData();
      formData.append("audio", audioBlob);

      try {
        const res = await fetch("http://localhost:8000/transcribe", {
          method: "POST",
          body: formData,
        });

        const { text: spokenText } = await res.json();

        if (spokenText?.trim()) {
          setText(spokenText);
          handleSend(); // ✅ reuse same pipeline
        }
      } catch (err) {
        console.error("🎙 Transcription failed", err);
      }
    };

    recorder.start();
    setRecording(true);
  };

  const stopRecording = () => {
    if (!mediaRecorderRef.current) return;

    mediaRecorderRef.current.stop();
    mediaRecorderRef.current.stream
      .getTracks()
      .forEach((track) => track.stop());

    setRecording(false);
  };

  // =====================================================
  // ✅ UI (UNCHANGED WITH ONE SMALL ADDITION)
  // =====================================================
  return (
    <div
      style={{
        width: "min(480px, 92vw)",
        height: "70vh",
        padding: "16px 18px",
        display: "flex",
        flexDirection: "column",
        backdropFilter: "blur(14px)",
        background:
          "linear-gradient(180deg, rgba(28,36,24,0.82), rgba(18,24,16,0.88))",
        borderRadius: 14,
        border: "1px solid rgba(160, 200, 140, 0.25)",
        boxShadow:
          "0 20px 40px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.05)",
        color: "#EAF2E6",
        fontFamily: "Inter, system-ui, sans-serif",
        opacity: disabled ? 0.55 : 1,
        pointerEvents: disabled ? "none" : "auto",
      }}
    >
      {/* ✅ CHAT AREA */}
      <div
        style={{
          flex: 1,
          overflowY: "auto",
          display: "flex",
          flexDirection: "column",
          gap: 10,
          paddingRight: 6,
          marginBottom: 12,
        }}
      >
        {messages.map((m) => (
          <div
            key={m.id}
            style={{
              alignSelf: m.role === "user" ? "flex-end" : "flex-start",
              maxWidth: "85%",
              padding: "10px 14px",
              borderRadius: 14,
              background:
                m.role === "user"
                  ? "linear-gradient(180deg, #6f8f5f, #5a784b)"
                  : "linear-gradient(180deg, #1f2a1b, #161e14)",
              fontSize: 14,
              lineHeight: 1.45,
            }}
          >
            {m.text}
          </div>
        ))}
        <div ref={chatEndRef} />
      </div>

      {/* ✅ INPUT */}
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        disabled={disabled || loading || recording}
        placeholder={
          recording
            ? "Listening…"
            : disabled
            ? "Waiting for introduction…"
            : "Type or speak…"
        }
        style={{
          width: "94.5%",
          minHeight: 70,
          resize: "none",
          background: "rgba(0,0,0,0.35)",
          color: "#F3F7F1",
          border: "1px solid rgba(255,255,255,0.12)",
          borderRadius: 10,
          padding: "10px 12px",
          outline: "none",
          fontSize: 14,
        }}
      />

      {/* ✅ CONTROLS */}
      <div style={{ display: "flex", gap: 10, marginTop: 10 }}>
        <button
          onClick={recording ? stopRecording : startRecording}
          style={{
            flex: 1,
            height: 40,
            borderRadius: 10,
            border: "none",
            background: recording
              ? "linear-gradient(180deg, #b94a48, #8f3432)"
              : "linear-gradient(180deg, #4e6b5f, #384f45)",
            color: "#EAF2E6",
            fontWeight: 600,
          }}
        >
          {recording ? "Stop 🎙" : "Speak 🎙"}
        </button>


        <button
          onClick={handleObjection}
          style={{
            flex: 1,
            height: 40,
            borderRadius: 10,
            border: "1px solid rgba(255,80,80,0.5)",
            background: "linear-gradient(180deg, #5c1e1e, #3c1414)",
            color: "#FFECEC",
            fontWeight: 600,
          }}
        >
          Objection ⛔
        </button>

        <button
          onClick={handleSend}
          disabled={disabled || loading}
          style={{
            flex: 1,
            height: 40,
            borderRadius: 10,
            border: "none",
            background:
              disabled || loading
                ? "linear-gradient(180deg, #3a4a34, #2a3326)"
                : "linear-gradient(180deg, #7fa06c, #5f7f50)",
            fontWeight: 600,
          }}
        >
          {loading ? "Processing…" : "Send"}
        </button>
      </div>
    </div>
  );
}