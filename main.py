import os
import requests

token = os.getenv("TELEGRAM_TOKEN")
chat = os.getenv("CHAT_ID")

r = requests.post(
    f"https://api.telegram.org/bot{token}/sendMessage",
    data={
        "chat_id": chat,
        "text": "GitHub bot test"
    }
)

print(r.status_code)
print(r.text)