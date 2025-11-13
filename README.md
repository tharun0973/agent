cat << 'EOF' > README.md
# AI Voice Call Agent

A minimal Python-based voice call agent that can answer calls, play a greeting, and respond with AI-generated speech using Twilio and a TTS provider (OpenAI/ElevenLabs).

## Features
- Receives incoming phone calls
- Plays greeting audio
- Generates AI voice responses
- Uses Twilio for handling calls
- Clean modular code structure

## Setup

### 1. Clone the repo
git clone https://github.com/tharun0973/agent.git
cd agent

### 2. Install dependencies
pip install -r requirements.txt

### 3. Create .env file
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxx
TWILIO_PHONE_NUMBER=+1xxxxxxxxxx

OPENAI_API_KEY=xxxxxxxx
# OR
ELEVENLABS_API_KEY=xxxxxxxx

### 4. Run the agent
python main.py

## Deploy
Use Railway or Render. Set your public URL as the Twilio Voice Webhook.

## Customize
- Replace greeting.mp3 with your own greeting
- Change TTS voice in voice_module.py
- Add conversation flow inside agent_logic.py

## License
MIT
EOF
