import os,requests

token=os.getenv("TELEGRAM_TOKEN")

r=requests.get(
f"https://api.telegram.org/bot{token}/getMe"
)

print(r.text)
