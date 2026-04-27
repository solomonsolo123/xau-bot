import os
import requests
import yfinance as yf
import pandas as pd

# ─── CONFIGURATION ──────────────────────────────────────────
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def calculate_rsi(prices, period=14):
    """Standard RSI calculation for trend strength."""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0))
    loss = (-delta.where(delta < 0, 0))

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def get_pro_analysis():
    """Fetches Gold data and creates an accessible report."""
    try:
        # GC=F is Gold Futures
        ticker = yf.Ticker("GC=F")
        df = ticker.history(period="1mo", interval="1d")
        
        if len(df) < 15:
            return "⚠️ ERROR: NOT ENOUGH DATA SAMPLES FOUND."

        # Latest Price Data
        last_row = df.iloc[-1]
        h, l, c = last_row['High'], last_row['Low'], last_row['Close']
        
        # Pivot Point Math
        pivot = (h + l + c) / 3
        r1 = (2 * pivot) - l
        s1 = (2 * pivot) - h
        
        # RSI Logic
        df['RSI'] = calculate_rsi(df['Close'])
        current_rsi = df['RSI'].iloc[-1]

        # Accessibility: Clear Directional Symbols
        if c > pivot:
            direction_label = "UP / BULLISH"
            direction_emoji = "🟩🟩🟩 POSITIVE 🟩🟩🟩"
        else:
            direction_label = "DOWN / BEARISH"
            direction_emoji = "🟥🟥🟥 NEGATIVE 🟥🟥🟥"
        
        # RSI Strength Description
        if current_rsi > 70:
            rsi_desc = "VERY HIGH (OVERBOUGHT)"
        elif current_rsi < 30:
            rsi_desc = "VERY LOW (OVERSOLD)"
        else:
            rsi_desc = "NORMAL / NEUTRAL"

        # Building a screen-reader friendly message
        msg = (
            f"<b>GOLD (XAUUSD) REPORT</b>\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"<b>TREND DIRECTION:</b>\n"
            f"{direction_emoji}\n"
            f"<b>{direction_label}</b>\n\n"
            f"• <b>CURRENT PRICE:</b> ${c:,.2f}\n"
            f"• <b>RSI STRENGTH:</b> {current_rsi:.1f}\n"
            f"• <b>MARKET CONDITION:</b> {rsi_desc}\n\n"
            f"<b>KEY PRICE LEVELS:</b>\n"
            f"• 📈 <b>TARGET TOP (R1):</b> ${r1:,.2f}\n"
            f"• 📍 <b>CENTER (PIVOT):</b> ${pivot:,.2f}\n"
            f"• 📉 <b>BOTTOM (S1):</b> ${s1:,.2f}\n\n"
            f"━━━━━━━━━━━━━━━\n"
            f"<i>End of Analysis</i>"
        )
        return msg

    except Exception as e:
        return f"❌ SCRIPT ERROR: {str(e)}"

def send_telegram(text):
    """Sends the formatted text to Telegram."""
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("❌ ERROR: TELEGRAM_TOKEN OR CHAT_ID NOT FOUND IN SECRETS.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID, 
        "text": text, 
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, data=payload, timeout=30)
        response.raise_for_status()
        print("✅ SUCCESS: MESSAGE SENT TO TELEGRAM.")
    except Exception as e:
        print(f"❌ TELEGRAM ERROR: {e}")

if __name__ == "__main__":
    print("🚀 STARTING ACCESSIBLE GOLD BOT...")
    analysis_message = get_pro_analysis()
    send_telegram(analysis_message)