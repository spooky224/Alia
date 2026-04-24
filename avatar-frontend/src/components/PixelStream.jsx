import { useEffect, useRef } from "react";

export default function PixelStream({ onStreamReady }) {
  const iframeRef = useRef(null);
  const readySentRef = useRef(false);
  const srcSetRef = useRef(false); // ✅ CRITICAL: prevents reload

  console.log("[PixelStream] component rendered");

  useEffect(() => {
    console.log("[PixelStream] useEffect running");

    // ✅ SET IFRAME SRC ONLY ONCE (PREVENTS STREAM RELOAD)
    if (!srcSetRef.current) {
      iframeRef.current.src =
        "http://127.0.0.1:8080/?" +
        "autoconnect=true&autoplay=true&muted=true&playsinline=true";

      srcSetRef.current = true;
      console.log("[PixelStream] ✅ iframe src set (once)");
    }

    iframeRef.current.onload = () => {
      console.log("[PixelStream] ✅ iframe onload fired");

      // --------------------------------------------------
      // OPTIONAL: try overlay injection (never blocks flow)
      // --------------------------------------------------
      try {
        const iframeDoc = iframeRef.current.contentDocument;

        if (!iframeDoc) {
          console.warn(
            "[PixelStream] ⚠ iframeDoc is null (cross-origin) — skipping overlay injection"
          );
        } else {
          console.log("[PixelStream] iframeDoc available — injecting overlay disabler");

          
        }
      } catch (err) {
        console.warn(
          "[PixelStream] ⚠ overlay injection failed (expected):",
          err
        );
      }

      // --------------------------------------------------
      // ✅ ALWAYS notify parent ONCE
      // --------------------------------------------------
      if (!readySentRef.current) {
        readySentRef.current = true;
        console.log("[PixelStream] ✅ stream ready → notifying parent");

        if (typeof onStreamReady === "function") {
          onStreamReady();
        } else {
          console.error(
            "[PixelStream] ❌ onStreamReady is not a function",
            onStreamReady
          );
        }
      } else {
        console.warn("[PixelStream] stream-ready already sent, skipping");
      }
    };
  }, [onStreamReady]);

  return (
    <iframe
      ref={iframeRef}
      style={{
        width: "100%",
        height: "100%",
        border: "none",
      }}
      allow="autoplay; camera; microphone"
    />
  );
}
