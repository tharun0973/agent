from fastapi import FastAPI, Request
from fastapi.responses import Response
from twilio.rest import Client
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant
import openai, os, requests
from io import BytesIO

app = FastAPI()

@app.get("/")
def root():
    return {"status":"ok"}

@app.get("/token")
def generate_token():
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    api_key = os.getenv("TWILIO_API_KEY")
    api_secret = os.getenv("TWILIO_API_SECRET")
    twiml_app_sid = os.getenv("TWILIO_TWIML_APP_SID")
    token = AccessToken(account_sid, api_key, api_secret, identity="web_user")
    voice = VoiceGrant(outgoing_application_sid=twiml_app_sid)
    token.add_grant(voice)
    return {"token": token.to_jwt().decode()}

@app.post("/call")
async def make_call(request: Request):
    sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth = os.getenv("TWILIO_AUTH_TOKEN")
    from_num = os.getenv("TWILIO_PHONE_NUMBER")
    client = Client(sid, auth)
    call = client.calls.create(
        to="client:web_user",
        from_=from_num,
        url="https://agent-production-c7df.up.railway.app/twiml",
        method="GET"
    )
    return {"status":"success","sid":call.sid}

@app.get("/twiml")
async def twiml():
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
<Say voice="Polly.Aditi" language="en-IN">Namaste Sir, Riverwood se bol rahe hain. Aap kya poochna chahte hain?</Say>
<Record action="https://agent-production-c7df.up.railway.app/transcribe" method="POST" maxLength="15" trim="do-not-trim" playBeep="true" timeout="4"/>
<Say voice="Polly.Aditi" language="en-IN">Maaf kijiye, koi awaz record nahi hui.</Say>
</Response>
"""
    return Response(content=xml, media_type="application/xml")

@app.post("/transcribe")
async def transcribe(request: Request):
    try:
        form = await request.form()
        rec = form.get("RecordingUrl")
        if not rec:
            return Response(content="<Response><Say voice='Polly.Aditi'>Koi audio nahi mila.</Say></Response>",media_type="application/xml")
        audio = requests.get(rec + ".mp3").content
        if len(audio) < 2000:
            transcript = ""
        else:
            file = BytesIO(audio)
            file.name = "input.mp3"
            openai.api_key = os.getenv("OPENAI_API_KEY")
            try:
                transcript = openai.Audio.transcribe(model="gpt-4o-transcribe", file=file, response_format="text")
            except:
                transcript = ""
        if any(x in transcript.lower() for x in ["bye","thank you","thanks","bas","ho gaya","theek hai","close","end call"]):
            return Response(content="<Response><Say voice='Polly.Aditi' language='en-IN'>Thank you sir! Aapka din shubh ho.</Say><Hangup/></Response>",media_type="application/xml")
        if not transcript or len(transcript.strip())<3:
            return Response(content="""<Response><Say voice='Polly.Aditi' language='en-IN'>Sir, aapki awaaz clear nahi aayi, kya aap repeat karenge?</Say><Record action="https://agent-production-c7df.up.railway.app/transcribe" method="POST" maxLength="15" trim="do-not-trim" playBeep="true" timeout="4"/></Response>""",media_type="application/xml")
        prompt = f"User said: {transcript}. Reply warmly in Hinglish, short and natural."
        reply = openai.ChatCompletion.create(model="gpt-4o",messages=[{"role":"user","content":prompt}])["choices"][0]["message"]["content"]
        twxml = f"""<Response><Say voice="Polly.Aditi" language="en-IN">{reply}</Say><Record action="https://agent-production-c7df.up.railway.app/transcribe" method="POST" maxLength="15" trim="do-not-trim" playBeep="true" timeout="4"/></Response>"""
        return Response(content=twxml,media_type="application/xml")
    except:
        return Response(content="<Response><Say voice='Polly.Aditi'>Maaf kijiye, system error hua.</Say></Response>",media_type="application/xml")
