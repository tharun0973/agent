import os
from dotenv import load_dotenv
from elevenlabs import play, save, VoiceSettings
from elevenlabs.client import ElevenLabs

# Load environment variables
load_dotenv()

# Load API key and voice ID from .env
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("ELEVEN_VOICE_ID")

# Initialize ElevenLabs client
client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

def speak(text: str, filename: str = "output.mp3") -> None:
    """Generate speech from text and save to file."""
    audio = client.text_to_speech.convert(
        voice_id=VOICE_ID,
        voice_settings=VoiceSettings(stability=0.5, similarity_boost=0.75),
        text=text
    )
    save(audio, filename)

def stream(text: str) -> None:
    """Play speech directly from text."""
    audio = client.text_to_speech.convert(
        voice_id=VOICE_ID,
        voice_settings=VoiceSettings(stability=0.5, similarity_boost=0.75),
        text=text
    )
    play(audio)
