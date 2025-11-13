from fastapi import FastAPI, Request
from fastapi.responses import Response
from twilio.rest import Client
import openai, os, requests
from io import BytesIO

app = FastAPI()

@app.get("/")
def root():
 return {"status":"ok"}

@app.post("/call")
async def make_call(request:Request):
 data = await request.json()
 to = data["to"]
 sid = os.getenv("TWILIO_ACCOUNT_SID")
 token = os.getenv("TWILIO_AUTH_TOKEN")
 from_num = os.getenv("TWILIO_PHONE_NUMBER")
 if not all([sid,token,from_num]):
  return {"status":"error","message":"Missing Twilio credentials"}
 client = Client(sid,token)
 url = "https://agent-production-c7df.up.railway.app/twiml"
 try:
  call = client.calls.create(to=to,from_=from_num,url=url)
  return {"status":"success","sid":call.sid}
 except Exception as e:
  return {"status":"error","message":str(e)}

@app.api_route("/twiml", methods=["GET", "POST"])
async def twiml():
 twiml_response = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say voice="Polly.Aditi" language="en-IN">Namaste Sir, Riverwood se bol rahe hain. Aap kya poochna chahte hain?</Say>
  <Record action="https://agent-production-c7df.up.railway.app/transcribe" method="POST" maxLength="15" trim="do-not-trim" playBeep="true"/>
  <Say voice="Polly.Aditi" language="en-IN">Maaf kijiye, koi awaz record nahi hui.</Say>
</Response>
"""
 return Response(content=twiml_response, media_type="application/xml")

@app.post("/transcribe")
async def transcribe(request:Request):
 try:
  form = await request.form()
  url = form.get("RecordingUrl")
  if not url:
   return Response(content="<Response><Say voice='Polly.Aditi'>Koi audio nahi mila.</Say></Response>", media_type="application/xml")
  audio = requests.get(url + ".mp3").content
  file = BytesIO(audio)
  file.name = "input.mp3"
  openai.api_key = os.getenv("OPENAI_API_KEY")
  transcript = openai.Audio.transcribe(model="whisper-1", file=file, response_format="text")
  if any(word in transcript.lower() for word in ["bye","thank you","thanks","bas","ho gaya","theek hai","close","end call"]):
   goodbye = """<Response><Say voice="Polly.Aditi" language="en-IN">Thank you sir! Aapka din shubh ho.</Say><Hangup/></Response>"""
   return Response(content=goodbye, media_type="application/xml")
  prompt = f"""User said: {transcript}
If the transcript is unclear, incomplete, or sounds cut, DO NOT guess wrong things.
Instead, politely ask: "Sir, kya aap thoda clearly repeat kar sakte hain?"
Otherwise reply warmly in Hinglish as a friendly Riverwood agent.
Keep replies short and natural like a real phone call agent."""
  reply = openai.ChatCompletion.create(model="gpt-4o", messages=[{"role":"user","content":prompt}])["choices"][0]["message"]["content"]
  twiml = f"""<Response><Say voice="Polly.Aditi" language="en-IN">{reply}</Say><Record action="https://agent-production-c7df.up.railway.app/transcribe" method="POST" maxLength="15" trim="do-not-trim" playBeep="true"/></Response>"""
  return Response(content=twiml, media_type="application/xml")
 except Exception as e:
  return Response(content="<Response><Say voice='Polly.Aditi'>Maaf kijiye, system error hua.</Say></Response>", media_type="application/xml")
