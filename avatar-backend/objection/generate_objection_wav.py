from gtts import gTTS
from pydub import AudioSegment
import os

TEXT = "Okay, I have stopped talking. What is your objection or question?"
OUT_WAV = "objection.wav"

gTTS(TEXT).save("tmp.mp3")

audio = AudioSegment.from_mp3("tmp.mp3")
audio = audio.set_frame_rate(44100).set_channels(1).set_sample_width(2)
audio.export(OUT_WAV, format="wav")

os.remove("tmp.mp3")
print("✅ objection.wav generated")
