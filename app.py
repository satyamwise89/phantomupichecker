import os
import asyncio
import logging
import base64
import json
import re
import hashlib
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import httpx
from playwright.async_api import async_playwright

# Cryptography Dependencies Configuration
try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad, unpad
    has_crypto = True
except ImportError:
    has_crypto = False

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HybridInterceptor")

app = FastAPI()

# Global memory table for UI logs
upi_logs_database = []

# Core Credentials Configuration
USERNAME = "5deposit"
PASSWORD = "5Dp@0000"
SECRET_KEY = "z8uEAb-aN5QE6xY35P736SKwxi4cd9dYPjhw"

# Render Environment Variables
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL", "https://phantom-upi-hunter.onrender.com")

BASE_HEADERS = {
    "accept": "*/*",
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
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            await client.post(url, json=payload)
    except Exception as e:
        logger.error(f"💥 Telegram dispatch error: {e}")

def get_cryptoJS_aes_encrypt(raw_dict: dict) -> dict:
    data_bytes = json.dumps(raw_dict).encode('utf-8')
    if not has_crypto:
        dummy_salt = "1234567890abcdef"
        fake_cipher = base64.b64encode(data_bytes).decode('utf-8')
        return {"data": f"U2FsdGVkX1{dummy_salt}{fake_cipher}"}
    try:
        salt = os.urandom(8)
        password_bytes = SECRET_KEY.encode('utf-8')
        concat_bytes = b""
        last_block = b""
        while len(concat_bytes) < 48:
            hasher = hashlib.md5()
            hasher.update(last_block + password_bytes + salt)
            last_block = hasher.digest()
            concat_bytes += last_block
        derived_key = concat_bytes[:32]
        derived_iv = concat_bytes[32:48]
        cipher = AES.new(derived_key, AES.MODE_CBC, derived_iv)
        padded_data = pad(data_bytes, AES.block_size)
        encrypted_bytes = cipher.encrypt(padded_data)
        openssl_payload = b"Salted__" + salt + encrypted_bytes
        return {"data": base64.b64encode(openssl_payload).decode('utf-8')}
    except Exception:
        return {"data": base64.b64encode(data_bytes).decode('utf-8')}

def get_cryptoJS_aes_decrypt(encrypted_str: str) -> str:
    if not has_crypto or not encrypted_str:
        return ""
    try:
        encrypted_bytes = base64.b64decode(encrypted_str)
        if not encrypted_bytes.startswith(b"Salted__"): return ""
        salt = encrypted_bytes[8:16]
        ciphertext = encrypted_bytes[16:]
        password_bytes = SECRET_KEY.encode('utf-8')
        concat_bytes = b""
        last_block = b""
        while len(concat_bytes) < 48:
            hasher = hashlib.md5()
            hasher.update(last_block + password_bytes + salt)
            last_block = hasher.digest()
            concat_bytes += last_block
        derived_key = concat_bytes[:32]
        derived_iv = concat_bytes[32:48]
        cipher = AES.new(derived_key, AES.MODE_CBC, derived_iv)
        decrypted_padded = cipher.decrypt(ciphertext)
        return unpad(decrypted_padded, AES.block_size).decode('utf-8')
    except Exception:
        return ""

async def fetch_upi_job():
    logger.info("🚀 Launching Hybrid Cloud Tracking Sequence...")
    time_str = get_india_time().strftime("%Y-%m-%d %I:%M:%S %p")
    
    async with httpx.AsyncClient(headers=BASE_HEADERS, follow_redirects=True, timeout=30.0) as client:
        try:
            # PHASE 1: DIRECT LOGIN (Bypassing login page interface)
            login_url = "https://phantom777.now/api/front_open/login"
            login_payload = {"username": USERNAME, "password": PASSWORD, "passwordVisible": False, "recaptcha": "", "visitorId": "d5e743678fd43c2899b04c87af5c321ca7eedea63a9ae32a025d9e69b092f968"}
            await client.post(login_url, json=get_crypto_emulated_payload(login_payload) if not has_crypto else get_cryptoJS_aes_encrypt(login_payload))

            # PHASE 2: PAYMENT LIST GATEWAY SCAN
            list_url = "https://phantom777.now/api/front/supago/paymentlist"
            list_res = await client.post(list_url, json=get_crypto_emulated_payload({"amt": 500}) if not has_crypto else get_cryptoJS_aes_encrypt({"amt": 500}))
            
            dynamic_gateway_id = "2dd446ed"
            try:
                list_json = list_res.json()
                if list_json and "data" in list_json:
                    dec_str = get_cryptoJS_aes_decrypt(list_json.get("data", "")) if has_crypto else ""
                    if dec_str: dynamic_gateway_id = json.loads(dec_str)["data"]["t1"][0].get("pmuniqueid", "2dd446ed")
            except Exception: pass

            # PHASE 3: CHECKOUT URL RESOLUTION
            type_url = "https://phantom777.now/api/front/supago/paymenttype"
            type_res = await client.post(type_url, json=get_cryptoJS_aes_encrypt({"amt": 500, "id": dynamic_gateway_id}))
            
            checkout_url = ""
            try:
                type_json = type_res.json()
                if type_json and "data" in type_json:
                    dec_type = get_cryptoJS_aes_decrypt(type_json.get("data", ""))
                    if dec_type: checkout_url = json.loads(dec_type).get("url")
            except Exception: pass

            if not checkout_url:
                raise Exception("Phantom777 dynamic checkout link generation failed.")

            clean_url = checkout_url.replace("&amp;", "&")
            logger.info(f"🔗 Intermediate Link Resolved: {clean_url}")

            # 🔥 PHASE 4: PLAYWRIGHT CHROMIUM DEEP REDIRECT CAPTURE CORE
            logger.info("🤖 Spawning lightweight browser engine to capture final vercel url...")
            real_19_digit_id = None
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
                context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
                page = await context.new_page()
                
                # Navigate straight to the intermediate link 
                await page.goto(clean_url, timeout=30000, wait_until="commit")
                
                # Dynamic wait window loop (Bhai ye har 0.5 second me check karega ki link redirect hua ya nahi)
                for _ in range(16):
                    await asyncio.sleep(0.5)
                    current_browser_url = page.url
                    if "transaction" in current_browser_url and "order=" in current_browser_url:
                        logger.info(f"🎯 Matched Dynamic Browser Redirection Target: {current_browser_url}")
                        parsed_url = urlparse(current_browser_url)
                        query_params = parse_qs(parsed_url.query)
                        if query_params.get('order'):
                            real_19_digit_id = query_params.get('order')[0]
                            break
                await browser.close()

            if not real_19_digit_id:
                raise Exception("Browser automation session closed. Redirection threshold timed out without order extraction.")

            logger.info(f"🎉 Success! Extracted Real 19-Digit Order ID: {real_19_digit_id}")

            # PHASE 5: DIRECT TERMINAL API HANDSHAKE DISPATCH
            target_paybitra_endpoint = f"https://api.paybitra.com/v1/payIn/assign-bank/{real_19_digit_id}"
            paybitra_payload = {"amount": 500, "type": "upi"}
            paybitra_headers = {
                "accept": "*/*",
                "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
                "content-type": "application/json",
                "referer": "https://paybitra-payment-site-prod-20.vercel.app/",
                "sec-ch-ua": '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "cross-site",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            final_gateway_res = await client.post(target_paybitra_endpoint, json=paybitra_payload, headers=paybitra_headers)
            raw_response_text = final_gateway_res.text
            
            logger.info(f"📡 Real-Time Packet Return Stream: {raw_response_text}")

            captured_upi_id = None
            try:
                gateway_json = json.loads(raw_response_text)
                if gateway_json and "data" in gateway_json and "bank" in gateway_json["data"]:
                    captured_upi_id = gateway_json["data"]["bank"].get("upi_id")
            except Exception: pass

            display_log_val = captured_upi_id if captured_upi_id else "RAW_LOGGED"
            upi_logs_database.insert(0, {"timestamp": time_str, "upi": display_log_val, "status": "SUCCESS"})

            # Direct Telegram alert notification dispatch
            telegram_msg = (
                f"📡 *PAYBITRA SEAMLESS CLOUD BREAK*\n\n"
                f"🕒 *Time (IST):* {time_str}\n"
                f"🎯 *Extracted Order ID:* `{real_19_digit_id}`\n"
                f"⚙️ *Status Code:* `{final_gateway_res.status_code}`\n\n"
                f"📋 *RAW RESPONSE DUMP:* \n```json\n{raw_response_text}\n```\n"
                f"⏱️ *Interval:* 8 Minutes Autonomous Loop"
            )
            await send_telegram_alert(telegram_msg)

        except Exception as e:
            logger.error(f"💥 Runtime Exception Error: {str(e)}")
            upi_logs_database.insert(0, {"timestamp": time_str, "upi": "NOT_FOUND", "status": "FAILED"})
            await send_telegram_alert(f"⚠️ *UPI MONITOR CLOUD ALERT: NOT FOUND*\n\n🕒 *Time (IST):* {time_str}\n🔴 *Reason:* `{str(e)}` ")

async def start_autonomous_scheduler():
    """Bypass Sleep Engine: Runs infinitely by executing system self-pings every 8 minutes"""
    logger.info("⏳ Autonomous Self-Wakeup Clock Initialized.")
    await asyncio.sleep(10)
    while True:
        try:
            await fetch_upi_job()
            if RENDER_EXTERNAL_URL:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    res = await client.get(RENDER_EXTERNAL_URL)
                    logger.info(f"⚡ Anti-Sleep Self-Ping Dispatched. Status: {res.status_code}")
        except Exception as e:
            logger.error(f"Scheduler Loop Context Error: {e}")
        await asyncio.sleep(8 * 60)

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
        <title>🤖 Hybrid Redirect Interceptor Dashboard</title>
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
            <h2>🤖 Hybrid Redirect Interceptor Dashboard</h2>
            <p style="font-size:12px; color:#aaa;">Status: <span class="badge">Anti-Sleep Active (8 Min)</span></p>
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
