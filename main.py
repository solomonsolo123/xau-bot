import os
import requests

token = os.getenv("TELEGRAM_TOKEN")
chat = os.getenv("CHAT_ID")

requests.post(
    f"https://api.telegram.org/bot{token}/sendMessage",
    data={
        "chat_id": chat,
        "text": "GitHub bot is alive 🚀"
    }
)

print("Message sent")