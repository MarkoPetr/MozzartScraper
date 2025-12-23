from playwright.sync_api import sync_playwright
import pandas as pd
import os
import time
import random
from datetime import datetime, timedelta

# automatski datum za juče
yesterday = datetime.now() - timedelta(days=1)
DATE_STR = yesterday.strftime("%Y-%m-%d")

URL = f"https://www.mozzartbet.com/sr/rezultati/Fudbal/1?date={DATE_STR}&events=finished"
OUTPUT_DIR = "output"
EXCEL_FILE = os.path.join(OUTPUT_DIR, f"mozzart_{DATE_STR}_matches.xlsx")

MOBILE_UA = (
    "Mozilla/5.0 (Linux; Android 13; SM-A166B) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Mobile Safari/537.36"
)

def human_sleep(min_sec=5, max_sec=10):
    wait_time = random.uniform(min_sec, max_sec)
    time.sleep(wait_time)

def scrape_text():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=MOBILE_UA,
            viewport={"width": 412, "height": 915},
            locale="sr-RS"
        )
        page = context.new_page()
        page.goto(URL, timeout=60000)
        time.sleep(random.uniform(6, 9))  # human-like čekanje na učitavanje

        # zatvaranje popup-a sa kolačićima
        try:
            page.click("text=Sačuvaj i zatvori", timeout=5000)
            time.sleep(random.uniform(2,4))
        except:
            pass

        # Scroll i klik na "Učitaj još" dok god postoji
        while True:
            try:
                scroll_height = random.randint(400, 700)
                page.evaluate(f"window.scrollBy(0, {scroll_height})")
                time.sleep(random.uniform(1,2))

                page.click("text=Učitaj još", timeout=3000)
                human_sleep(5,10)
            except:
                break

        text = page.inner_text("body")
        browser.close()
    return text

def parse_matches(text):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    matches = []
    current_league = ""
    i = 0

    while i < len(lines):
        # prepoznaj liniju koja je liga
        if not lines[i].isdigit() and "FT" not in lines[i] and ":" not in lines[i]:
            current_league = lines[i]
            i += 1  # preskoči broj mečeva ispod lige
            if i < len(lines) and lines[i].isdigit():
                i += 1
            continue

        # meč
        if lines[i] == "FT":
            try:
                time_m = lines[i + 1]
                home = lines[i + 2]
                away = lines[i + 3]
                ft_home = int(lines[i + 4])
                ft_away = int(lines[i + 5])
                ht_home = int(lines[i + 6])
                ht_away = int(lines[i + 7])

                sh_home = ft_home - ht_home
                sh_away = ft_away - ht_away

                matches.append({
                    "Time": time_m,
                    "Liga": current_league,
                    "Home": home,
                    "Away": away,
                    "FT": f"{ft_home}:{ft_away}",
                    "HT": f"{ht_home}:{ht_away}",
                    "SH": f"{sh_home}:{sh_away}",
                })

            except Exception as e:
                pass
            i += 8
        else:
            i += 1
    return matches

def main():
    print(f"📅 Preuzimam mečeve od juče: {DATE_STR}")
    text = scrape_text()

    print("🧠 Parsiram mečeve...")
    matches = parse_matches(text)

    df = pd.DataFrame(matches)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df.to_excel(EXCEL_FILE, index=False)

    print(f"✅ Sačuvano {len(df)} mečeva u {EXCEL_FILE}")

if __name__ == "__main__":
    main()
