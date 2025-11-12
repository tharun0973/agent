import os
from twilio.rest import Client

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

def make_call(to: str, url: str) -> str:
    print(f"📞 Initiating call to {to} with audio from {url}")
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        call = client.calls.create(
            to=to,
            from_=TWILIO_PHONE_NUMBER,
            url=url
        )
        print("✅ Twilio call SID:", call.sid)
        return call.sid
    except Exception as e:
        print("❌ Twilio call error:", e)
        return "error"
