import { Link } from "react-router-dom";

export default function App() {
  return (
    <div
      style={{
        height: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        background: "#000",
        color: "white"
      }}
    >
      <h1 style={{ fontSize: "32px", marginBottom: "20px" }}>
        Avatar AI Frontend
      </h1>

      <p style={{ fontSize: "18px", marginBottom: "40px" }}>
        Choose how you want to interact with the avatar:
      </p>

      <Link to="/rep">
        <button
          style={{
            padding: "12px 24px",
            margin: "10px",
            background: "#2563eb",
            border: "none",
            borderRadius: "8px",
            color: "white",
            fontSize: "16px"
          }}
        >
          Rep Mode
        </button>
      </Link>

      <Link to="/doctor">
        <button
          style={{
            padding: "12px 24px",
            margin: "10px",
            background: "#10b981",
            border: "none",
            borderRadius: "8px",
            color: "white",
            fontSize: "16px"
          }}
        >
          Doctor Mode
        </button>
      </Link>
    </div>
  );
}