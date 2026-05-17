import os
import asyncio
import logging
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from playwright.async_api import async_playwright

# Logging Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("UPIMonitor")

app = FastAPI()

# Global memory to store captured UPI addresses for UI
upi_logs_database = []

# Configurations
USERNAME = "5deposit"
PASSWORD = "5Dp@0000"
GATEWAY_ID = "841168a2-dc70-45b1-a078-5dec07c5912a"

async def fetch_upi_job():
    """Core automation block matching the exact Tampermonkey pipeline logic"""
    async with async_playwright() as p:
        logger.info("Starting headless worker cycle...")
        # Render compatible arguments launch configurations
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        
        # Setting custom mobile/desktop user agents to match standard client footprints
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        try:
            # 1. Page login validation sequences
            await page.goto("https://phantom777.now/", timeout=60000)
            
            # Auto filling standard forms fields input matching DOM elements
            await page.fill("input[type='text']", USERNAME)
            await page.fill("input[type='password']", PASSWORD)
            
            # Click and wait for network states idle parameters validation
            await asyncio.sleep(2)  # Human simulation delay
            
            # Yahan hum direct script inject karke checkout logic trigger kar rhe h 
            # Takki browser flow automatic response evaluate kre
            logger.info("Executing script parameters injection inside window context...")
            
            # Hum direct page par fetch trigger kar rahe hain jisse use cookie/session automatic mil jaye
            checkout_url = await page.evaluate(f"""
                async () => {{
                    const SECRET_KEY = "z8uEAb-aN5QE6xY35P736SKwxi4cd9dYPjhw";
                    const TYPE_URL = "https://phantom777.now/api/front/supago/paymenttype";
                    
                    const encryptData = (obj) => CryptoJS.AES.encrypt(JSON.stringify(obj), SECRET_KEY).toString();
                    const decryptData = (str) => CryptoJS.AES.decrypt(str, SECRET_KEY).toString(CryptoJS.enc.Utf8);
                    
                    const res = await fetch(TYPE_URL, {{
                        method: "POST",
                        headers: {{ "content-type": "application/json" }},
                        body: JSON.stringify({{ "data": encryptData({{ "amt": 500, "id": "{GATEWAY_ID}" }}) }})
                    }});
                    const json = await res.json();
                    const decStr = CryptoJS.AES.decrypt(json.data, SECRET_KEY).toString(CryptoJS.enc.Utf8);
                    return JSON.parse(decStr).url;
                }}
            """)

            if not checkout_url:
                raise Exception("Checkout URL generation return blank string parameter.")

            logger.info(f"Checkout URL Parsed: {checkoutUrl}")
            
            # 2. Open checkout gateway url destination inside focus screen
            await page.goto(checkout_url.replace("&amp;", "&"), timeout=60000)
            
            # DOM Scraper watch tracking loops: Scrapes screen elements text matching UPI handle formats
            upi_address = None
            for _ in range(30): # 15 Seconds validation poll loops
                await asyncio.sleep(0.5)
                body_text = await page.inner_text("body")
                import re
                match = re.search(r'[a-zA-Z0-9.\-_]+@[a-zA-Z0-9.\-_]+', body_text)
                if match:
                    possible_upi = match.group(0)
                    if "example.com" not in possible_upi and "w3.org" not in possible_upi:
                        upi_address = possible_upi
                        break
            
            if upi_address:
                log_entry = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "upi": upi_address,
                    "status": "SUCCESS"
                }
                upi_logs_database.insert(0, log_entry) # Push inside memory stack arrays top
                logger.info(f"🎉 UPI Captured Successfully: {upi_address}")
            else:
                logger.warning("⚠️ Scraper Timeout. Unable to look matching string on window.")

        except Exception as e:
            logger.error(f"💥 Pipeline Execution Error Exception: {str(e)}")
        finally:
            await browser.close()

# Background Daemon Scheduler Loop (Runs every 5 minutes continuously)
async def start_infinite_scheduler_loop():
    await asyncio.sleep(10) # Initial server boot time cushion
    while True:
        try:
            await fetch_upi_job()
        except Exception as e:
            logger.error(f"Scheduler Exception Loop: {e}")
        await asyncio.sleep(5 * 60) # Wait 5 minutes before re-executing pipelines

@app.on_event("startup")
async def startup_event():
    # Background worker integration
    asyncio.create_task(start_infinite_scheduler_loop())

# --- WEB DASHBOARD INTERFACE ROUTERS ---
@app.get("/api/logs")
async def get_live_logs_api():
    return JSONResponse(content={"logs": upi_logs_database})

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard_ui_page(request: Request):
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Phantom777 Live Server UPI Monitor Dashboard</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: 'Courier New', monospace; background-color: #121212; color: #ffffff; padding: 20px; }
            .container { max-width: 800px; margin: 0 auto; background: #1e1e1e; padding: 20px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
            h2 { border-bottom: 2px solid #333; padding-bottom: 8px; color: #00ffff; }
            .log-box { background: #000; padding: 15px; height: 350px; overflow-y: auto; border-radius: 5px; border: 1px solid #333; }
            .log-entry { padding: 8px; border-bottom: 1px solid #222; font-size: 13px; display: flex; justify-content: space-between; }
            .timestamp { color: #888; }
            .upi-value { color: #1dd1a1; font-weight: bold; background: #111; padding: 2px 6px; border-radius: 4px; border: 1px solid #1dd1a1; }
            .badge { background: #10ac84; color: #fff; padding: 3px 8px; border-radius: 20px; font-size: 11px; }
            .refresh-btn { background: #e74c3c; border: none; color: white; padding: 10px 20px; border-radius: 4px; cursor: pointer; font-weight: bold; float: right; }
            .refresh-btn:hover { background: #c0392b; }
        </style>
    </head>
    <body>
        <div class="container">
            <button class="refresh-btn" onclick="loadLogsFromServer()">Force Refresh UI 🔄</button>
            <h2>📋 Phantom777 Live Server UPI Monitor</h2>
            <p style="font-size:12px; color:#aaa;">Status: <span class="badge">Live Monitoring Active (Every 5 Mins)</span></p>
            <div class="log-box" id="logs-render-area">Loading timelines entries from backend server memory...</div>
        </div>
        <script>
            async function loadLogsFromServer() {
                try {
                    const res = await fetch('/api/logs');
                    const data = await res.json();
                    const area = document.getElementById('logs-render-area');
                    if(data.logs.length === 0) {
                        area.innerHTML = "<div style='color:#ffa502; text-align:center; padding-top:50px;'>No logs captured yet. Worker loop running...</div>";
                        return;
                    }
                    area.innerHTML = "";
                    data.logs.forEach(log => {
                        area.innerHTML += `
                            <div class="log-entry">
                                <span class="timestamp">[${log.timestamp}]</span>
                                <span class="upi-value">${log.upi}</span>
                                <span style="color:#2ecc71;">[CAPTURED]</span>
                            </div>
                        `;
                    });
                } catch(e) { console.error("Error updates:", e); }
            }
            // Auto sync ui screen every 15 seconds
            setInterval(loadLogsFromServer, 15000);
            window.onload = loadLogsFromServer;
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)