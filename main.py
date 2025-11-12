from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from agent_logic import generate_reply
from voice_module import speak
from twilio_module import make_call
from twilio.base.exceptions import TwilioRestException
import os

app = FastAPI()

@app.get("/ping")
def ping():
    print("✅ /ping received — app is alive")
    return {"status": "ok"}

@app.get("/greet")
def greet_user(request: Request):
    print("🔊 /greet triggered by", request.headers.get("User-Agent"))
    greeting = (
        "Namaste! Main hoon Miss Riverwood — aapki AI voice agent from Riverwood Projects. Kaise madad kar sakti hoon aaj?"
    )
    try:
        speak(greeting, filename="greeting.mp3")
        if not os.path.exists("greeting.mp3") or os.path.getsize("greeting.mp3") < 1000:
            raise Exception("MP3 file not generated or too small")
        return FileResponse("greeting.mp3", media_type="audio/mpeg", filename="greeting.mp3")
    except Exception as e:
        print("❌ Error generating greeting:", e)
        return JSONResponse(content={"error": "Failed to generate greeting"}, status_code=500)

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_input = data.get("message", "")
    print(f"💬 /chat received: {user_input}")
    response_text = generate_reply(user_input)
    speak(response_text, filename="output.mp3")
    return {"response": response_text}

@app.get("/play")
def play_audio():
    print("🔊 /play triggered")
    return FileResponse("output.mp3", media_type="audio/mpeg")

@app.post("/call")
async def call_user(request: Request):
    print("📞 /call route hit")
    try:
        data = await request.json()
        print("📦 Payload received:", data)

        to_number = data.get("to")
        audio_url = data.get("url")

        if not to_number or not audio_url:
            raise ValueError("Missing 'to' or 'url' in payload")

        print(f"📞 Initiating call to {to_number} with audio {audio_url}")
        sid = make_call(to_number, audio_url)
        print(f"✅ Twilio call SID: {sid}")
        return {"status": "calling", "sid": sid}

    except TwilioRestException as e:
        print(f"❌ Twilio error: {e.code} — {e.msg}")
        return {"status": "error", "sid": "twilio_error", "message": str(e)}

    except Exception as e:
        print(f"❌ General error in /call:", e)
        return {"status": "error", "sid": "general_error", "message": str(e)}

@app.on_event("startup")
def generate_greeting_once():
    greeting = (
        "Namaste! Main hoon Miss Riverwood — aapki AI voice agent from Riverwood Projects. Kaise madad kar sakti hoon aaj?"
    )
    print("🚀 Pre-generating greeting.mp3 at startup...")
    speak(greeting, filename="greeting.mp3")
