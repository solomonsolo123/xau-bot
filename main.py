import os
import requests
import yfinance as yf

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def fetch_xauusd():
    """Fetch last 2 days of XAUUSD data."""
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
    """Analyze market and return signal."""
    if len(data) < 2:
        return "NEUTRAL", 0, [], {}
    
    latest = data[-1]
    prev = data[-2]
    
    o, h, l, c = latest["Open"], latest["High"], latest["Low"], latest["Close"]
    pc = prev["Close"]
    
    change = c - pc
    change_pct = (change / pc) * 100
    daily_range = h - l
    pos = ((c - l) / daily_range * 100) if daily_range > 0 else 50
    
    bull, bear = 0, 0
    reasons = []
    
    # Candle direction
    if c > o:
        bull += 2
        reasons.append(f"✅ Close (${c:,.2f}) > Open (${o:,.2f})")
    else:
        bear += 2
        reasons.append(f"❌ Close (${c:,.2f}) < Open (${o:,.2f})")
    
    # vs yesterday
    if c > pc:
        bull += 2
        reasons.append(f"✅ Up {change_pct:+.2f}% from yesterday")
    else:
        bear += 2
        reasons.append(f"❌ Down {change_pct:+.2f}% from yesterday")
    
    # Position in range
    if pos > 70:
        bull += 1
        reasons.append(f"✅ Near daily high ({pos:.0f}%)")
    elif pos < 30:
        bear += 1
        reasons.append(f"❌ Near daily low ({pos:.0f}%)")
    
    # Breakout
    if c > prev["High"]:
        bull += 2
        reasons.append("✅ Above yesterday's high")
    elif c < prev["Low"]:
        bear += 2
        reasons.append("❌ Below yesterday's low")
    
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
    """Send to Telegram."""
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("❌ Missing secrets!")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    
    try:
        r = requests.post(url, data=payload, timeout=30)
        r.raise_for_status()
        print("✅ Sent to Telegram!")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def build_msg(signal, conf, reasons, m):
    """Format Telegram message."""
    emo = {"BULLISH": "🟢", "BEARISH": "🔴", "NEUTRAL": "⚪"}[signal]
    
    msg = f"""{emo} <b>XAUUSD SIGNAL</b> {emo}

📅 <b>{m['date']}</b>
📊 <b>Signal:</b> <code>{signal}</code>
💪 <b>Confidence:</b> {conf:.0f}%

📈 <b>O:</b> ${m['open']:,.2f}  <b>H:</b> ${m['high']:,.2f}
📉 <b>L:</b> ${m['low']:,.2f}  <b>C:</b> ${m['close']:,.2f}

📉 Change: ${m['change']:+.2f} ({m['change_pct']:+.2f}%)
📏 Range: ${m['range']:,.2f}

🔍 Analysis:"""
    for r in reasons:
        msg += f"\n   {r}"
    msg += f"\n\n📊 Score: Bullish {m['bull']} vs Bearish {m['bear']}"
    msg += "\n\n<i>⚠️ Not financial advice.</i>"
    return msg

# ─── MAIN ─────────────────────────
if __name__ == "__main__":
    print("🚀 Fetching XAUUSD...")
    data = fetch_xauusd()
    
    if not data or len(data) < 2:
        print("❌ No data")
        exit(1)
    
    print("🔍 Analyzing...")
    signal, conf, reasons, metrics = analyze(data)
    
    print(f"🎯 {signal} ({conf:.0f}%)")
    
    msg = build_msg(signal, conf, reasons, metrics)
    send_message(msg)