from playwright.sync_api import sync_playwright
import pandas as pd
import time

URL = "https://www.mozzartbet.com/sr/rezultati/Fudbal/1?date=2025-12-17&events=finished"
OUTPUT_FILE = "mozzart_finished_yesterday.xlsx"

def scrape_yesterday_finished():
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, timeout=60000)

        # čekamo da se stranica stabilizuje i da se rezultati učitaju
        page.wait_for_timeout(6000)

        # uzimamo tekst cele stranice
        body_text = page.locator("body").inner_text()

        lines = [l.strip() for l in body_text.splitlines() if l.strip()]

        i = 0
        while i < len(lines) - 6:
            if lines[i] == "FT":
                try:
                    time_match = lines[i - 1]
                    home = lines[i + 1]
                    away = lines[i + 2]
                    ft = lines[i + 3]

                    if ":" in ft:
                        results.append({
                            "Time": time_match,
                            "Home": home,
                            "Away": away,
                            "FT": ft
                        })
                except Exception as e:
                    print("⚠️ Greška pri parsiranju meča:", e)
            i += 1

        browser.close()

    return results

if __name__ == "__main__":
    matches = scrape_yesterday_finished()

    df = pd.DataFrame(matches)
    df.to_excel(OUTPUT_FILE, index=False)

    if matches:
        print(f"✅ Sačuvano {len(df)} završenih fudbalskih mečeva")
    else:
        print("⚠️ Nema završenih fudbalskih mečeva za 17.12.2025")
