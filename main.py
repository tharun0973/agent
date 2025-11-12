from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from agent_logic import generate_reply
from voice_module import speak
from twilio_module import make_call

app = FastAPI()

@app.get("/greet")
def greet_user():
    greeting = (
        "Namaste! Main hoon Miss Riverwood — aapki AI voice agent from Riverwood Projects. Kaise madad kar sakti hoon aaj?"
    )
    speak(greeting, filename="greeting.mp3")
    return FileResponse("greeting.mp3", media_type="audio/mpeg")

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_input = data.get("message", "")
    response_text = generate_reply(user_input)
    speak(response_text, filename="output.mp3")
    return {"response": response_text}

@app.get("/play")
def play_audio():
    return FileResponse("output.mp3", media_type="audio/mpeg")

@app.post("/call")
async def call_user(request: Request):
    data = await request.json()
    to_number = data.get("to")
    audio_url = data.get("url")  # Must be public (Railway/ngrok)
    sid = make_call(to_number, audio_url)
    return {"status": "calling", "sid": sid}
