import os
import requests
import yfinance as yf
import pandas as pd

# ─── SETTINGS ───────────────────────────────────────────────
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# These settings control when your phone will buzz
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

def calculate_rsi(prices, period=14):
    """Standard RSI calculation."""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0))
    loss = (-delta.where(delta < 0, 0))
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def get_pro_analysis():
    """Analyze Gold and return message ONLY if RSI is at extremes."""
    try:
        # Fetching Gold Futures (GC=F)
        ticker = yf.Ticker("GC=F")
        df = ticker.history(period="1mo", interval="1d")
        
        if len(df) < 15:
            return None, "Warming up data..."

        last_row = df.iloc[-1]
        h, l, c = last_row['High'], last_row['Low'], last_row['Close']
        
        # Mathematical Calculations
        pivot = (h + l + c) / 3
        r1 = (2 * pivot) - l
        s1 = (2 * pivot) - h
        df['RSI'] = calculate_rsi(df['Close'])
        current_rsi = df['RSI'].iloc[-1]

        # CONDITIONAL CHECK: Only proceed if RSI is extreme
        is_extreme = current_rsi >= RSI_OVERBOUGHT or current_rsi <= RSI_OVERSOLD
        
        if not is_extreme:
            # This returns nothing to the main function, so no message is sent
            return None, f"Market is calm (RSI: {current_rsi:.1f})"

        # Accessibility: High-Contrast Directional Blocks
        direction_emoji = "🟩🟩🟩" if c > pivot else "🟥🟥🟥"
        rsi_label = "⚠️ OVERBOUGHT (SELL ZONE)" if current_rsi >= 70 else "💎 OVERSOLD (BUY ZONE)"

        # Building the screen-reader friendly message
        msg = (
            f"🚨 <b>GOLD RSI ALERT</b> 🚨\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"<b>{rsi_label}</b>\n\n"
            f"• <b>CURRENT RSI:</b> {current_rsi:.1f}\n"
            f"• <b>CURRENT PRICE:</b> ${c:,.2f}\n\n"
            f"<b>MARKET TREND:</b>\n"
            f"{direction_emoji} {'BULLISH' if c > pivot else 'BEARISH'}\n\n"
            f"<b>LEVELS TO WATCH:</b>\n"
            f"• 📈 <b>TOP (R1):</b> ${r1:,.2f}\n"
            f"• 📉 <b>BOTTOM (S1):</b> ${s1:,.2f}\n\n"
            f"━━━━━━━━━━━━━━━\n"
            f"<i>Check your broker now.</i>"
        )
        return msg, "Extreme detected"

    except Exception as e:
        return f"❌ SCRIPT ERROR: {str(e)}", "Error"

def send_telegram(text):
    """Sends the HTML message to your phone."""
    if not TELEGRAM_TOKEN or not CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    requests.post(url, data=payload, timeout=30)

if __name__ == "__main__":
    print("🚀 Scanning Gold Market...")
    message, status = get_pro_analysis()
    
    if message:
        send_telegram(message)
        print(f"✅ ALERT SENT: {status}")
    else:
        print(f"😴 SILENT MODE: {status}")