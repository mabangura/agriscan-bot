# AgriScan WhatsApp AI Bot + Dashboard (Cloud Deployment)

## Features
- AI-powered WhatsApp bot for diagnosing crop diseases
- Dashboard to visualize farmer reports (with location, images, disease)
- Multi-crop support: cassava, cocoa, rice, onion, oil palm

## Setup Instructions

### 1. Install Dependencies
```
pip install -r requirements.txt
```

### 2. Set up .env
Copy `.env.template` to `.env` and fill in your Twilio credentials.

### 3. Run the Bot + Dashboard
```
python app.py       # for the WhatsApp bot
python dashboard.py # for the visualization dashboard
```

### 4. Deploy to Render or Replit
- Create a new web service
- Upload this project
- Set build command: `pip install -r requirements.txt`
- Set start command: `python app.py`
