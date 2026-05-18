import os
import asyncio
import logging
import base64
import json
import re
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import httpx

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RealOrderInterceptor")

app = FastAPI()

# Global memory table for UI logs
upi_logs_database = []

# Core Credentials Configuration
USERNAME = "5deposit"
PASSWORD = "5Dp@0000"

# Render Environment Variables
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
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
    logger.info("🚀 Executing Real Order Token Inspection Routine...")
    time_str = get_india_time().strftime("%Y-%m-%d %I:%M:%S %p")
    
    async with httpx.AsyncClient(headers=BASE_HEADERS, follow_redirects=True, timeout=25.0) as client:
        try:
            # PHASE 1: DIRECT LOGIN HANDSHAKE
            logger.info("🔑 Phase 1: Authentication...")
            login_url = "https://phantom777.now/api/front_open/login"
            login_payload = {"username": USERNAME, "password": PASSWORD, "passwordVisible": False, "recaptcha": "", "visitorId": "d5e743678fd43c2899b04c87af5c321ca7eedea63a9ae32a025d9e69b092f968"}
            await client.post(login_url, json=get_crypto_emulated_payload(login_payload))

            # PHASE 2: CONFIGURATION GATEWAY EXTRACTION
            logger.info("📡 Phase 2: Fetching payment list mapping...")
            list_url = "https://phantom777.now/api/front/supago/paymentlist"
            await client.post(list_url, json=get_crypto_emulated_payload({"amt": 500}))
            
            # PHASE 3: FETCHING CHECKOUT REDIRECTION LINK
            logger.info("🔗 Phase 3: Resolving dynamic payment type token url...")
            type_url = "https://phantom777.now/api/front/supago/paymenttype"
            
            # 2dd446ed waala unique ID fallback default target setup
            type_payload = {"amt": 500, "id": "2dd446ed"} 
            type_res = await client.post(type_url, json=get_crypto_emulated_payload(type_payload))
            
            # URL trace window logic mimicking Tampermonkey response behavior
            checkout_url = ""
            try:
                type_json = type_res.json()
                if type_json and type_json.get("success") and type_json.get("data", {}).get("url"):
                    checkout_url = type_json["data"]["url"]
            except Exception:
                pass
            
            # Fallback checkout URL generator string format block if JSON parsing settles empty
            if not checkout_url:
                checkout_url = "https://paybitra-payment-site-prod-20.vercel.app/payment/checkout/select-payment?order=12600984311024"

            clean_url = checkout_url.replace("&amp;", "&")
            logger.info(f"🎯 Checkout URL Resolved: {clean_url}")

            # Extracting the ACTUAL REAL Order ID from the verified checkout link parameters
            real_order_id = "12600984311024" # Safe global placeholder row
            try:
                parsed_url = urlparse(clean_url)
                query_params = parse_qs(parsed_url.query)
                if query_params.get('order'):
                    real_order_id = query_params.get('order')[0]
            except Exception:
                pass

            logger.info(f"🎯 Extracted Real Order ID from link: {real_order_id}")

            # PHASE 4: EXECUTE TERMINAL GATEWAY ASSIGN-BANK DISPATCH
            target_paybitra_endpoint = f"https://api.paybitra.com/v1/payIn/assign-bank/{real_order_id}"
            
            paybitra_payload = {"amount": 500, "type": "upi"}
            paybitra_headers = {
                "accept": "application/json, text/plain, */*", 
                "content-type": "application/json", 
                "referer": "https://paybitra-payment-site-prod-20.vercel.app/"
            }
            
            final_gateway_res = await client.post(target_paybitra_endpoint, json=paybitra_payload, headers=paybitra_headers)
            raw_response_text = final_gateway_res.text
            
            logger.info(f"📡 Real Response Received from Paybitra: {raw_response_text}")

            # Safe verification check just to display inside the local web dashboard log rows
            captured_upi_id = None
            try:
                gateway_json = json.loads(raw_response_text)
                if gateway_json and "data" in gateway_json and "bank" in gateway_json["data"]:
                    captured_upi_id = gateway_json["data"]["bank"].get("upi_id")
            except Exception:
                pass

            display_log_val = captured_upi_id if captured_upi_id else "RAW_LOGGED"
            upi_logs_database.insert(0, {"timestamp": time_str, "upi": display_log_val, "status": "SUCCESS"})

            # Forwarding full transparent API data block back to Telegram chat channel
            telegram_msg = (
                f"📡 *PAYBITRA REAL RESPONSE BLOCK*\n\n"
                f"🕒 *Time (IST):* {time_str}\n"
                f"🎯 *Used Real Order ID:* `{real_order_id}`\n"
                f"⚙️ *Status Code:* `{final_gateway_res.status_code}`\n\n"
                f"📋 *RAW JSON DATA:* \n```json\n{raw_response_text}\n```\n"
                f"⏱️ *Interval:* 8 Minutes Autonomous Loop"
            )
            await send_telegram_alert(telegram_msg)

        except Exception as e:
            logger.error(f"💥 Runtime Exception: {str(e)}")
            upi_logs_database.insert(0, {"timestamp": time_str, "upi": "ERROR", "status": "FAILED"})
            await send_telegram_alert(f"⚠️ *UPI MONITOR ALERT: PROCESS CRASH*\n\n🕒 *Time (IST):* {time_str}\n🔴 *Error Trace:* `{str(e)}` ")

async def start_autonomous_scheduler():
    """Bypass Sleep Engine: Runs infinitely by executing system self-pings every 8 minutes"""
    logger.info("⏳ Autonomous Self-Wakeup Clock Initialized.")
    await asyncio.sleep(10) # Initial startup buffer
    
    while True:
        try:
            await fetch_upi_job()
            if RENDER_EXTERNAL_URL:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    self_hit_res = await client.get(RENDER_EXTERNAL_URL)
                    logger.info(f"⚡ Anti-Sleep Self-Ping Dispatched. Status: {self_hit_res.status_code}")
        except Exception as e:
            logger.error(f"Scheduler Loop Context Error: {e}")
        
        await asyncio.sleep(8 * 60) # Exactly 8 Minutes Loop Execution Rotation

@app.on_event("startup")
async def startup_event():
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
        <title>🤖 Real Order ID Interceptor Monitor</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: 'Courier New', monospace; background-color: #121212; color: #ffffff; padding: 20px; }
            .container { max-width: 800px; margin: 0 auto; background: #1e1e1e; padding: 20px; border-radius: 8px; border: 1px solid #34495e; }
            h2 { border-bottom: 2px solid #333; padding-bottom: 8px; color: #00ffff; }
            .badge { background: #2980b9; color: #fff; padding: 3px 8px; border-radius: 20px; font-size: 11px; }
            .log-box { background: #000; padding: 15px; height: 250px; overflow-y: auto; border-radius: 5px; margin-top: 15px; font-size: 13px; }
            .log-entry { padding: 6px; border-bottom: 1px solid #222; display: flex; justify-content: space-between; }
            .timestamp { color: #ff9f43; }
            .upi-value { color: #1dd1a1; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>🤖 Real Order ID Interceptor Dashboard</h2>
            <p style="font-size:12px; color:#aaa;">Status: <span class="badge">Anti-Sleep Core Active (8 Min)</span></p>
            <p>Every response from the bank gateway is being intercepted and streamed raw directly to your Telegram chat channel continuously.</p>
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
                        area.innerHTML += `<div class="log-entry"><span class="timestamp">[${log.timestamp}]</span><span class="upi-value">${log.upi}</span></div>`;
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
