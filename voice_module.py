import os
import requests

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("ELEVEN_VOICE_ID")  # hGb0Exk8cp4vQEnwolxa for Ayesha

def speak(text: str, filename: str = "output.mp3"):
    print(f"🔊 Generating audio with ElevenLabs (Ayesha): {text}")
    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
        headers = {
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"🎧 Audio saved to {filename} ({os.path.getsize(filename)} bytes)")
        else:
            print("❌ ElevenLabs error:", response.status_code, response.text)
    except Exception as e:
        print("❌ ElevenLabs exception:", e)
