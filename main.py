import os
import requests

# Use getenv to avoid crashing, but check if it's actually there
token = os.getenv("TELEGRAM_TOKEN")

if not token:
    print("❌ Error: TELEGRAM_TOKEN is not set in environment variables.")
else:
    # Telegram API URLs are case-sensitive; ensure the 'bot' prefix is lowercase
    url = f"https://api.telegram.org/bot{token}/getMe"
    
    try:
        r = requests.get(url)
        r.raise_for_status() # This will catch 404s or 401s specifically
        print("✅ Success!")
        print(r.json()) # Printing as JSON is easier to read than raw text
    except requests.exceptions.HTTPError as err:
        print(f"❌ API Error: {err}")
        print(f"Response Body: {r.text}")