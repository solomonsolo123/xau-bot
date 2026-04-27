import os
import requests
import yfinance as yf
import pandas as pd

# ─── CONFIGURATION ──────────────────────────────────────────
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def calculate_rsi(prices, period=14):
    """Calculate the Relative Strength Index."""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1, + rs))

def get_pro_analysis():
    ticker = yf.Ticker("GC=F")
    # Fetch more data to calculate RSI accurately
    df = ticker.history(period="1mo", interval="1d")
    
    if len(df) < 2: return None

    # Latest Data
    last_row = df.iloc[-1]
    prev_row = df.iloc[-2]
    
    h, l, c = last_row['High'], last_row['Low'], last_row['Close']
    
    # 1. Pivot Point Levels (For your Entry/Exit)
    pivot = (h + l + c) / 3
    r1 = (2 * pivot) - l
    s1 = (2 * pivot) - h
    
    # 2. RSI Calculation
    df['RSI'] = calculate_rsi(df['Close'])
    current_rsi = df['RSI'].iloc[-1]

    # 3. Logic
    signal = "BULLISH 🟢" if c > pivot else "BEARISH 🔴"
    rsi_status = "Overbought ⚠️" if current_rsi > 70 else "Oversold 💎" if current_rsi < 30 else "Neutral ⚖️"

    msg = (
        f"🏆 <b>XAUUSD PRO ANALYSIS</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"DIRECTION: <b>{signal}</b>\n"
        f"RSI (14): <code>{current_rsi:.1f}</code> ({rsi_status})\n\n"
        f"🎯 <b>KEY LEVELS:</b>\n"
        f"🚀 Target (R1): <code>${r1:,.2f}</code>\n"
        f"📍 Pivot: <code>${pivot:,.2f}</code>\n"
        f"🛡️ Support (S1): <code>${s1:,.2f}</code>\n\n"
        f"💰 Current: <b>${c:,.2f}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"<i>Bot running on 5m interval. No need to check charts!</i>"
    )
    return msg

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"})

if __name__ == "__main__":
    message = get_pro_analysis()
    if message:
        send_telegram(message)
        print("✅ Pro Analysis Sent.")