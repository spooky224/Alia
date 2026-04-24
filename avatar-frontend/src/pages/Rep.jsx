import { useState, useEffect, useRef } from "react";
import PixelStream from "../components/PixelStream";
import RepPanel from "../components/RepPanel";

export default function Rep() {
  console.log("[Rep] component rendered");

  const [slides, setSlides] = useState([]);
  const [activeSlide, setActiveSlide] = useState(0);
  const [displayedSlide, setDisplayedSlide] = useState(null);
  const [isTransitioning, setIsTransitioning] = useState(false);

  const [introDone, setIntroDone] = useState(false);
  const introStartedRef = useRef(false);

  const currentSlide = slides[activeSlide];

  const [category, setCategory] = useState(null);
  const [product, setProduct] = useState(null);

  // =========================================================
  // ✅ Slide transitions (UNCHANGED)
  // =========================================================
  useEffect(() => {
    if (!currentSlide) {
      setDisplayedSlide(null);
      return;
    }

    setIsTransitioning(true);
    const timeout = setTimeout(() => {
      setDisplayedSlide(currentSlide);
      setIsTransitioning(false);
    }, 300);

    return () => clearTimeout(timeout);
  }, [currentSlide]);

  // =========================================================
  // ✅ STREAM → INTRO PIPELINE (UNCHANGED)
  // =========================================================
  const handleStreamReady = () => {
    console.log("[Rep] ✅ handleStreamReady CALLED");

    if (introStartedRef.current) return;
    introStartedRef.current = true;

    const INTRO_DELAY_MS = 3500;

    setTimeout(async () => {
      try {
        const audio = new Audio("http://localhost:8000/intro/intro.wav");
        audio.onended = () => setIntroDone(true);
        await audio.play();
        await fetch("http://localhost:8000/intro/play", { method: "POST" });
      } catch {
        setIntroDone(true);
      }
    }, INTRO_DELAY_MS);
  };

  // =========================================================
  // ✅ FINAL POLISHED LAYOUT
  // =========================================================
  return (
    <div
      style={{
        display: "flex",
        width: "100%",
        height: "98vh",
        overflow: "hidden",
        background:
          "linear-gradient(180deg, #050505 0%, #000 30%, #000 70%, #050505 100%)",
      }}
    >
      {/* ================================================= */}
      {/* ✅ LEFT — STREAM STAGE (16:9 CONTAINMENT)          */}
      {/* ================================================= */}
      <div
        style={{
          flex: 1,
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            width: "100%",
            maxWidth: "calc(100vh * 16 / 9)",
            aspectRatio: "16 / 9",
            position: "relative",
            background: "#000",
          }}
        >
          <PixelStream onStreamReady={handleStreamReady} />

          {/* ✅ Slides stay visually bound to the avatar */}
          {displayedSlide && category && product && (
            <img
              src={`http://localhost:8000/slides/${category}/${product}/${displayedSlide.slide}`}
              alt="TV Slide"
              style={{
                position: "absolute",
                right: "1%",
                top: "21.1%",
                width: "37.8%",
                height: "37%",
                maxWidth: 520,
                aspectRatio: "16 / 9",
                objectFit: "cover",
                boxShadow: "0 12px 32px rgba(0,0,0,0.35)",
                opacity: isTransitioning ? 0 : 1,
                transform: isTransitioning
                  ? "translateY(16px)"
                  : "translateY(0)",
                transition:
                  "opacity 280ms ease-out, transform 320ms ease-out",
                pointerEvents: "none",
                zIndex: 10,
              }}
            />
          )}
        </div>
      </div>

      {/* ================================================= */}
      {/* ✅ RIGHT — CHAT CONSOLE (HARMONIZED)               */}
      {/* ================================================= */}
      <div
        style={{
          width: 480,
          minWidth: 420,
          height: "100%",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          padding: "80px 16px 16px 16px",
          background:
            "linear-gradient(180deg, #050505 0%, #000 40%, #000 100%)",
        }}
      >
        <RepPanel
          setSlides={setSlides}
          setActiveSlide={setActiveSlide}
          setCategory={setCategory}
          setProduct={setProduct}
          disabled={!introDone}
        />
      </div>
    </div>
  );
}
