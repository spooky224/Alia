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

  const category = "bactol";
  const product = "bactol_savon_professionnel";

  // ✅ Slide transitions (UNCHANGED)
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
  // 🔥 STREAM → INTRO PIPELINE (WITH STABILIZATION DELAY)
  // =========================================================
  const handleStreamReady = () => {
    console.log("[Rep] ✅ handleStreamReady CALLED");

    if (introStartedRef.current) {
      console.warn("[Rep] intro already started — skipping");
      return;
    }
    introStartedRef.current = true;

    const INTRO_DELAY_MS = 3500; // ✅ tune 2500–4000ms if needed
    console.log(`[Rep] ⏳ delaying intro by ${INTRO_DELAY_MS}ms`);

    setTimeout(async () => {
      try {
        console.log("[Rep] 🔊 starting intro audio");
        const audio = new Audio("http://localhost:8000/intro/intro.wav");

        audio.onplay = () => {
          console.log("[Rep] ✅ intro audio started");
        };

        audio.onended = () => {
          console.log("[Rep] ✅ intro audio ended → enabling RepPanel");
          setIntroDone(true);
        };

        // ✅ Start intro audio
        await audio.play();

        // ✅ Trigger backend lipsync AFTER audio starts
        console.log("[Rep] 🌐 sending POST /intro/play");
        const res = await fetch("http://localhost:8000/intro/play", {
          method: "POST",
        });

        console.log(
          "[Rep] ✅ /intro/play response",
          res.status,
          res.ok
        );
      } catch (err) {
        console.error("[Rep] ❌ intro pipeline failed", err);
        // Fail-safe: never lock UI forever
        setIntroDone(true);
      }
    }, INTRO_DELAY_MS);
  };

  return (
    <div
      style={{
        position: "relative",
        width: "100%",
        height: "100vh",
        backgroundColor: "#000",
        overflow: "hidden",
      }}
    >
      {/* ✅ INPUT PANEL — gated until intro finishes */}
      <div
        style={{
          position: "absolute",
          top: 20,
          left: 20,
          zIndex: 1000,
        }}
      >
        <RepPanel
          setSlides={setSlides}
          setActiveSlide={setActiveSlide}
          disabled={!introDone}
        />
      </div>

      <div style={{ position: "relative", width: "100%", height: "100%" }}>
        {/* ✅ Pixel Streaming drives intro */}
        <PixelStream onStreamReady={handleStreamReady} />

        {/* ✅ Slide overlay (UNCHANGED) */}
        {displayedSlide && (
          <img
            src={`http://localhost:8000/slides/${category}/${product}/${displayedSlide.slide}`}
            alt="TV Slide"
            style={{
              position: "absolute",
              top: "24.7%",
              left: "59.1%",
              width: "33.4%",
              height: "33%",
              objectFit: "cover",
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
  );
}