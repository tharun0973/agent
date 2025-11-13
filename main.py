from fastapi import FastAPI, Request
from fastapi.responses import Response
from twilio.rest import Client
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

app = FastAPI()

# OpenAI client
client_openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@app.get("/")
def root():
    return {"status": "ok"}


@app.post("/call")
async def make_call(request: Request):
    data = await request.json()
    to = data["to"]

    sid = os.getenv("TWILIO_ACCOUNT_SID")
    token = os.getenv("TWILIO_AUTH_TOKEN")
    from_num = os.getenv("TWILIO_PHONE_NUMBER")

    client_twilio = Client(sid, token)
    url = "https://agent-production-c7df.up.railway.app/twiml"

    call = client_twilio.calls.create(
        to=to,
        from_=from_num,
        url=url,
        method="GET"
    )

    return {"status": "success", "sid": call.sid}


@app.get("/twiml")
async def twiml():
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say voice="Polly.Aditi" language="en-IN">
    Namaste Sir, Riverwood se bol rahe hain. Aap kya poochna chahte hain?
  </Say>

  <Gather input="speech" speechTimeout="auto"
     action="https://agent-production-c7df.up.railway.app/transcribe"
     method="POST" />

  <Say voice="Polly.Aditi" language="en-IN">
    Maaf kijiye, hum aapki baat nahi sun paye.
  </Say>
</Response>"""
    return Response(content=xml, media_type="application/xml")


@app.post("/transcribe")
async def transcribe(request: Request):
    form = await request.form()
    speech = form.get("SpeechResult") or ""

    # No speech detected
    if not speech.strip():
        return Response(
            content="""<Response>
                <Say voice="Polly.Aditi" language="en-IN">
                    Sir, awaaz clear nahi aayi. Kya aap repeat karenge?
                </Say>
                <Gather input="speech" speechTimeout="auto"
                    action="https://agent-production-c7df.up.railway.app/transcribe"
                    method="POST" />
            </Response>""",
            media_type="application/xml"
        )

    # End call triggers
    if any(w in speech.lower() for w in ["bye", "thanks", "thank you", "end", "stop"]):
        return Response(
            content="""<Response>
                <Say voice="Polly.Aditi" language="en-IN">
                    Dhanyavaad Sir! Aapka din shubh ho.
                </Say>
                <Hangup/>
            </Response>""",
            media_type="application/xml"
        )

    # Generate GPT reply
    result = client_openai.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": f"User said: {speech}. Reply naturally in short Hinglish. If user asks for English, reply in English."
        }]
    )

    reply = result.choices[0].message.content

    xml = f"""<Response>
        <Say voice="Polly.Aditi" language="en-IN">{reply}</Say>
        <Gather input="speech" speechTimeout="auto"
            action="https://agent-production-c7df.up.railway.app/transcribe"
            method="POST" />
    </Response>"""

    return Response(content=xml, media_type="application/xml")
