import os
from datetime import datetime
import time
import json
import smtplib
import zipfile
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

import requests
import pandas as pd

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # dotenv not installed; use environment variables directly

# ==========================================
# 1. CONFIG
# ==========================================
# Sensitive values are loaded from environment variables to avoid committing secrets.
# Required env vars:
#  - PENNY_RAW_COOKIE
#  - PENNY_GUILD_ID
# Optional email env vars:
#  - PENNY_SEND_EMAIL (true/false)
#  - PENNY_RECIPIENT_EMAIL
#  - PENNY_SENDER_EMAIL
#  - PENNY_SENDER_PASSWORD
#  - PENNY_SMTP_SERVER
#  - PENNY_SMTP_PORT
RAW_COOKIE = os.environ.get("PENNY_RAW_COOKIE")
GUILD_ID = os.environ.get("PENNY_GUILD_ID")

SEND_EMAIL = os.environ.get("PENNY_SEND_EMAIL", "true").lower() in ("1", "true", "yes")
RECIPIENT_EMAIL = os.environ.get("PENNY_RECIPIENT_EMAIL")
SENDER_EMAIL = os.environ.get("PENNY_SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("PENNY_SENDER_PASSWORD")

# Optional SMTP overrides
SMTP_SERVER = os.environ.get("PENNY_SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("PENNY_SMTP_PORT", 587))

ZIP_CODES = [
    "30121",
    "30161",
    "30720",
    "30114",
    "30144",
    "30075",
    "30062",
    "30030",
    "30331",
    "30134",
    "30117",
    "30501",
]


def run_mission() -> None:
    """Run the penny-items mission and produce a dashboard HTML file and exports."""
    print(f"🚀 Mission Start: {datetime.now().strftime('%I:%M %p')}")
    session = requests.Session()

    # Validate required configuration before making requests
    if not RAW_COOKIE or not GUILD_ID:
        print(
            "⚠️ Missing required configuration: set PENNY_RAW_COOKIE and PENNY_GUILD_ID environment variables. Aborting."
        )
        return

    session.headers.update(
        {"User-Agent": "Mozilla/5.0", "X-Guild-Id": GUILD_ID, "Cookie": RAW_COOKIE}
    )

    # Validate email config; if incomplete, disable email for this run
    global SEND_EMAIL  # pylint: disable=global-statement
    if SEND_EMAIL and (not SENDER_EMAIL or not SENDER_PASSWORD or not RECIPIENT_EMAIL):
        print(
            "⚠️ Incomplete email config (PENNY_SENDER_EMAIL, PENNY_SENDER_PASSWORD, "
            "PENNY_RECIPIENT_EMAIL). Email sending disabled for this run."
        )
        SEND_EMAIL = False

    all_data = []

    out_dir = os.path.join(os.getcwd(), "outputs")
    os.makedirs(out_dir, exist_ok=True)
    raw_path = os.path.join(out_dir, "raw_responses.jsonl")

    for zip_code in ZIP_CODES:
        print(f"📡 Scanning {zip_code}...", end=" ", flush=True)
        try:
            r = session.get(
                "https://pro.scouterdev.io/api/penny-items",
                params={
                    "zip_code": zip_code,
                    "guildId": GUILD_ID,
                    "experimental": "true",
                    "include_out_of_stock": "false",
                },
                timeout=15,
            )
            if r.status_code == 200:
                try:
                    data = r.json()
                except ValueError:
                    data = []
                # append raw response for auditing
                with open(raw_path, "a", encoding="utf-8") as rf:
                    entry = {
                        "ts": datetime.now().isoformat(),
                        "zip_code": zip_code,
                        "status": r.status_code,
                        "body": data,
                    }
                    rf.write(json.dumps(entry, ensure_ascii=False) + "\n")

                all_data.extend(data)
                print(f"✅ {len(data)} (saved raw to {raw_path})")
            else:
                print(f"⚠️ HTTP {r.status_code}")
        except requests.RequestException:
            print("❌ Timeout or request error")
        time.sleep(1.2)

    if not all_data:
        print("Empty API response. Check Cookie!")
        return

    df = pd.DataFrame(all_data).drop_duplicates(subset=["store_sku", "store_name"])

    # --- FLEXIBLE STOCK CHECKING ---
    stock_col = next(
        (c for c in ["stock", "total_stock", "on_hand", "quantity"] if c in df.columns),
        None,
    )
    if stock_col:
        df["display_stock"] = (
            pd.to_numeric(df[stock_col], errors="coerce").fillna(0).astype(int)
        )
    else:
        df["display_stock"] = "Check App"

    # --- DATE CALCULATION ---
    date_col = next(
        (c for c in ["dropped_at", "date_pennied", "updated_at"] if c in df.columns),
        None,
    )
    if date_col:
        df["penny_date"] = pd.to_datetime(df[date_col], errors="coerce")
        # Use apply to compute days to avoid static type checker issues with .dt
        df["days_old"] = df["penny_date"].apply(
            lambda d: int((datetime.now() - d).days) if pd.notna(d) else 999
        )
    else:
        df["penny_date"] = pd.NaT
        df["days_old"] = 999

    # normalize and enrich fields for the dashboard
    df = normalize_scan_df(df)

    # --- PERSISTENT EXPORTS ---
    out_csv = os.path.join(out_dir, "last_scan.csv")
    out_json = os.path.join(out_dir, "last_scan.json")
    try:
        df.to_csv(out_csv, index=False)
        df.to_json(out_json, orient="records", force_ascii=False)
        print(f"💾 Saved scan outputs: {out_csv}, {out_json}")
    except (OSError, ValueError) as e:
        print(f"⚠️ Failed to save outputs: {e}")

    html_path = generate_dashboard(df)

    # Send email if configured - zip the HTML and send the ZIP (more reliable for large dashboards)
    if SEND_EMAIL and html_path:
        zip_path = os.path.splitext(html_path)[0] + ".zip"
        try:
            # remove existing zip if present
            if os.path.exists(zip_path):
                os.remove(zip_path)
            with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                zf.write(html_path, arcname=os.path.basename(html_path))
            print(f"💾 Zipped dashboard: {zip_path}")
            send_zip_email(zip_path)
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"⚠️ Failed to zip or send dashboard: {e}")


def normalize_scan_df(df: pd.DataFrame) -> pd.DataFrame:
    # pylint: disable=unused-variable

    """Normalize and enrich a scan DataFrame for dashboard consumption.

    Adds columns: display_stock, penny_date, days_old, price, retail_price,
    image_link, location, raw_stock_field, raw_date_field.
    Returns the modified DataFrame.
    """
    # --- FLEXIBLE STOCK CHECKING ---
    stock_col = next(
        (c for c in ["stock", "total_stock", "on_hand", "quantity"] if c in df.columns),
        None,
    )
    if stock_col:
        df["display_stock"] = (
            pd.to_numeric(df[stock_col], errors="coerce").fillna(0).astype(int)
        )
    else:
        df["display_stock"] = "Check App"

    # --- DATE CALCULATION ---
    date_col = next(
        (c for c in ["dropped_at", "date_pennied", "updated_at"] if c in df.columns),
        None,
    )
    if date_col:
        df["penny_date"] = pd.to_datetime(df[date_col], errors="coerce")
        df["days_old"] = df["penny_date"].apply(
            lambda d: int((datetime.now() - d).days) if pd.notna(d) else 999
        )
    else:
        df["penny_date"] = pd.NaT
        df["days_old"] = 999

    # --- IDENTIFY OTHER FIELDS ---
    _sku_col = next(
        (c for c in ["store_sku", "sku", "sku_number"] if c in df.columns), "store_sku"
    )
    _upc_col = next((c for c in ["upc", "barcode", "gtin"] if c in df.columns), None)
    _price_col = next(
        (
            c
            for c in ["price", "current_price", "offer_price", "price_cents"]
            if c in df.columns
        ),
        None,
    )
    _retail_col = next(
        (c for c in ["retail_price", "list_price", "msrp"] if c in df.columns), None
    )
    _img_col = next(
        (
            c
            for c in ["image_link", "image", "image_url", "thumbnail"]
            if c in df.columns
        ),
        None,
    )
    _loc_col = next(
        (c for c in ["location", "aisle", "location_description"] if c in df.columns),
        None,
    )

    # record detected field names to DataFrame attrs (used for debugging/UI)
    _detected_fields = (_sku_col, _upc_col, _price_col, _retail_col, _img_col, _loc_col)
    df.attrs["detected_fields"] = [x for x in _detected_fields if x]
    df["store_sku"] = df.get(_sku_col, df.get("store_sku"))
    df["upc"] = df[_upc_col] if _upc_col in df.columns else df.get("upc", "N/A")

    def _format_price(v):
        if pd.isna(v):
            return "N/A"
        try:
            v = float(v)
            if v > 1000:  # maybe cents
                return f"${v/100:.2f}"
            return f"${v:.2f}"
        except (ValueError, TypeError):
            return str(v)

    def _detect_price_row(row):
        for c in ["price", "current_price", "offer_price", "price_cents"]:
            if c in row and pd.notna(row[c]):
                v = row[c]
                if c == "price_cents":
                    try:
                        return f"${float(v)/100:.2f}"
                    except Exception:  # pylint: disable=broad-exception-caught
                        return "N/A"
                try:
                    return f"${float(v):.2f}"
                except Exception:  # pylint: disable=broad-exception-caught
                    return str(v)
        return "N/A"

    df["price"] = df.apply(_detect_price_row, axis=1)
    df["retail_price"] = (
        df[_retail_col].apply(_format_price)
        if _retail_col in df.columns
        else df.get("retail_price", "N/A")
    )
    df["image_link"] = (
        df[_img_col] if _img_col in df.columns else df.get("image_link", "")
    )
    df["location"] = (
        df[_loc_col] if _loc_col in df.columns else df.get("location", "Check Aisle")
    )

    # expose the raw field names for UI and debugging (per-row)
    def _raw_stock_field(row):
        for c in ["stock", "total_stock", "on_hand", "quantity"]:
            if c in row and pd.notna(row[c]):
                return c
        return ""

    df["raw_stock_field"] = df.apply(_raw_stock_field, axis=1)

    df["raw_date_field"] = date_col if date_col else ""

    return df


def generate_dashboard(df):
    """Stream-write the dashboard HTML to avoid large in-memory concatenation and
    provide progress logs for long runs. Returns the generated HTML file path.
    """
    stores = sorted(df["store_name"].unique())
    store_options = "".join(
        [f'<option value="{s}">{s.upper()}</option>' for s in stores]
    )

    html_path = "Penny_Dashboard.html"
    total_items = len(df)
    written = 0
    print(f"🧩 Generating dashboard for {len(stores)} stores ({total_items} items)")

    header = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
        <style>
            body {{ background: #121212; color: #eee; font-family: sans-serif; margin: 0; padding-bottom: 80px; }}
            .nav {{ position: sticky; top: 0; background: #121212; padding: 10px; border-bottom: 2px solid #ffb142; z-index: 1000; }}
            input, select {{ width: 100%; padding: 12px; margin: 5px 0; background: #222; color: #fff; border: 1px solid #444; border-radius: 8px; box-sizing: border-box; font-size: 16px; }}
            .card {{ background: #1e1e1e; margin: 10px; padding: 12px; border-radius: 10px; display: flex; border-left: 5px solid #ffb142; align-items: center; }}
            .card.checked {{ opacity: 0.35; filter: grayscale(1); }}
            .card.ignored {{ opacity: 0.18; filter: grayscale(1); border-left-color: #444; }}
            .card img {{ width: 120px; height: 120px; border-radius: 8px; margin-right: 12px; object-fit: cover; }}
            .thumb {{ cursor: zoom-in; }}
            .info {{ flex: 1; min-width: 0 }}
            .details {{ display: none; background: #0f0f0f; color: #ddd; padding: 8px; margin-top: 8px; border-radius: 6px; font-family: monospace; font-size: 12px; white-space: pre-wrap; max-height: 300px; overflow: auto }}
            /* Responsive grid on wider screens */
            @media(min-width:900px) {{
                #cont {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; }}
                .store-wrapper {{ display: block; }}
            }}
            @media(min-width:1200px) {{
                #cont {{ grid-template-columns: repeat(3, 1fr); }}
            }}
            .item-name {{ font-weight: bold; display: block; margin-bottom: 4px; font-size: 0.9em; }}
            .location {{ color: #ffb142; font-weight: bold; font-size: 0.8em; }}
            .meta {{ color: #888; font-size: 0.75em; margin-top: 5px; font-family: monospace; }}
            .store-header {{ background: #b33939; padding: 10px; margin-top: 20px; font-weight: bold; }}
            .badge {{ font-size: 0.7em; padding: 2px 5px; border-radius: 4px; font-weight: bold; }}
            .hide-btn {{ background: transparent; color: #ff4757; border: 1px solid #ff4757; padding: 6px 10px; border-radius: 6px; font-size: 0.8em; margin-left: 5px; }}
            .restore-btn {{ display: none; color: #1dd1a1; border-color: #1dd1a1; }}
            .card.ignored .restore-btn {{ display: inline-block; }}
            .card.ignored .hide-btn.ignore-btn {{ display: none; }}
            .controls {{ display: flex; gap: 8px; flex-wrap: wrap; align-items: center; margin-top: 6px; }}
            .pill {{ background: #222; color: #ffb142; border: 1px solid #ffb142; padding: 6px 12px; border-radius: 999px; font-size: 0.8em; }}
            .fab {{ position: fixed; bottom: 20px; right: 20px; background: #ffb142; color: #000; border: none; padding: 15px 25px; border-radius: 30px; font-weight: bold; font-size: 1em; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }}
        </style>
    </head>
    <body>
        <div class="nav">
            <h3 style="margin:5px 0; color:#ffb142;">🎯 Penny Command</h3>
            <input type="text" id="srch" placeholder="🔍 Search SKU or Item..." onkeyup="fltr()">
            <select id="st" multiple size="8" onchange="fltr()"><option value="all">📍 All Stores</option>{store_options}</select>
            <select id="dt" onchange="fltr()"><option value="all">🕒 Any Date</option><option value="1">🚀 New Today</option></select>
            <div class="controls">
                <label style="display:flex; align-items:center; gap:6px; font-size:0.9em;">
                    <input type="checkbox" id="hideIgnored" checked onchange="fltr()" style="width:auto;">
                    <span>Hide ignored items</span>
                </label>
                <button class="pill" onclick="clearIgnores()">Clear ignored</button>
            </div>
        </div>
        <div id="cont">
"""

    footer = """
        </div>
        <button class="fab" onclick="localStorage.clear(); location.reload();">🔄 Reset</button>

        <!-- Image modal -->
        <div id="imgModal" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.9); z-index:2000; align-items:center; justify-content:center;">
            <div style="position:relative; width:100%; height:100%; display:flex; align-items:center; justify-content:center;">
                <img id="modalImg" src="" style="max-width:98%; max-height:88%; border-radius:6px; box-shadow:0 10px 30px rgba(0,0,0,0.7);" />
                <div id="modalMeta" style="position:absolute; bottom:16px; left:16px; right:16px; color:#fff; font-family:monospace; font-size:14px; background: rgba(0,0,0,0.35); padding:6px; border-radius:6px; text-align:center;"></div>
                <button id="modalClose" onclick="closeModal()" style="position:absolute; top:12px; right:12px; background:#ffb142; border:none; padding:8px 12px; border-radius:6px;">Close</button>
            </div>
        </div>

        <script>
            const IGNORE_PREFIX = 'ignored::';

            function isIgnored(id) {{
                return localStorage.getItem(IGNORE_PREFIX + id) || localStorage.getItem(id);
            }}

            function markIgnored(id) {{
                localStorage.setItem(IGNORE_PREFIX + id, '1');
                localStorage.removeItem(id); // clean legacy keys
            }}

            function unignore(id) {{
                localStorage.removeItem(IGNORE_PREFIX + id);
                localStorage.removeItem(id);
            }}

            function clearIgnores() {{
                Object.keys(localStorage).forEach(k => {{
                    if (k.startsWith(IGNORE_PREFIX) || k.startsWith('id_')) {{
                        localStorage.removeItem(k);
                    }}
                }});
                fltr();
            }}

            function applyIgnoreState(card) {{
                const ignored = !!isIgnored(card.id);
                card.classList.toggle('ignored', ignored);
                return ignored;
            }}

            function fltr() {{
                let q = document.getElementById('srch').value.toLowerCase();
                let st = document.getElementById('st');
                let selected = Array.from(st.selectedOptions).map(o => o.value);
                let d = document.getElementById('dt').value;
                let hideIgnored = document.getElementById('hideIgnored').checked;

                document.querySelectorAll('.store-wrapper').forEach(w => {{
                    let storeName = w.getAttribute('data-store');
                    let sMatch = selected.includes('all') || selected.length === 0 || selected.includes(storeName);
                    let hasVis = false;

                    w.querySelectorAll('.card').forEach(c => {{
                        const ignored = applyIgnoreState(c);
                        let txt = c.innerText.toLowerCase();
                        let match = (txt.includes(q) || txt.split('\n').some(l => l.includes(q))) && sMatch;
                        if (d === '1' && parseInt(c.getAttribute('data-days')) > 1) match = false;

                        const shouldShow = match && !(ignored && hideIgnored);
                        c.style.display = shouldShow ? 'flex' : 'none';
                        if (shouldShow) hasVis = true;
                    }});
                    w.style.display = hasVis ? 'block' : 'none';
                }});
            }}

            function toggleCheck(id) {{
                document.getElementById(id).classList.toggle('checked');
            }}

            function openModal(src, meta) {{
                const modal = document.getElementById('imgModal');
                const img = document.getElementById('modalImg');
                const md = document.getElementById('modalMeta');
                img.src = '';
                md.textContent = '';
                modal.style.display = 'flex';
                img.onload = () => {{ /* loaded */ }};
                img.onerror = () => {{ md.textContent = 'Failed to load image'; }};
                img.src = src;
                md.textContent = meta || '';
            }}

            function closeModal() {{
                const modal = document.getElementById('imgModal');
                const img = document.getElementById('modalImg');
                modal.style.display = 'none';
                img.src = '';
            }}

            document.addEventListener('keydown', (e) => {{ if (e.key === 'Escape') closeModal(); }});
            document.getElementById('imgModal').addEventListener('click', (e) => {{ if (e.target && e.target.id === 'imgModal') closeModal(); }});

            function toggleDetails(e, id) {{
                if (e) e.stopPropagation();
                let el = document.getElementById('details_' + id);
                if (!el) return;
                el.style.display = (el.style.display === 'none') ? 'block' : 'none';
            }}

            function ignoreItem(e, id) {{
                if (e) e.stopPropagation();
                markIgnored(id);
                fltr();
            }}

            function restoreItem(e, id) {{
                if (e) e.stopPropagation();
                unignore(id);
                fltr();
            }}

            window.onload = () => {{
                document.querySelectorAll('.card').forEach(c => applyIgnoreState(c));
                fltr();
            }};
        </script>
    </body>
    </html>
    """

    try:
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(header)

            for store, items in df.groupby("store_name"):
                f.write(
                    f'<div class="store-wrapper" data-store="{store}"><div class="store-header">🏪 {store.upper()}</div>'
                )
                for _, item in items.iterrows():
                    uid = f"id_{hash(item['store_sku'] + store) % 10**8}"
                    days = item["days_old"]
                    new_tag = (
                        '<span class="badge" style="background:#2ecc71; color:black;">NEW TODAY</span>'
                        if days <= 1
                        else ""
                    )

                    raw = {
                        k: (None if pd.isna(v) else v)
                        for k, v in item.to_dict().items()
                    }
                    raw_json = json.dumps(raw, ensure_ascii=False, indent=2).replace(
                        "</", "<" + chr(92) + "/"
                    )
                    stock_field = item.get("raw_stock_field", "")
                    stock_field_val = item.get(stock_field, "") if stock_field else ""

                    meta_text = f"SKU: {item.get('store_sku')} • Price: {item.get('price','N/A')} • Stock: {item['display_stock']}"
                    meta_js = json.dumps(meta_text)
                    full_js = json.dumps(item.get("image_link", ""))
                    thumb_url = item.get("image_link", "")

                    card_html = f"""
                    <div class="card" id="{uid}" data-days="{days}" onclick="toggleCheck('{uid}')">
                        <img class="thumb" src="{thumb_url}" data-full={full_js} loading="lazy" onerror="this.src='https://via.placeholder.com/140?text=No+Image'" onclick="event.stopPropagation(); openModal({full_js}, {meta_js})">
                        <div class="info">
                            {new_tag}
                            <span class="item-name">{item.get('item_name', 'Unknown Item')}</span>
                            <span class="location">📍 {item.get('location', 'Check Aisle')}</span>
                            <div class="meta">SKU: {item.get('store_sku')} | UPC: {item.get('upc','N/A')} | Stock: {item['display_stock']} <small style='opacity:.8'>(raw: {stock_field or 'N/A'}={stock_field_val})</small></div>
                            <div class="meta">Price: {item.get('price','N/A')} | Retail: {item.get('retail_price','N/A')} | Pennied: {item.get('penny_date') if not pd.isna(item.get('penny_date')) else 'N/A'}</div>
                            <button class="hide-btn ignore-btn" onclick="ignoreItem(event, '{uid}')">IGNORE</button>
                            <button class="hide-btn restore-btn" onclick="restoreItem(event, '{uid}')">RESTORE</button>
                            <button class="hide-btn" onclick="toggleDetails(event, '{uid}')">DETAILS</button>
                            <pre class="details" id="details_{uid}" style="display:none">{raw_json}</pre>
                        </div>
                    </div>
                    """

                    f.write(card_html)
                    written += 1
                    if written % 200 == 0:
                        print(f"  • Written {written}/{total_items} items...")

                f.write("</div>")

            f.write(footer)
        print("✅ Dashboard Complete! Open Penny_Dashboard.html in your folder.")
        return html_path
    except Exception as e:
        print(f"⚠️ Failed to generate HTML: {e}")
        return None
    return "Penny_Dashboard.html"


def send_zip_email(zip_file):
    """Send a ZIP attachment via SMTP using the configured credentials."""
    try:
        # Safety: ensure credentials are present
        if not SENDER_EMAIL or not SENDER_PASSWORD or not RECIPIENT_EMAIL:
            print(
                "⚠️ Email not sent: missing SENDER/RECIPIENT or password environment variables."
            )
            return
        if not os.path.exists(zip_file):
            print(f"⚠️ ZIP file not found: {zip_file}")
            return
        size = os.path.getsize(zip_file)
        if size > 25 * 1024 * 1024:
            print(
                f"⚠️ ZIP ({size/1024/1024:.2f} MB) exceeds Gmail's 25MB attachment limit. Email not sent."
            )
            return

        # Build message
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECIPIENT_EMAIL
        msg["Subject"] = (
            f"🎯 Penny Dashboard (zipped) - {datetime.now().strftime('%b %d, %I:%M %p')}"
        )
        msg.attach(MIMEText("Attached: Penny_Dashboard.zip", "plain"))

        with open(zip_file, "rb") as f:
            part = MIMEApplication(f.read(), _subtype="zip")
            part.add_header(
                "Content-Disposition", "attachment", filename=os.path.basename(zip_file)
            )
            msg.attach(part)

        smtp_host = globals().get("SMTP_SERVER") or "smtp.gmail.com"
        smtp_port = globals().get("SMTP_PORT") or 587

        print(f"📧 Sending ZIP to {RECIPIENT_EMAIL} (SMTP {smtp_host}:{smtp_port})...")
        try:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=60) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                server.send_message(msg)
            print(f"✅ ZIP sent successfully to {RECIPIENT_EMAIL}!")
        except smtplib.SMTPAuthenticationError as e:
            print(f"⚠️ Authentication failed: {e}")
            print(
                "💡 TIP: Ensure you are using a Gmail App Password and that the sender "
                "matches the app password account."
            )
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"⚠️ Failed to send ZIP: {e}")

    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"⚠️ Failed to prepare ZIP email: {e}")


def send_dashboard_email(html_file):
    """Send the dashboard HTML file via email."""
    try:
        # Safety: ensure credentials are present
        if not SENDER_EMAIL or not SENDER_PASSWORD or not RECIPIENT_EMAIL:
            print(
                "⚠️ Email not sent: missing SENDER/RECIPIENT or password environment variables."
            )
            return
        # Read the HTML file
        with open(html_file, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🎯 Penny List - {datetime.now().strftime('%b %d, %I:%M %p')}"
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECIPIENT_EMAIL

        # Attach HTML
        html_part = MIMEText(html_content, "html")
        msg.attach(html_part)

        # Resolve SMTP config from globals and validate
        smtp_host = globals().get("SMTP_SERVER")
        smtp_port = globals().get("SMTP_PORT")
        if not smtp_host or not smtp_port:
            print(
                "⚠️ SMTP configuration missing (SMTP_SERVER or SMTP_PORT). Email not sent."
            )
            return

        print(
            f"📧 Sending email to {RECIPIENT_EMAIL} (SMTP {smtp_host}:{smtp_port})..."
        )
        try:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                server.send_message(msg)
            print(f"✅ Email sent successfully to {RECIPIENT_EMAIL}!")
        except smtplib.SMTPAuthenticationError as e:
            print(f"⚠️ Authentication failed: {e}")
            print(
                "💡 TIP: Ensure you are using a Gmail App Password (not your account "
                "password) and that the sender address matches the app password account."
            )
        except smtplib.SMTPConnectError as e:
            print(f"⚠️ SMTP connection error: {e}")
        except smtplib.SMTPRecipientsRefused as e:
            print(f"⚠️ Recipient refused: {e}")
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"⚠️ Failed to send email: {e}")
            print(
                "💡 TIP: Network or SMTP server may be blocking the connection, or "
                "credentials are incorrect."
            )
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"⚠️ Failed to send email: {e}")
        print(
            "💡 TIP: For Gmail, use an App Password from "
            "https://myaccount.google.com/apppasswords"
        )


if __name__ == "__main__":
    run_mission()
