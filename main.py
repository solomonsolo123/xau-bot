import os
import requests

token = os.environ.get("TELEGRAM_TOKEN")
chat_id = os.environ.get("CHAT_ID") # You'll need to add this to GitHub Secrets

if not token or not chat_id:
    print("❌ Error: TELEGRAM_TOKEN or CHAT_ID is missing!")
else:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": "🚀 Hello from GitHub Actions! Your trading bot is online."
    }

    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        print("✅ Message sent to Telegram!")
    except Exception as e:
        print(f"❌ Failed to send: {e}")