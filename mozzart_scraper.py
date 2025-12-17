from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
import re

OUT = "match_debug.txt"

def url_yesterday():
    d = datetime.now() - timedelta(days=1)
    return f"https://www.mozzartbet.com/sr/rezultati?date={d.strftime('%Y-%m-%d')}&events=finished"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url_yesterday(), timeout=60000)
    page.wait_for_timeout(6000)

    divs = page.locator("div").all()

    found = False
    lines_out = []

    for div in divs:
        txt = div.inner_text().strip()
        if not txt:
            continue

        # tražimo blok sa FT i bar 2 reda teksta
        if "FT" in txt and "\n" in txt:
            lines = [l.strip() for l in txt.split("\n") if l.strip()]

            words = [l for l in lines if not l.isdigit() and not re.search(r"\d{2}:\d{2}", l)]
            numbers = [l for l in lines if l.isdigit()]

            if len(words) >= 2 and len(numbers) >= 4:
                lines_out.append("=== MATCH START ===")
                for l in lines:
                    if l.isdigit():
                        lines_out.append(f"NUM  : {l}")
                    else:
                        lines_out.append(f"TEXT : {l}")
                lines_out.append("=== MATCH END ===\n")
                found = True
                break  # SAMO PRVI MEČ

    browser.close()

with open(OUT, "w", encoding="utf-8") as f:
    for l in lines_out:
        f.write(l + "\n")

if found:
    print("DEBUG MEČ SAČUVAN U match_debug.txt")
else:
    print("NIJEDAN MEČ NIJE NAĐEN")
