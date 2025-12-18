from playwright.sync_api import sync_playwright
import pandas as pd
import os
import time

URL = "https://www.mozzartbet.com/sr/rezultati/Fudbal/1?date=2025-12-17&events=finished"
OUTPUT_DIR = "output"
EXCEL_FILE = os.path.join(OUTPUT_DIR, "mozzart_184_matches.xlsx")

MOBILE_UA = (
    "Mozilla/5.0 (Linux; Android 13; SM-A166B) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Mobile Safari/537.36"
)

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
        page.wait_for_timeout(7000)

        # zatvaranje popup-a sa kolačićima ako postoji
        try:
            page.click("text=Sačuvaj i zatvori", timeout=5000)
            page.wait_for_timeout(3000)
        except:
            pass

        # Scroll i klik na "Učitaj još" dok god postoji
        while True:
            try:
                page.click("text=Učitaj još", timeout=3000)
                page.wait_for_timeout(7000)
            except:
                break

        text = page.inner_text("body")
        browser.close()
    return text

def parse_matches(text):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    matches = []

    i = 0
    while i < len(lines):
        if lines[i] == "FT":
            try:
                # uzimamo sledećih 6 linija
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
                    "Home": home,
                    "Away": away,
                    "FT": f"{ft_home}:{ft_away}",
                    "HT": f"{ht_home}:{ht_away}",
                    "SH": f"{sh_home}:{sh_away}",
                })

            except Exception as e:
                # ako nešto nije kako treba, preskoči taj blok
                pass
            i += 8
        else:
            i += 1
    return matches

def main():
    print("📱 Preuzimam stranicu...")
    text = scrape_text()

    print("🧠 Parsiram mečeve...")
    matches = parse_matches(text)

    df = pd.DataFrame(matches)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df.to_excel(EXCEL_FILE, index=False)

    print(f"✅ Sačuvano {len(df)} mečeva u {EXCEL_FILE}")

if __name__ == "__main__":
    main()
