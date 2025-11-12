from gtts import gTTS
import os

def speak(text: str, filename: str = "output.mp3"):
    print(f"🔊 Generating audio with gTTS: {text}")
    try:
        tts = gTTS(text)
        tts.save(filename)
        if os.path.exists(filename) and os.path.getsize(filename) > 1000:
            print(f"🎧 Audio saved to {filename} ({os.path.getsize(filename)} bytes)")
        else:
            print(f"❌ Audio file {filename} is too small or missing")
    except Exception as e:
        print("❌ gTTS error:", e)
