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
  print("Error in /call:",str(e))
  return {"status":"error","message":str(e)}

@app.api_route("/twiml", methods=["GET", "POST"])
async def twiml():
 twiml_response = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say voice="Polly.Aditi" language="en-IN">Namaste Sir, Riverwood se bol rahe hain. Aaj aapke liye kya kar sakte hain?</Say>
  <Gather input="speech" timeout="10" action="https://agent-production-c7df.up.railway.app/transcribe" method="POST"/>
  <Say voice="Polly.Aditi" language="en-IN">Maaf kijiye, hum aapki baat nahi sun paye.</Say>
</Response>
"""
 return Response(content=twiml_response, media_type="application/xml")


@app.post("/transcribe")
async def transcribe(request:Request):
 try:
  form = await request.form()
  url = form.get("RecordingUrl")
  print("Recording URL:",url)
  if not url:
   return Response(content="<Response><Say voice='alice'>Recording not found.</Say></Response>",media_type="application/xml")
  audio = requests.get(url+".mp3").content
  file = BytesIO(audio)
  file.name = "input.mp3"
  print("Audio downloaded and wrapped")
  openai.api_key = os.getenv("OPENAI_API_KEY")
  transcript = openai.Audio.transcribe(model="whisper-1",file=file,response_format="text")
  print("Transcript:",transcript)
  prompt = f"User said: {transcript}\nReply warmly in Hinglish as Riverwood agent."
  reply = openai.ChatCompletion.create(model="gpt-4o",messages=[{"role":"user","content":prompt}])["choices"][0]["message"]["content"]
  print("GPT reply:",reply)
  return Response(content=f"<Response><Say voice='alice'>{reply}</Say></Response>",media_type="application/xml")
 except Exception as e:
  print("Error in /transcribe:",str(e))
  return Response(content="<Response><Say voice='alice'>Maaf kijiye, kuch takneeki samasya ho gayi hai.</Say></Response>",media_type="application/xml")
