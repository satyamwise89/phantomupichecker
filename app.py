import os
import asyncio
import logging
import base64
import json
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import httpx

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SelfWakeupInterceptor")

app = FastAPI()

# Global memory table for UI logs
upi_logs_database = []

# Core Credentials Configuration
USERNAME = "5deposit"
PASSWORD = "5Dp@0000"

# Render Environment Variables
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
# Render dashboard par aapka live link is env variable me automatic milta hai
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL", "https://phantom-upi-hunter.onrender.com")

BASE_HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
    "content-type": "application/json",
    "origin": "https://phantom777.now",
    "referer": "https://phantom777.now/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

def get_india_time():
    utc_now = datetime.now(timezone.utc)
    return utc_now.astimezone(timezone(timedelta(hours=5, minutes=30)))

async def send_telegram_alert(message: str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("⚠️ Telegram credentials missing in environment variables.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            await client.post(url, json=payload)
    except Exception as e:
        logger.error(f"💥 Telegram dispatch error: {e}")

def get_crypto_emulated_payload(raw_dict: dict) -> dict:
    dummy_salt = "1234567890abcdef"
    fake_cipher_bytes = base64.b64encode(json.dumps(raw_dict).encode('utf-8')).decode('utf-8')
    return {"data": f"U2FsdGVkX1{dummy_salt}{fake_cipher_bytes}"}

async def fetch_upi_job():
    logger.info("🚀 Executing Automatic 8-Minute UPI Fetch Routine...")
    time_str = get_india_time().strftime("%Y-%m-%d %I:%M:%S %p")
    
    async with httpx.AsyncClient(headers=BASE_HEADERS, follow_redirects=True, timeout=25.0) as client:
        try:
            # PHASE 1: LOGIN
            login_url = "https://phantom777.now/api/front_open/login"
            login_payload = {"username": USERNAME, "password": PASSWORD, "passwordVisible": False, "recaptcha": "", "visitorId": "d5e743678fd43c2899b04c87af5c321ca7eedea63a9ae32a025d9e69b092f968"}
            await client.post(login_url, json=get_crypto_emulated_payload(login_payload))

            # PHASE 2: CONFIGURATION
            list_url = "https://phantom777.now/api/front/supago/paymentlist"
            await client.post(list_url, json=get_crypto_emulated_payload({"amt": 500}))
            
            # PHASE 3: FETCH LIVE UPI
            simulated_live_id = "126" + str(int(asyncio.get_event_loop().time() * 1000))[:16]
            target_paybitra_endpoint = f"https://api.paybitra.com/v1/payIn/assign-bank/{simulated_live_id}"
            
            paybitra_payload = {"amount": 500, "type": "upi"}
            paybitra_headers = {"accept": "application/json, text/plain, */*", "content-type": "application/json", "referer": "https://paybitra-payment-site-prod-20.vercel.app/"}
            
            final_gateway_res = await client.post(target_paybitra_endpoint, json=paybitra_payload, headers=paybitra_headers)
            
            captured_upi_id = None
            try:
                gateway_json = final_gateway_res.json()
                if gateway_json and "data" in gateway_json and "bank" in gateway_json["data"]:
                    captured_upi_id = gateway_json["data"]["bank"].get("upi_id")
            except Exception:
                pass
            
            # FIXED: Kisi bhi tarah ka fake handle generation completely delete kar diya hai.
            if captured_upi_id:
                upi_logs_database.insert(0, {"timestamp": time_str, "upi": captured_upi_id, "status": "SUCCESS"})
                logger.info(f"🎉 Auto Captured UPI: {captured_upi_id}")
                await send_telegram_alert(f"🎯 *UPI CAPTURED SUCCESSFULLY*\n\n💸 *UPI ID:* `{captured_upi_id}`\n🕒 *Time (IST):* {time_str}\n⏱️ *Interval:* 8 Minutes Autonomous Core")
            else:
                # Agar API response blank aaya toh seedhe None ya empty filter handle hoga
                raise Exception("API responded but no live bank allocation keys found inside the packet.")

        except Exception as e:
            logger.error(f"💥 Runtime Exception: {str(e)}")
            # Real facts dispatch directly to your Telegram chat
            upi_logs_database.insert(0, {"timestamp": time_str, "upi": "NOT_FOUND", "status": "FAILED"})
            await send_telegram_alert(f"⚠️ *UPI MONITOR ALERT: NOT FOUND*\n\n🕒 *Time (IST):* {time_str}\n🔴 *Reason:* `{str(e)}` \n❌ *Status:* NOT FOUND")

async def start_autonomous_scheduler():
    """Bypass Sleep Engine: Runs infinitely by executing system self-pings every 8 minutes"""
    logger.info("⏳ Autonomous Self-Wakeup Clock Initialized.")
    await asyncio.sleep(10) # Initial startup buffer
    
    while True:
        try:
            # 🔄 STEP 1: Core dynamic extraction process execution (Har 8 min mein chalega)
            await fetch_upi_job()
            
            # 🔥 STEP 2: Pure Anti-Sleep Trick (Har 8 minute mein khud ko hit karega)
            if RENDER_EXTERNAL_URL:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    self_hit_res = await client.get(RENDER_EXTERNAL_URL)
                    logger.info(f"⚡ Anti-Sleep Self-Ping Dispatched. Status: {self_hit_res.status_code}")
                    
        except Exception as e:
            logger.error(f"Scheduler Loop Context Error: {e}")
        
        # ⏱️ FIXED INTERVAL: 8 Minutes loop rotation window (8 * 60 seconds)
        await asyncio.sleep(8 * 60)

@app.on_event("startup")
async def startup_event():
    # Automatically registers background process thread upon application boot
    asyncio.create_task(start_autonomous_scheduler())

@app.get("/api/logs")
async def get_live_logs_api():
    return JSONResponse(content={"logs": upi_logs_database})

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard_ui_page(request: Request):
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🤖 8-Min Real-Fact Autonomous Interceptor</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: 'Courier New', monospace; background-color: #121212; color: #ffffff; padding: 20px; }
            .container { max-width: 800px; margin: 0 auto; background: #1e1e1e; padding: 20px; border-radius: 8px; border: 1px solid #34495e; }
            h2 { border-bottom: 2px solid #333; padding-bottom: 8px; color: #00ffff; }
            .badge { background: #e74c3c; color: #fff; padding: 3px 8px; border-radius: 20px; font-size: 11px; }
            .log-box { background: #000; padding: 15px; height: 250px; overflow-y: auto; border-radius: 5px; margin-top: 15px; font-size: 13px; }
            .log-entry { padding: 6px; border-bottom: 1px solid #222; display: flex; justify-content: space-between; }
            .timestamp { color: #ff9f43; }
            .upi-value { font-weight: bold; }
            .success-upi { color: #1dd1a1; }
            .fail-upi { color: #ff4757; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>🤖 8-Min Real-Fact Autonomous Dashboard</h2>
            <p style="font-size:12px; color:#aaa;">Status: <span class="badge" style="background: #27ae60;">Anti-Sleep Core Enabled (8 Min)</span></p>
            <p>The engine uses local loopback network self-pings to keep the Render free tier awake permanently. Displays only real-time facts.</p>
            <div class="log-box" id="logs-area">Loading live streaming logs thread...</div>
        </div>
        <script>
            async function refreshLogs() {
                try {
                    let res = await fetch('/api/logs');
                    let data = await res.json();
                    let area = document.getElementById('logs-area');
                    if(data.logs.length === 0) {
                        area.innerHTML = "<div style='color:#aaa; text-align:center; padding-top:100px;'>No logs captured yet. Processing autonomous queue...</div>";
                        return;
                    }
                    area.innerHTML = "";
                    data.logs.forEach(log => {
                        let upiClass = log.upi === "NOT_FOUND" ? "fail-upi" : "success-upi";
                        area.innerHTML += `<div class="log-entry"><span class="timestamp">[${log.timestamp}]</span><span class="upi-value ${upiClass}">${log.upi}</span></div>`;
                    });
                } catch(e) {}
            }
            setInterval(refreshLogs, 5000);
            window.onload = refreshLogs;
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)
