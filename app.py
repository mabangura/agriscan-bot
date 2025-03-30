# WhatsApp AI bot Flask app
# Placeholder for app.py

# WhatsApp AI bot Flask app
# Placeholder for app.py

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from requests.auth import HTTPBasicAuth
import sqlite3
import requests
import os
from PIL import Image
from io import BytesIO
import torch
from torchvision import transforms

app = Flask(__name__)

# Twilio credentials from environment
TWILIO_SID = os.environ.get("TWILIO_SID", "AC7c352c2467ca474c4d2d31054e837b12")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "1e8828033db00e5d47decc6e4575973a")

# Load AI model
MODEL_PATH = "cassava_model.pt"
model = torch.load(MODEL_PATH, map_location=torch.device('cpu'))
model.eval()

# Crop classes
CLASS_NAMES = [
    "Cassava Mosaic", "Cassava Bacterial Blight", "Healthy Cassava",
    "Cocoa Black Pod", "Healthy Cocoa",
    "Rice Blast", "Healthy Rice",
    "Oil Palm Anthracnose", "Healthy Oil Palm",
    "Onion Purple Blotch", "Healthy Onion"
]

# Transform
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

# Database setup
DB_PATH = "agriscan.db"
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone TEXT,
    image_url TEXT,
    disease TEXT,
    location TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)''')
conn.commit()

# Firebase voice notes (update with your URLs)
VOICE_RESPONSES = {
    "Cassava Mosaic": "https://firebasestorage.googleapis.com/v0/b/ai-agri-649c0.firebasestorage.app/o/Cut%20n%20burn.mp3?alt=media&token=18a6772e-9c08-4c43-92aa-8c730fcc8e4f",
    "Cassava Bacterial Blight": "https://firebasestorage.googleapis.com/v0/b/ai-agri-649c0.firebasestorage.app/o/Small%20sick.mp3?alt=media&token=f4ce57f7-1e32-48b5-899a-f478e8d26f5b",
    "Healthy Cassava": "https://firebasestorage.googleapis.com/v0/b/ai-agri-649c0.firebasestorage.app/o/Casaava%20well%20kayn.mp3?alt=media&token=02df816c-c472-4f16-bd3b-e013a0ec0d80",
    "Cocoa Black Pod": "https://yourfirebaseurl.com/krio_cocoa_blackpod.mp3",
    "Healthy Cocoa": "https://yourfirebaseurl.com/krio_healthy_cocoa.mp3",
    "Rice Blast": "https://yourfirebaseurl.com/krio_rice_blast.mp3",
    "Healthy Rice": "https://yourfirebaseurl.com/krio_healthy_rice.mp3",
    "Oil Palm Anthracnose": "https://yourfirebaseurl.com/krio_oilpalm_anthracnose.mp3",
    "Healthy Oil Palm": "https://yourfirebaseurl.com/krio_healthy_oilpalm.mp3",
    "Onion Purple Blotch": "https://yourfirebaseurl.com/krio_onion_purpleblotch.mp3",
    "Healthy Onion": "https://yourfirebaseurl.com/krio_healthy_onion.mp3"
}

# Prediction function
def predict_disease(image_url):
    try:
        response = requests.get(
            image_url,
            auth=HTTPBasicAuth(TWILIO_SID, TWILIO_AUTH_TOKEN),
            stream=True
        )
        content_type = response.headers.get('Content-Type', '')
        if 'image' not in content_type:
            print("Not an image.")
            return "Unknown"

        img = Image.open(BytesIO(response.content)).convert('RGB')
        input_tensor = transform(img).unsqueeze(0)
        with torch.no_grad():
            output = model(input_tensor)
            _, predicted = torch.max(output, 1)
        return CLASS_NAMES[predicted.item()]
    except Exception as e:
        print(f"Prediction error: {e}")
        return "Unknown"

@app.route("/webhook", methods=["POST"])
def whatsapp_webhook():
    num_media = int(request.values.get("NumMedia", 0))
    phone = request.values.get("From", "")
    latitude = request.values.get("Latitude", "N/A")
    longitude = request.values.get("Longitude", "N/A")
    location = f"{latitude}, {longitude}" if latitude != "N/A" else "Unknown"

    resp = MessagingResponse()
    msg = resp.message()

    if num_media > 0:
        image_url = request.values.get("MediaUrl0")
        diagnosis = predict_disease(image_url)

        # Save report
        c.execute("INSERT INTO reports (phone, image_url, disease, location) VALUES (?, ?, ?, ?)",
                  (phone, image_url, diagnosis, location))
        conn.commit()

        msg.body(f"Disease Detected: {diagnosis}\nAdvice (Krio): Listen to voice note.")
        audio_url = VOICE_RESPONSES.get(diagnosis)
        if audio_url:
            msg.media(audio_url)
    else:
        msg.body("Send a photo of your crop problem. We go help you check am.")

    return str(resp)

# 👇 This part is CRITICAL for Render.com
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
