from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from agent_logic import generate_reply
from voice_module import speak
from twilio_module import make_call
from twilio.base.exceptions import TwilioRestException  # ✅ Add this

app = FastAPI()

@app.get("/ping")
def ping():
    print("✅ /ping received — app is alive")
    return {"status": "ok"}

@app.get("/greet")
def greet_user():
    print("🔊 /greet triggered")
    greeting = (
        "Namaste! Main hoon Miss Riverwood — aapki AI voice agent from Riverwood Projects. Kaise madad kar sakti hoon aaj?"
    )
    try:
        speak(greeting, filename="greeting.mp3")
        return FileResponse("greeting.mp3", media_type="audio/mpeg")
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
    data = await request.json()
    to_number = data.get("to")
    audio_url = data.get("url")
    print(f"📞 /call triggered for {to_number} with audio {audio_url}")
    try:
        sid = make_call(to_number, audio_url)
        print(f"✅ Twilio call SID: {sid}")
        return {"status": "calling", "sid": sid}
    except TwilioRestException as e:
        print(f"❌ Twilio call error: {e.code} — {e.msg}")
        return {"status": "error", "sid": "error"}
    except Exception as e:
        print(f"❌ Unexpected error during call: {e}")
        return {"status": "error", "sid": "error"}
