import os
from gtts import gTTS
from pydub import AudioSegment

# ✅ TARGET PATH
INTRO_DIR = os.path.abspath("intro")
os.makedirs(INTRO_DIR, exist_ok=True)

INTRO_WAV_PATH = os.path.join(INTRO_DIR, "intro.wav")

INTRO_TEXT = """
Hello Doctor.
I am Alia, your virtual medical assistant.
I am here to support you with product presentations, explanations, and discussions, adapted to your specialty and preferences.
Before we begin, I would like to know a bit more about you.
Can you tell me what is you speciality?
""".strip()

print("[intro] Generating global intro WAV")

tmp_mp3 = "/tmp/intro_tts.mp3"
gTTS(INTRO_TEXT).save(tmp_mp3)

audio = AudioSegment.from_mp3(tmp_mp3)
audio = audio.set_frame_rate(44100)
audio = audio.set_channels(1)
audio = audio.set_sample_width(2)

audio.export(INTRO_WAV_PATH, format="wav")
os.remove(tmp_mp3)

print(f"[intro] ✅ intro.wav generated at {INTRO_WAV_PATH}")