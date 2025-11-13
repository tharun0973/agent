from fastapi import FastAPI, Request, Form
from fastapi.responses import Response
from twilio.rest import Client
import openai
import os
import requests
from io import BytesIO

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok"}

@app.post("/call")
async def make_call(request: Request):
    data = await request.json()
    to = data["to"]
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_PHONE_NUMBER")
    if not all([account_sid, auth_token, from_number]):
        return {"status": "error", "message": "Missing Twilio credentials"}
    client = Client(account_sid, auth_token)
    twiml_url = "https://agent-production-c7df.up.railway.app/twiml"
    try:
        call = client.calls.create(to=to, from_=from_number, url=twiml_url)
        return {"status": "success", "sid": call.sid}
    except Exception as e:
        print("Error in /call:", str(e))
        return {"status": "error", "message": str(e)}

@app.api_route("/twiml", methods=["GET", "POST"])
async def twiml():
    twiml_response = """
<Response>
    <Say voice="Polly.Ayesha">Namaste Sir, Riverwood se bol rahe hain. Aaj aapke liye kya kar sakte hain?</Say>
    <Gather input="speech" timeout="10" action="https://agent-production-c7df.up.railway.app/transcribe" method="POST"/>
    <Say voice="Polly.Ayesha">Maaf kijiye, hum aapki baat nahi sun paye.</Say>
</Response>
""".strip()
    return Response(content=twiml_response, media_type="application/xml")

@app.post("/transcribe")
async def transcribe(request: Request):
    try:
        form = await request.form()
        recording_url = form.get("RecordingUrl")
        print("Recording URL:", recording_url)

        if not recording_url:
            return Response(content="<Response><Say voice='Polly.Ayesha'>Recording not found.</Say></Response>", media_type="application/xml")

        audio_bytes = requests.get(recording_url + ".mp3").content
        audio_file = BytesIO(audio_bytes)
        audio_file.name = "input.mp3"
        print("Audio downloaded and wrapped")

        openai.api_key = os.getenv("OPENAI_API_KEY")
        transcript = openai.Audio.transcribe(
            model="whisper-1",
            file=audio_file,
            response_format="text"
        )
        print("Transcript:", transcript)

        prompt = f"User said: {transcript}\nReply warmly in Hinglish as Riverwood agent."
        reply = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )["choices"][0]["message"]["content"]
        print("GPT reply:", reply)

        return Response(content=f"<Response><Say voice='Polly.Ayesha'>{reply}</Say></Response>", media_type="application/xml")

    except Exception as e:
        print("Error in /transcribe:", str(e))
        fallback = "<Response><Say voice='Polly.Ayesha'>Maaf kijiye, kuch takneeki samasya ho gayi hai.</Say></Response>"
        return Response(content=fallback, media_type="application/xml")
