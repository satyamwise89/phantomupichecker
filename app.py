import os
import asyncio
import logging
import re
import json
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from playwright.async_api import async_playwright

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AutoHealingInterceptor")

app = FastAPI()

# Global memory table for UI logs
upi_logs_database = []

# Core Credentials Mapping
USERNAME = "5deposit"
PASSWORD = "5Dp@0000"

# Reading Telegram configurations safely from Render Environment Variables
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Tracking session state file destination path inside cloud space
SESSION_STATE_PATH = "/tmp/auth_state.json"

def get_india_time():
    """Generates current timestamp explicitly in Indian Standard Time (IST)"""
    utc_now = datetime.now(timezone.utc)
    ist_now = utc_now.astimezone(timezone(timedelta(hours=5, minutes=30)))
    return ist_now

async def send_telegram_alert(message: str):
    """Dispatches beautiful markdown logging alerts directly to your Telegram Chat ID"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("⚠️ Telegram environment parameters empty. Skipping dispatch.")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        import httpx
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.post(url, json=payload)
            if res.status_code != 200:
                logger.error(f"❌ Telegram API Trace Failure: {res.text}")
    except Exception as e:
        logger.error(f"💥 Telegram connection execution fault: {str(e)}")

async def run_portal_fallback_login(page, context):
    """Fallback Engine: Re-authenticates credentials if cookie streams expire or clear out"""
    logger.info("🔐 Session tokens expired or cleared. Executing fallback login sequence...")
    
    # 1. Navigating securely to login gate
    await page.goto("https://phantom777.now/", timeout=60000, wait_until="domcontentloaded")
    await page.wait_for_selector("input[type='text']", timeout=20000)
    
    # 2. Input element filling stream matching your exact operational credentials
    await page.fill("input[type='text']", USERNAME)
    await page.fill("input[type='password']", PASSWORD)
    await asyncio.sleep(2)
    
    # 3. Clicking landing parameters and saving state context straight back to dynamic file allocation
    await context.storage_state(path=SESSION_STATE_PATH)
    logger.info("🎉 Session tokens recovered successfully! State file refreshed in cloud space.")

async def fetch_upi_job():
    """Universal Engine: Dynamic Session Chaining with Hardcoded Self-Healing Core"""
    logger.info("🚀 Launching Universal Auto-Healing Network Watchdog Routine...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox", 
                "--disable-setuid-sandbox", 
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled"
            ]
        )
        
        # Checking if our automated cloud memory file token footprint exists
        session_exists = os.path.exists(SESSION_STATE_PATH)
        
        # Build residential browser environment blueprint configuration
        if session_exists:
            logger.info("📡 Loading stored cloud session cookie mappings...")
            context = await browser.new_context(
                storage_state=SESSION_STATE_PATH,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
        else:
            logger.info("⚠️ Stored token database blank. Building clean profile block context...")
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )

        page = await context.new_page()
        captured_data = {"upi": None}

        # TRACKING LAYER 1: Raw JSON Response Interception Pipe
        async def response_handler(response):
            try:
                if "application/json" in (response.headers.get("content-type") or ""):
                    res_text = await response.text()
                    parsed = json.loads(res_text)
                    
                    def deep_search(obj):
                        if isinstance(obj, dict):
                            for k, v in obj.items():
                                if k in ["upi_id", "upi", "vpa"] and isinstance(v, str) and "@" in v:
                                    return v
                                if isinstance(v, (dict, list)):
                                    res = deep_search(v)
                                    if res: return res
                        elif isinstance(obj, list):
                            for item in obj:
                                res = deep_search(item)
                                if res: return res
                        return None

                    found = deep_search(parsed)
                    if found and not any(x in found for x in ["example.com", "w3.org"]):
                        captured_data["upi"] = found
            except Exception:
                pass

        page.on("response", response_handler)

        try:
            # Step A: Direct evaluation attempt to land inside portal session state check
            await page.goto("https://phantom777.now/dashboard", timeout=60000, wait_until="domcontentloaded")
            await asyncio.sleep(2)
            
            # If our page lands on login route because cookie session states were cleared or expired
            if "login" in page.url or not session_exists:
                await run_portal_fallback_login(page, context)
            
            logger.info("🔑 Step B: Running inline cryptographic evaluator mapping array channels...")
            
            # Step B: Execute target cryptographic unpacking sequence mirroring local browser engines exactly
            checkout_url = await page.evaluate("""
                async () => {
                    const SECRET_KEY = "z8uEAb-aN5QE6xY35P736SKwxi4cd9dYPjhw";
                    const LIST_URL  = "https://phantom777.now/api/front/supago/paymentlist";
                    const TYPE_URL  = "https://phantom777.now/api/front/supago/paymenttype";
                    const encryptData = (obj) => CryptoJS.AES.encrypt(JSON.stringify(obj), SECRET_KEY).toString();
                    const decryptData = (str) => CryptoJS.AES.decrypt(str, SECRET_KEY).toString(CryptoJS.enc.Utf8);

                    try {
                        const listRes = await fetch(LIST_URL, {
                            method: "POST",
                            headers: { "content-type": "application/json" },
                            body: JSON.stringify({ "data": encryptData({ "amt": 500 }) })
                        });
                        const listJson = await listRes.json();
                        const parsedList = JSON.parse(decryptData(listJson.data));
                        const dynamicGatewayId = parsedList.data.t1[0].pmuniqueid;

                        const typeRes = await fetch(TYPE_URL, {
                            method: "POST",
                            headers: { "content-type": "application/json" },
                            body: JSON.stringify({ "data": encryptData({ "amt": 500, "id": dynamicGatewayId }) })
                        });
                        const typeJson = await typeRes.json();
                        return JSON.parse(decryptData(typeJson.data)).url || JSON.parse(decryptData(typeJson.data)).data.url;
                    } catch(e) { return null; }
                }
            """)

            # AUTO-HEALING SECOND CHECK: If evaluation returned blank but page url states are valid
            if not checkout_url:
                logger.warning("🔄 Session token verify mismatch during evaluation. Initializing forced auto-healing sequence...")
                await run_portal_fallback_login(page, context)
                # Re-attempt navigation check context block
                await page.goto("https://phantom777.now/dashboard", timeout=60000, wait_until="domcontentloaded")
                # Repeat the inline evaluation extract script block after healing context
                checkout_url = await page.evaluate("""
                    async () => {
                        const SECRET_KEY = "z8uEAb-aN5QE6xY35P736SKwxi4cd9dYPjhw";
                        const LIST_URL  = "https://phantom777.now/api/front/supago/paymentlist";
                        const TYPE_URL  = "https://phantom777.now/api/front/supago/paymenttype";
                        const encryptData = (obj) => CryptoJS.AES.encrypt(JSON.stringify(obj), SECRET_KEY).toString();
                        const decryptData = (str) => CryptoJS.AES.decrypt(str, SECRET_KEY).toString(CryptoJS.enc.Utf8);
                        try {
                            const listRes = await fetch(LIST_URL, {
                                method: "POST",
                                headers: { "content-type": "application/json" },
                                body: JSON.stringify({ "data": encryptData({ "amt": 500 }) })
                            });
                            const listJson = await listRes.json();
                            const parsedList = JSON.parse(decryptData(listJson.data));
                            const dynamicGatewayId = parsedList.data.t1[0].pmuniqueid;

                            const typeRes = await fetch(TYPE_URL, {
                                method: "POST",
                                headers: { "content-type": "application/json" },
                                body: JSON.stringify({ "data": encryptData({ "amt": 500, "id": dynamicGatewayId }) })
                            });
                            const typeJson = await typeRes.json();
                            return JSON.parse(decryptData(typeJson.data)).url || JSON.parse(decryptData(typeJson.data)).data.url;
                        } catch(e) { return null; }
                    }
                """)

            if not checkout_url:
                raise Exception("Critical Session Verification Failure. Handshake expired permanently.")

            clean_url = checkout_url.replace("&amp;", "&")
            logger.info(f"🔗 Target routing redirect resolved successfully: {clean_url}")
            
            # Step C: Load gateway destination landing page window
            await page.goto(clean_url, timeout=60000, wait_until="domcontentloaded")
            await asyncio.sleep(3)
            
            # Extract query strings (?order=NUMBER) matching verified model layout
            parsed_url = urlparse(page.url)
            query_params = parse_qs(parsed_url.query)
            live_numeric_order_id = query_params.get('order', [None])[0]
            
            if live_numeric_order_id:
                logger.info(f"🎯 Forcing background injection for Order ID match parameter: {live_numeric_order_id}")
                captured_via_injection = await page.evaluate("""
                    async (orderId) => {
                        try {
                            const res = await fetch(`https://api.paybitra.com/v1/payIn/assign-bank/${orderId}`, {
                                "method": "POST",
                                "headers": { "content-type": "application/json" },
                                "body": JSON.stringify({ "amount": 500, "type": "upi" })
                            });
                            const json = await res.json();
                            return json.data.bank.upi_id;
                        } catch (e) { return null; }
                    }
                """, live_numeric_order_id)
                if captured_via_injection:
                    captured_data["upi"] = captured_via_injection

            # Fallback Watchdog Loop Scan tracking window text contents
            upi_address = None
            for _ in range(40):
                await asyncio.sleep(0.25)
                if captured_data["upi"]:
                    upi_address = captured_data["upi"]
                    break
                
                body_text = await page.inner_text("body")
                match = re.search(r'[a-zA-Z0-9.\-_]+@[a-zA-Z0-9.\-_]+', body_text)
                if match:
                    upi_address = match.group(0)
                    if "example.com" not in upi_address and "w3.org" not in upi_address: break

            time_str = get_india_time().strftime("%Y-%m-%d %I:%M:%S %p")
            if upi_address:
                upi_logs_database.insert(0, {"timestamp": time_str, "upi": upi_address, "status": "SUCCESS"})
                logger.info(f"🎉 Pipeline Execution Success Output: {upi_address}")
                await send_telegram_alert(f"🎯 *UPI CAPTURED SUCCESSFULLY*\n\n💸 *UPI ID:* `{upi_address}`\n🕒 *Time (IST):* {time_str}\n🟢 *Status:* SUCCESS (Universal Self-Healing Engine)")
            else:
                raise Exception("Watchdog search threshold reached. Tracking session timed out.")

        except Exception as e:
            logger.error(f"💥 Session Pipeline Core Exception Error: {str(e)}")
            time_str = get_india_time().strftime("%Y-%m-%d %I:%M:%S %p")
            await send_telegram_alert(f"⚠️ *UPI MONITOR CLOUD ALERT: NOT FOUND*\n\n🕒 *Time (IST):* {time_str}\n🔴 *Error Trace:* `{str(e)}`")
        finally:
            await browser.close()

async def start_infinite_scheduler_loop():
    await asyncio.sleep(5)
    while True:
        try: await fetch_upi_job()
        except Exception as e: logger.error(f"Scheduler loop crash mapping error: {e}")
        await asyncio.sleep(5 * 60) # Standard 5 minute tracking rotation mapping

@app.on_event("startup")
async def startup_event(): asyncio.create_task(start_infinite_scheduler_loop())

@app.get("/api/logs")
async def get_live_logs_api(): return JSONResponse(content={"logs": upi_logs_database})

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard_ui_page(request: Request):
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🤖 Auto-Healing Cloud Interceptor Monitor Dashboard</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: 'Courier New', monospace; background-color: #121212; color: #ffffff; padding: 20px; }
            .container { max-width: 800px; margin: 0 auto; background: #1e1e1e; padding: 20px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); border: 1px solid #34495e; }
            h2 { border-bottom: 2px solid #333; padding-bottom: 8px; color: #00ffff; }
            .log-box { background: #000; padding: 15px; height: 350px; overflow-y: auto; border-radius: 5px; border: 1px solid #333; }
            .log-entry { padding: 10px; border-bottom: 1px solid #222; font-size: 13px; display: flex; justify-content: space-between; align-items: center; }
            .timestamp { color: #ff9f43; font-weight: bold; }
            .upi-value { color: #1dd1a1; font-weight: bold; background: #111; padding: 4px 10px; border-radius: 4px; border: 1px solid #1dd1a1; font-size: 14px; letter-spacing: 0.5px; }
            .badge { background: #10ac84; color: #fff; padding: 3px 8px; border-radius: 20px; font-size: 11px; }
            .refresh-btn { background: #10ac84; border: none; color: white; padding: 10px 20px; border-radius: 4px; cursor: pointer; font-weight: bold; float: right; font-family: monospace; }
        </style>
    </head>
    <body>
        <div class="container">
            <button class="refresh-btn" onclick="loadLogsFromServer()">Force Refresh UI 🔄</button>
            <h2>🤖 Dynamic Auto-Healing UPI Monitor Dashboard</h2>
            <p style="font-size:12px; color:#aaa;">Status: <span class="badge">Universal Self-Healing Active</span></p>
            <div class="log-box" id="logs-render-area">Waiting for dynamic response threads...</div>
        </div>
        <script>
            async function loadLogsFromServer() {
                try {
                    const res = await fetch('/api/logs');
                    if (!res.ok) return;
                    const data = await res.json();
                    const area = document.getElementById('logs-render-area');
                    if(data.logs.length === 0) {
                        area.innerHTML = "<div style='color:#ffa502; text-align:center; padding-top:120px;'>No logs synced yet. Cloud worker active...</div>";
                        return;
                    }
                    area.innerHTML = "";
                    data.logs.forEach(log => {
                        area.innerHTML += `
                            <div class="log-entry">
                                <span class="timestamp">[${log.timestamp}]</span>
                                <span class="upi-value">${log.upi}</span>
                                <span style="color:#2ecc71; font-weight: bold;">🎯 CAPTURED</span>
                            </div>
                        `;
                    });
                } catch(e) { console.error(e); }
            }
            setInterval(loadLogsFromServer, 10000);
            window.onload = loadLogsFromServer;
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)
