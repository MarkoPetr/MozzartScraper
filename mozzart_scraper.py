from playwright.sync_api import sync_playwright
import pandas as pd
import time

# Datum koji želiš da preuzmeš
DATE = "2025-12-17"
URL = f"https://www.mozzartbet.com/sr/rezultati/Fudbal/1?date={DATE}&events=finished"
OUTPUT_FILE = "mozzart_finished_yesterday.xlsx"

def scrape_finished_matches():
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 🔹 Otvori stranicu
        page.goto(URL, timeout=60000)

        # 🔹 Skroluj dok svi mečevi ne budu učitani
        previous_count = 0
        while True:
            # Broj FT elemenata trenutno u DOM-u
            ft_elements = page.locator("text=FT")
            current_count = ft_elements.count()

            # Scroll do dna
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

            # Sačekaj da se učitaju novi mečevi (maks 5s)
            for _ in range(5):
                time.sleep(1)
                new_count = ft_elements.count()
                if new_count > current_count:
                    break

            if current_count == previous_count:
                break
            previous_count = current_count

        # 🔹 Parsiraj FT i HT rezultate
        body_text = page.locator("body").inner_text()
        lines = [l.strip() for l in body_text.splitlines() if l.strip()]

        i = 0
        while i < len(lines) - 7:
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
        print(f"✅ Sačuvano {len(df)} završenih fudbalskih mečeva")
    else:
        print("⚠️ Nema završenih fudbalskih mečeva")
