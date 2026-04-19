export default function DoctorPanel({ sendText }) {
    return (
      <div style={{ padding: 20, background: "#111", color: "white" }}>
        <h2>Doctor Mode</h2>
  
        <textarea
          id="docInput"
          placeholder="Ask medical questions..."
          style={{ width: "80%", height: 60 }}
        />
  
        <button
          onClick={async () => {
            const msg = document.getElementById("docInput").value;
            if (!msg.trim()) return;
  
            // ✅ FRONTEND → FASTAPI → AUDIO MP3
            const response = await fetch("http://localhost:5000/send_text", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ message: msg }),
            });
  
            const audioBlob = await response.blob();
            const audioUrl = URL.createObjectURL(audioBlob);
  
            // ✅ Website plays the MP3
            const audio = new Audio(audioUrl);
            audio.play();
  
            // ✅ Clean
            document.getElementById("docInput").value = "";
          }}
          style={{
            marginLeft: 10,
            background: "#10b981",
            padding: "10px 20px",
            borderRadius: 6,
            color: "white",
          }}
        >
          Send
        </button>
      </div>
    );
  }