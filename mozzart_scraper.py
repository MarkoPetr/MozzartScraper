from playwright.sync_api import sync_playwright
import pandas as pd
import time

URL = "https://www.mozzartbet.com/sr/rezultati/Fudbal/1?date=2025-12-17&events=finished"
OUTPUT_FILE = "mozzart_finished_1712.xlsx"

def scrape_finished_matches():
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, timeout=60000)
        page.wait_for_timeout(8000)  # čekamo da se AJAX sadržaj učita

        body_text = page.locator("body").inner_text()
        lines = [l.strip() for l in body_text.splitlines() if l.strip()]

        i = 0
        while i < len(lines) - 6:  # -6 jer uzimamo 6 linija posle FT
            if lines[i] == "FT":
                try:
                    time_match = lines[i + 1]
                    home = lines[i + 2]
                    away = lines[i + 3]
                    ft_home = lines[i + 4]
                    ft_away = lines[i + 5]
                    ht_home = lines[i + 6]
                    ht_away = lines[i + 7]

                    results.append({
                        "Time": time_match,
                        "Home": home,
                        "Away": away,
                        "FT": f"{ft_home}:{ft_away}",
                        "HT": f"{ht_home}:{ht_away}"
                    })
                except Exception as e:
                    print("⚠️ Greška pri parsiranju meča:", e)
            i += 1

        browser.close()
    return results

if __name__ == "__main__":
    matches = scrape_finished_matches()

    df = pd.DataFrame(matches)
    df.to_excel(OUTPUT_FILE, index=False)

    if matches:
        print(f"✅ Sačuvano {len(df)} završenih fudbalskih mečeva za 17.12.2025")
    else:
        print("⚠️ Nema završenih fudbalskih mečeva za 17.12.2025")
