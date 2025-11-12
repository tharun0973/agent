import os
import requests

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVEN_VOICE_ID = os.getenv("ELEVEN_VOICE_ID")

def speak(text: str, filename: str = "output.mp3"):
    print(f"🔊 Generating audio for: {text}")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVEN_VOICE_ID}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=5)
        print("✅ ElevenLabs response:", response.status_code)
        response.raise_for_status()
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"🎧 Audio saved to {filename}")
    except Exception as e:
        print("❌ ElevenLabs error:", e)
        with open(filename, "wb") as f:
            f.write(b"")  # Write empty fallback
