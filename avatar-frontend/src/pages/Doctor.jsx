import PixelStream from "../components/PixelStream";
import DoctorPanel from "../components/DoctorPanel";

export default function Doctor() {
  const sendText = async (msg) => {
    if (!msg.trim()) return;
    await fetch("http://localhost:5000/send_text", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: msg }),
    });
  };

  return (
    <div style={{ height: "100vh", display: "flex", flexDirection: "column" }}>
      <DoctorPanel sendText={sendText} />
      <PixelStream />
    </div>
  );
}