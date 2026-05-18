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

# Logging Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("UniversalInterceptor")

app = FastAPI()

# Global memory to store captured UPI addresses for UI
upi_logs_database = []

# Configurations
USERNAME = "5deposit"
PASSWORD = "5Dp@0000"

# Reading credentials safely from Render Environment Variables
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def get_india_time():
    """Helper to explicitly generate current time in Indian Standard Time (IST)"""
    utc_now = datetime.now(timezone.utc)
    ist_now = utc_now.astimezone(timezone(timedelta(hours=5, minutes=30)))
    return ist_now

async def send_telegram_alert(message: str):
    """Helper function to send live status logs directly to Telegram Channel/Chat"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("⚠️ Telegram Environment Variables not configured on dashboard. Skipping alert.")
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
            response = await client.post(url, json=payload)
            if response.status_code != 200:
                logger.error(f"❌ Telegram API Error: {response.text}")
    except Exception as e:
        logger.error(f"💥 Failed to dispatch Telegram notification: {str(e)}")

async def fetch_upi_job():
    """Universal Engine: Dynamic Hybrid Tracking with optimized DOM navigation to prevent timeouts"""
    logger.info("🚀 Launching Universal Hybrid Network Watchdog...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox", 
                "--disable-setuid-sandbox", 
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled" # Soft bypass for headless checks
            ]
        )
        
        # Setting a standard viewport and locale to look like a normal browser
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720},
            locale="en-US"
        )
        page = await context.new_page()
        
        # Shared thread variables
        captured_data = {"upi": None}

        # TRACKING LAYER 1: Raw Global JSON Network Interceptor
        async def response_handler(response):
            try:
                if "application/json" in (response.headers.get("content-type") or ""):
                    response_text = await response.text()
                    parsed_json = json.loads(response_text)
                    
                    def deep_search_upi(obj):
                        if isinstance(obj, dict):
                            for k, v in obj.items():
                                if k in ["upi_id", "upi", "vpa"] and isinstance(v, str) and "@" in v:
                                    return v
                                if isinstance(v, (dict, list)):
                                    res = deep_search_upi(v)
                                    if res:
                                        return res
                        elif isinstance(obj, list):
                            for item in obj:
                                res = deep_search_upi(item)
                                if res:
                                    return res
                        return None

                    extracted_handle = deep_search_upi(parsed_json)
                    if extracted_handle and not any(x in extracted_handle for x in ["example.com", "w3.org"]):
                        captured_data["upi"] = extracted_handle
                        logger.info(f"📡 Global Interceptor Captured Raw JSON UPI: {extracted_handle}")
            except Exception:
                pass

        page.on("response", response_handler)

        try:
            # FIXED: Added domcontentloaded cushion to prevent 30s timeout on heavy images/scripts
            logger.info("📡 Navigating to Phantom777 Portal...")
            await page.goto("https://phantom777.now/", timeout=45000, wait_until="domcontentloaded")
            
            # FIXED: Wait explicitly for inputs to render to avoid element filling crashes
            await page.wait_for_selector("input[type='text']", timeout=15000)
            await page.fill("input[type='text']", USERNAME)
            await page.fill("input[type='password']", PASSWORD)
            await asyncio.sleep(2)
            
            logger.info("🔑 Step 2: Evaluating layered checkout token maps dynamically...")
            
            # 2. Cryptographic Session Link Extractor
            checkout_url = await page.evaluate("""
                async () => {
                    const SECRET_KEY = "z8uEAb-aN5QE6xY35P736SKwxi4cd9dYPjhw";
                    const LIST_URL  = "https://phantom777.now/api/front/supago/paymentlist";
                    const TYPE_URL  = "https://phantom777.now/api/front/supago/paymenttype";
                    const encryptData = (obj) => CryptoJS.AES.encrypt(JSON.stringify(obj), SECRET_KEY).toString();
                    const decryptData = (str) => CryptoJS.AES.decrypt(str, SECRET_KEY).toString(CryptoJS.enc.Utf8);

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
                    
                    let targetUrl = "";
                    if(typeJson.success && typeJson.data && typeJson.data.url) targetUrl = typeJson.data.url;
                    else targetUrl = JSON.parse(decryptData(typeJson.data)).url || JSON.parse(decryptData(typeJson.data)).data.url;
                    return targetUrl;
                }
            """)

            if not checkout_url:
                raise Exception("Failed to dynamically evaluate checkout redirection sequence parameters.")

            clean_url = checkout_url.replace("&amp;", "&")
            logger.info(f"🔗 Navigating globally to gateway endpoint destination: {clean_url}")
            
            # 3. Open dynamic destination tab view container
            await page.goto(clean_url, timeout=45000, wait_until="domcontentloaded")
            await asyncio.sleep(3) # Synchronization window
            
            # TRACKING LAYER 2: Live Query String Parameter Parser Injection
            current_active_url = page.url
            parsed_url = urlparse(current_active_url)
            query_params = parse_qs(parsed_url.query)
            live_numeric_order_id = query_params.get('order', [None])[0]
            
            if live_numeric_order_id and len(live_numeric_order_id) > 5:
                logger.info(f"⚡ Detected multi-request parameter target key: {live_numeric_order_id}. Initializing forced pipeline request cascade...")
                
                captured_via_injection = await page.evaluate("""
                    async (orderId) => {
                        try {
                            const targetApiUrl = `https://api.paybitra.com/v1/payIn/assign-bank/${orderId}`;
                            const res = await fetch(targetApiUrl, {
                                "method": "POST",
                                "headers": { "content-type": "application/json" },
                                "body": JSON.stringify({ "amount": 500, "type": "upi" })
                            });
                            const json = await res.json();
                            if(json && json.data && json.data.bank && json.data.bank.upi_id) {
                                return json.data.bank.upi_id;
                            }
                        } catch (e) { return null; }
                        return null;
                    }
                """, live_numeric_order_id)
                
                if captured_via_injection:
                    captured_data["upi"] = captured_via_injection

            # TRACKING LAYER 3: Global Watchdog Core Fallback
            upi_address = None
            for _ in range(40):
                await asyncio.sleep(0.25)
                if captured_data["upi"]:
                    upi_address = captured_data["upi"]
                    break
                
                body_text = await page.inner_text("body")
                match = re.search(r'[a-zA-Z0-9.\-_]+@[a-zA-Z0-9.\-_]+', body_text)
                if match:
                    possible_upi = match.group(0)
                    if "example.com" not in possible_upi and "w3.org" not in possible_upi:
                        upi_address = possible_upi
                        break
            
            india_now = get_india_time()
            time_str = india_now.strftime("%Y-%m-%d %I:%M:%S %p")

            if upi_address:
                log_entry = { "timestamp": time_str, "upi": upi_address, "status": "SUCCESS" }
                upi_logs_database.insert(0, log_entry)
                logger.info(f"🎉 Universal Framework Success Output: {upi_address}")
                
                telegram_msg = (
                    f"🎯 *UPI CAPTURED SUCCESSFULLY*\n\n"
                    f"💸 *UPI ID:* `{upi_address}`\n"
                    f"🕒 *Time (IST):* {time_str}\n"
                    f"🟢 *Status:* SUCCESS (Universal Hybrid Core)"
                )
                await send_telegram_alert(telegram_msg)
            else:
                raise Exception("Watchdog dynamic synchronization threshold exceeded. No output signatures resolved.")

        except Exception as e:
            logger.error(f"💥 Cloud Interceptor Fatal Exception: {str(e)}")
            india_now = get_india_time()
            time_str = india_now.strftime("%Y-%m-%d %I:%M:%S %p")
            
            telegram_msg = (
                f"⚠️ *UPI MONITOR ALERT: NOT FOUND*\n\n"
                f"🕒 *Time (IST):* {time_str}\n"
                f"🔴 *Error Exception:* `{str(e)}`\n"
                f"❌ *Status:* NOT FOUND"
            )
            await send_telegram_alert(telegram_msg)
        finally:
            await browser.close()

async def start_infinite_scheduler_loop():
    await asyncio.sleep(5)
    while True:
        try:
            await fetch_upi_job()
        except Exception as e:
            logger.error(f"Scheduler core crash: {e}")
        await asyncio.sleep(5 * 60)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(start_infinite_scheduler_loop())

@app.get("/api/logs")
async def get_live_logs_api():
    return JSONResponse(content={"logs": upi_logs_database})

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard_ui_page(request: Request):
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🤖 Deep API Interceptor UPI Monitor Dashboard</title>
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
            .refresh-btn:hover { background: #0f9673; }
        </style>
    </head>
    <body>
        <div class="container">
            <button class="refresh-btn" onclick="loadLogsFromServer()">Force Refresh UI 🔄</button>
            <h2>🤖 Deep API Interceptor UPI Monitor Dashboard</h2>
            <p style="font-size:12px; color:#aaa;">Status: <span class="badge">Universal Watchdog Active (Every 5 Mins Loop)</span></p>
            <div class="log-box" id="logs-render-area">Waiting for backend pipeline response threads...</div>
        </div>
        <script>
            async function loadLogsFromServer() {
                try {
                    const res = await fetch('/api/logs');
                    if (!res.ok) return;
                    const data = await res.json();
                    const area = document.getElementById('logs-render-area');
                    if(data.logs.length === 0) {
                        area.innerHTML = "<div style='color:#ffa502; text-align:center; padding-top:120px;'>No logs captured yet. Universal session engine running...</div>";
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
                } catch(e) { console.error("UI Update Sync Fault:", e); }
            }
            setInterval(loadLogsFromServer, 10000);
            window.onload = loadLogsFromServer;
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)
