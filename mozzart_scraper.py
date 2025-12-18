from playwright.sync_api import sync_playwright
import pandas as pd

# Datum koji želiš da preuzmeš
DATE = "2025-12-17"
URL = f"https://www.mozzartbet.com/sr/rezultati/Fudbal/1?date={DATE}&events=finished"
OUTPUT_FILE = "mozzart_finished_yesterday.xlsx"

def scrape_finished_matches():
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, timeout=60000)

        # 🔹 Izvuci ceo array mečeva iz globalnog JS objekta
        # window.__INITIAL_STATE__ ili slično (zavisno od verzije sajta)
        matches_data = page.evaluate("""
            () => {
                // Neki Mozzart sajtovi drže rezultate u window.__INITIAL_STATE__.results
                if (window.__INITIAL_STATE__ && window.__INITIAL_STATE__.results) {
                    return window.__INITIAL_STATE__.results.matches || [];
                }
                return [];
            }
        """)

        # 🔹 Parsiranje i zapisivanje u results
        for match in matches_data:
            results.append({
                "Time": match.get("time", ""),
                "Home": match.get("homeTeam", {}).get("name", ""),
                "Away": match.get("awayTeam", {}).get("name", ""),
                "FT": f"{match.get('score', {}).get('fullTime', {}).get('home', '-')}" \
                      f":{match.get('score', {}).get('fullTime', {}).get('away', '-')}",
                "HT": f"{match.get('score', {}).get('halfTime', {}).get('home', '-')}" \
                      f":{match.get('score', {}).get('halfTime', {}).get('away', '-')}"
            })

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
