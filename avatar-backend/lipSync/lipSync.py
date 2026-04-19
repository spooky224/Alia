# lipSync.py
import os
import time
from pythonosc.udp_client import SimpleUDPClient

os.environ["PHONEMIZER_ESPEAK_PATH"] = "/opt/homebrew/bin/espeak-ng"
os.environ["ESPEAK_DATA_PATH"] = "/opt/homebrew/lib/espeak-ng-data"

import whisper_timestamped as whisper
from phonemizer import phonemize
from viseme_map import PHONEME_TO_VISEME, get_curve_weights

# ==========================
# CONFIG
# ==========================
OSC_IP = "127.0.0.1"
OSC_PORT = 7777
osc_client = SimpleUDPClient(OSC_IP, OSC_PORT)

OSC_STOP_ROUTE = "/lipsync/stop"
OSC_START_ROUTE = "/lipsync/start"

WAV_PATH = os.path.expanduser("~/UnrealSpeech/LiveSpeech.wav")

READY_SIGNAL = "/tmp/lipsync_ready"
START_SIGNAL = "/tmp/lipsync_start"

def log(msg):
    print(f"[lipSync] {msg}", flush=True)

# ==========================
# RESET HELPERS
# ==========================
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

# ==========================
# IPA → ARPABET
# ==========================
IPA_TO_ARPAbet = {
    "iː": "IY", "i": "IY", "ɪ": "IH", "eɪ": "EY", "e": "EH",
    "ɛ": "EH", "æ": "AH", "aɪ": "AY", "aʊ": "AW", "ɑː": "AA",
    "ɑ": "AA", "a": "AH", "ɔɪ": "OY", "ɔː": "AO", "ɔ": "AO",
    "oʊ": "OH", "o": "OH", "ʊ": "UH", "uː": "UW", "u": "UW",
    "ʌ": "AH", "ə": "AH",
    "tʃ": "CH", "dʒ": "JH",
    "p": "P", "b": "B", "t": "T", "d": "D",
    "k": "K", "g": "G",
    "f": "F", "v": "V",
    "θ": "TH", "ð": "DH",
    "s": "S", "z": "Z",
    "ʃ": "SH", "ʒ": "ZH",
    "m": "M", "n": "N", "l": "L", "r": "R",
    "j": "Y", "w": "W",
}

def ipa_to_arpabet(s):
    out, i = [], 0
    while i < len(s):
        if s[i:i+3] in IPA_TO_ARPAbet:
            out.append(IPA_TO_ARPAbet[s[i:i+3]])
            i += 3
        elif s[i:i+2] in IPA_TO_ARPAbet:
            out.append(IPA_TO_ARPAbet[s[i:i+2]])
            i += 2
        elif s[i] in IPA_TO_ARPAbet:
            out.append(IPA_TO_ARPAbet[s[i]])
            i += 1
        else:
            i += 1
    return out or ["SIL"]

def extract_timed_visemes(wav):
    log("Loading audio + Whisper model")
    audio = whisper.load_audio(wav)
    model = whisper.load_model("tiny")

    log("Running Whisper transcription (HEAVY)")
    result = whisper.transcribe(model, audio, language="en")

    timeline = []
    for seg in result["segments"]:
        for word in seg["words"]:
            raw = phonemize(
                word["text"],
                backend="espeak",
                language="en-us",
                with_stress=False,
                preserve_punctuation=False,
            )

            phonemes = ipa_to_arpabet(raw)
            dur = (word["end"] - word["start"]) / len(phonemes)

            for i, p in enumerate(phonemes):
                timeline.append({
                    "start": word["start"] + i * dur,
                    "end": word["start"] + (i + 1) * dur,
                    "curves": get_curve_weights(
                        PHONEME_TO_VISEME.get(p, "REST")
                    ),
                })
    return timeline

# ==========================
# MAIN
# ==========================
if __name__ == "__main__":
    # cleanup flags
    for f in (READY_SIGNAL, START_SIGNAL):
        if os.path.exists(f):
            os.remove(f)

    log("Starting heavy lip-sync preprocessing")
    visemes = extract_timed_visemes(WAV_PATH)

    if not visemes:
        log("No visemes extracted, exiting")
        exit(0)

    log("✅ LipSync READY (heavy work done)")
    open(READY_SIGNAL, "w").close()

    log("Waiting for START signal from frontend...")
    while not os.path.exists(START_SIGNAL):
        time.sleep(0.001)

    os.remove(START_SIGNAL)
    log("✅ LipSync RUNNING")

    t0 = time.time()

    while True:
        now = time.time() - t0
        active = next((v for v in visemes if v["start"] <= now < v["end"]), None)

        if active:
            osc_client.send_message(OSC_START_ROUTE, 0)
            for k, v in active["curves"].items():
                osc_client.send_message("/curve", [k, float(v)])

        if now > visemes[-1]["end"]:
            osc_client.send_message(OSC_STOP_ROUTE, 0)
            log("✅ LipSync Stop Sent")
            break
        time.sleep(0.02)
    log("✅ LipSync FINISHED")
    reset_face_to_neutral()