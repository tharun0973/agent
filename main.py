from fastapi import FastAPI, Request
from twilio.rest import Client
import os

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok"}

@app.post("/call")
async def make_call(request: Request):
    data = await request.json()
    to = data["to"]
    url = data["url"]

    # Load Twilio credentials from Railway environment variables
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_PHONE_NUMBER")

    if not all([account_sid, auth_token, from_number]):
        return {"status": "error", "message": "Missing Twilio credentials"}

    client = Client(account_sid, auth_token)

    # Generate Twimlet URL to play the MP3
    twimlet_url = f"https://twimlets.com/echo?Twiml=<Response><Play>{url}</Play></Response>"

    try:
        call = client.calls.create(
            to=to,
            from_=from_number,
            url=twimlet_url
        )
        return {"status": "success", "sid": call.sid}
    except Exception as e:
        return {"status": "error", "message": str(e)}
