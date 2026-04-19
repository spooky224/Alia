import { useState } from "react";

export default function RepPanel({
  setSlides,
  setActiveSlide,
  disabled = false,
}) {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (disabled || !text.trim() || loading) return;
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/process_message", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      });

      const data = await res.json();
      const presentationSlides = data.timeline || [];

      const audioRes = await fetch("http://localhost:8000/speak", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: data.speech_text,
        }),
      });

      const blob = await audioRes.blob();
      const audio = new Audio(URL.createObjectURL(blob));

      // ✅ Presentation starts
      audio.onplaying = async () => {
        console.log("[Presentation] started");
        await fetch("http://localhost:8000/start_lipsync", {
          method: "POST",
        });
        setSlides(presentationSlides);
        setActiveSlide(0);
      };

      // ✅ Slide timing driven by audio
      audio.ontimeupdate = () => {
        if (!presentationSlides.length) return;

        for (let i = presentationSlides.length - 1; i >= 0; i--) {
          if (audio.currentTime >= presentationSlides[i].start) {
            setActiveSlide(i);
            break;
          }
        }
      };

      // ✅ Presentation ended → CLEAR SLIDES
      audio.onended = () => {
        console.log("[Presentation] ended → clearing slides");

        setSlides([]);       // ✅ removes all slides
        setActiveSlide(0);   // ✅ reset index
      };

      audio.play();
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
      setText("");
    }
  };

  return (
    <div
      style={{
        width: 320,
        padding: "16px 18px",
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
        transition: "opacity 200ms ease-out",
      }}
    >
      <div
        style={{
          fontSize: 12,
          textTransform: "uppercase",
          letterSpacing: "0.12em",
          opacity: 0.7,
          marginBottom: 10,
        }}
      >
        Presenter Input
      </div>

      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        disabled={disabled || loading}
        placeholder={
          disabled
            ? "Waiting for introduction…"
            : "Type the message to present…"
        }
        style={{
          width: "100%",
          minHeight: 80,
          resize: "none",
          background: "rgba(0,0,0,0.35)",
          color: "#F3F7F1",
          border: "1px solid rgba(255,255,255,0.12)",
          borderRadius: 10,
          padding: "10px 12px",
          outline: "none",
          fontSize: 14,
          lineHeight: 1.4,
          boxShadow: "inset 0 2px 6px rgba(0,0,0,0.35)",
        }}
      />

      <button
        onClick={handleSend}
        disabled={disabled || loading}
        style={{
          marginTop: 12,
          width: "100%",
          height: 40,
          borderRadius: 10,
          border: "none",
          cursor: disabled || loading ? "default" : "pointer",
          background:
            disabled || loading
              ? "linear-gradient(180deg, #3a4a34, #2a3326)"
              : "linear-gradient(180deg, #7fa06c, #5f7f50)",
          color: "#102010",
          fontWeight: 600,
          letterSpacing: "0.04em",
          boxShadow:
            "0 6px 16px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.35)",
        }}
      >
        {disabled
          ? "Intro playing…"
          : loading
          ? "Processing…"
          : "Send"}
      </button>
    </div>
  );
}