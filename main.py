import os
import requests
import yfinance as yf

# ─── CONFIGURATION ──────────────────────────────────────────
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def fetch_xauusd():
    """Fetch last 5 days of XAUUSD (Gold Futures) data."""
    # GC=F is the symbol for Gold Continuous Contract on Yahoo Finance
    ticker = yf.Ticker("GC=F")
    hist = ticker.history(period="5d", interval="1d")
    
    data = []
    for date, row in hist.iterrows():
        data.append({
            "Date": str(date),
            "Open": float(row["Open"]),
            "High": float(row["High"]),
            "Low": float(row["Low"]),
            "Close": float(row["Close"]),
        })
    return data

def analyze(data):
    """Analyze market and return signal with HTML-safe strings."""
    if len(data) < 2:
        return "NEUTRAL", 0, [], {}
    
    latest = data[-1]
    prev = data[-2]
    
    o, h, l, c = latest["Open"], latest["High"], latest["Low"], latest["Close"]
    pc = prev["Close"]
    
    change = c - pc
    change_pct = (change / pc) * 100
    daily_range = h - l
    # Position in the daily range (0% = at low, 100% = at high)
    pos = ((c - l) / daily_range * 100) if daily_range > 0 else 50
    
    bull, bear = 0, 0
    reasons = []
    
    # 1. Candle direction (Today's Open vs Today's Close)
    if c > o:
        bull += 2
        reasons.append(f"✅ Close (${c:,.2f}) above Open (${o:,.2f})")
    else:
        bear += 2
        reasons.append(f"❌ Close (${c:,.2f}) below Open (${o:,.2f})")
    
    # 2. Performance vs yesterday
    if c > pc:
        bull += 2
        reasons.append(f"✅ Up {change_pct:+.2f}% from yesterday")
    else:
        bear += 2
        reasons.append(f"❌ Down {change_pct:+.2f}% from yesterday")
    
    # 3. Position in daily range
    if pos > 70:
        bull += 1
        reasons.append(f"✅ Strength: Near daily high ({pos:.0f}%)")
    elif pos < 30:
        bear += 1
        reasons.append(f"❌ Weakness: Near daily low ({pos:.0f}%)")
    
    # 4. Breakout analysis (vs Yesterday's High/Low)
    if c > prev["High"]:
        bull += 2
        reasons.append("✅ Breakout: Above yesterday's high")
    elif c < prev["Low"]:
        bear += 2
        reasons.append("❌ Breakdown: Below yesterday's low")
    
    total = bull + bear
    if bull > bear:
        signal, conf = "BULLISH", (bull/total)*100
    elif bear > bull:
        signal, conf = "BEARISH", (bear/total)*100
    else:
        signal, conf = "NEUTRAL", 50
    
    metrics = {
        "date": latest["Date"][:10], "open": o, "high": h,
        "low": l, "close": c, "change": change, "change_pct": change_pct,
        "range": daily_range, "bull": bull, "bear": bear
    }
    return signal, conf, reasons, metrics

def send_message(text):
    """Send to Telegram with error handling."""
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("❌ Missing Secrets (TELEGRAM_TOKEN or CHAT_ID)!")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID, 
        "text": text, 
        "parse_mode": "HTML"
    }
    
    try:
        r = requests.post(url, data=payload, timeout=30)
        r.raise_for_status()
        print("✅ Sent to Telegram!")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response Body: {e.response.text}")
        return False

def build_msg(signal, conf, reasons, m):
    """Format Telegram message using HTML-safe characters."""
    emo = {"BULLISH": "🟢", "BEARISH": "🔴", "NEUTRAL": "⚪"}[signal]
    
    msg = (
        f"{emo} <b>XAUUSD SIGNAL</b> {emo}\n\n"
        f"📅 <b>Date:</b> {m['date']}\n"
        f"📊 <b>Signal:</b> <code>{signal}</code>\n"
        f"💪 <b>Confidence:</b> {conf:.0f}%\n\n"
        f"📈 <b>O:</b> ${m['open']:,.2f} | <b>H:</b> ${m['high']:,.2f}\n"
        f"📉 <b>L:</b> ${m['low']:,.2f} | <b>C:</b> ${m['close']:,.2f}\n\n"
        f"💹 Change: {m['change_pct']:+.2f}%\n"
        f"📏 Daily Range: ${m['range']:,.2f}\n\n"
        f"🔍 <b>Analysis:</b>"
    )
    
    for r in reasons:
        # We replace < and > to prevent Telegram 400 Bad Request errors
        clean_reason = r.replace("<", "&lt;").replace(">", "&gt;")
        msg += f"\n  {clean_reason}"
        
    msg += f"\n\n📊 <b>Score:</b> Bull {m['bull']} - Bear {m['bear']}"
    msg += "\n\n<i>⚠️ Disclaimer: Not financial advice.</i>"
    return msg

# ─── MAIN EXECUTION ───────────────────────────────────────
if __name__ == "__main__":
    print("🚀 Bot starting...")
    print("📈 Fetching XAUUSD Data...")
    
    try:
        data = fetch_xauusd()
        
        if not data or len(data) < 2:
            print("❌ Error: Not enough data points fetched.")
            exit(1)
        
        print("🔍 Running Analysis...")
        signal, conf, reasons, metrics = analyze(data)
        
        print(f"🎯 Prediction: {signal} ({conf:.0f}%)")
        
        # Build the final formatted string
        telegram_text = build_msg(signal, conf, reasons, metrics)
        
        # Send it!
        send_message(telegram_text)
        
    except Exception as e:
        print(f"❌ Fatal Script Error: {e}")