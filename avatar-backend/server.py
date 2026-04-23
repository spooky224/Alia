from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

import os
import time
import json
import threading
import subprocess
from lipSync.viseme_map import PHONEME_TO_VISEME, get_curve_weights
import sys

from gtts import gTTS
from pydub import AudioSegment
from pythonosc.udp_client import SimpleUDPClient

from orchestrator.orchestrator import handle_message


# =================================================
# APP SETUP
# =================================================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# =================================================
# CONSTANTS
# =================================================
AUDIO_PATH = os.path.expanduser("~/UnrealSpeech/LiveSpeech.wav")
LIPSYNC_SCRIPT = os.path.abspath("lipSync/lipSync.py")

INTRO_VISEMES_PATH = os.path.abspath("intro/intro_visemes.json")
INTRO_AUDIO_PATH = os.path.abspath("intro/intro.wav")

READY_SIGNAL = "/tmp/lipsync_ready"
START_SIGNAL = "/tmp/lipsync_start"

BASE_PRESENTATIONS_DIR = os.path.abspath(
    "presentation_agent/presentations"
)

OSC_IP = "127.0.0.1"
OSC_PORT = 7777

OSC_START_ROUTE = "/lipsync/start"
OSC_STOP_ROUTE = "/lipsync/stop"


# =================================================
# OSC CLIENT
# =================================================
osc_client = SimpleUDPClient(OSC_IP, OSC_PORT)


# =================================================
# MODELS
# =================================================
class TextMessage(BaseModel):
    message: str


# =================================================
# UTILS
# =================================================
def log(msg: str):
    print(f"[server] {msg}", flush=True)
    
def reset_face_to_neutral():
    """
    Explicitly reset all facial curves to neutral (0.0).
    Unreal keeps last OSC values unless we do this.
    """
    log("Resetting face to neutral")

    neutral_curves = get_curve_weights("REST")

    for curve_name in neutral_curves.keys():
        osc_client.send_message("/curve", [curve_name, 0.0])

    # small delay so Unreal applies the reset
    time.sleep(0.05)

    log("Face reset complete")


def cleanup_flags():
    for path in (READY_SIGNAL, START_SIGNAL):
        if os.path.exists(path):
            os.remove(path)


def generate_wav(text: str):
    log("Generating TTS WAV")

    tmp_mp3 = "/tmp/tts.mp3"
    gTTS(text).save(tmp_mp3)

    audio = AudioSegment.from_mp3(tmp_mp3)
    audio = audio.set_frame_rate(44100)
    audio = audio.set_channels(1)
    audio = audio.set_sample_width(2)

    audio.export(AUDIO_PATH, format="wav")
    os.remove(tmp_mp3)


# =================================================
# ✅ ORCHESTRATOR ENTRYPOINT
# =================================================
@app.post("/process_message")
def process_message(data: TextMessage):
    log(f"Received user message: {data.message}")
    return handle_message(data.message)


# =================================================
# ✅ LIVE SPEECH + LIPSYNC (UNCHANGED)
# =================================================
@app.post("/speak")
def speak(data: TextMessage):
    cleanup_flags()
    generate_wav(data.message)

    log("Launching lipSync preprocessing")
    subprocess.Popen([sys.executable, LIPSYNC_SCRIPT])

    log("Waiting for lipSync READY signal")
    while not os.path.exists(READY_SIGNAL):
        time.sleep(0.01)

    log("✅ lipSync READY — returning audio")
    return FileResponse(AUDIO_PATH, media_type="audio/wav")


@app.post("/start_lipsync")
def start_lipsync():
    log("✅ START signal received from frontend")
    open(START_SIGNAL, "w").close()
    return {"status": "started"}


# =================================================
# ✅ INTRO (CACHED, NO WHISPER)
# =================================================
def play_intro_visemes():
    log("▶ Playing cached intro visemes")

    if not os.path.exists(INTRO_VISEMES_PATH):
        log("❌ intro_visemes.json not found")
        return

    with open(INTRO_VISEMES_PATH, "r") as f:
        visemes = json.load(f)

    t0 = time.time()

    while True:
        now = time.time() - t0
        active = next(
            (v for v in visemes if v["start"] <= now < v["end"]),
            None
        )

        if active:
            osc_client.send_message(OSC_START_ROUTE, 0)
            for curve, value in active["curves"].items():
                osc_client.send_message("/curve", [curve, float(value)])

        if now > visemes[-1]["end"]:
            osc_client.send_message(OSC_STOP_ROUTE, 0)
            log("✅ Intro lipsync finished")
            reset_face_to_neutral()
            break

        time.sleep(0.02)


@app.post("/intro/play")
def intro_play():
    log("✅ /intro/play received")
    threading.Thread(
        target=play_intro_visemes,
        daemon=True,
    ).start()

    return {"status": "intro_started"}


# =================================================
# ✅ INTRO AUDIO SERVING
# =================================================
@app.get("/intro/intro.wav")
def get_intro_audio():
    return FileResponse(INTRO_AUDIO_PATH, media_type="audio/wav")


# =================================================
# ✅ SLIDE IMAGE SERVING
# =================================================
@app.get("/slides/{category}/{product}/{filename}")
def get_slide(category: str, product: str, filename: str):
    """
    Serves slide PNGs to the frontend.
    """
    slide_path = os.path.join(
        BASE_PRESENTATIONS_DIR,
        category,
        product,
        filename,
    )

    if not os.path.isfile(slide_path):
        return {"error": "Slide not found"}

    return FileResponse(slide_path, media_type="image/png")