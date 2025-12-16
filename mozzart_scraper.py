from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime

OUTPUT_FILE = "sofascore_live.xlsx"
MOZZART_URL = "https://www.mozzartbet.com/sr/rezultati?events=finished"

def scrape_finished_matches():
    matches = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Otvaramo stranicu sa završenim mečevima
        page.goto(MOZZART_URL, timeout=60000)
        page.wait_for_timeout(5000)  # čekamo učitavanje JS sadržaja

        # Selektujemo sve blokove mečeva
        match_blocks = page.locator(".event-row")  # proveriti stvarnu klasu za meč

        for i in range(match_blocks.count()):
            block = match_blocks.nth(i)

            # Timovi
            home_team = block.locator(".home-team").text_content().strip()
            away_team = block.locator(".away-team").text_content().strip()

            # Golovi
            home_goals = block.locator(".home-score span").text_content().strip()
            away_goals = block.locator(".away-score span").text_content().strip()

            matches.append({
                "home_team": home_team,
                "away_team": away_team,
                "home_goals": int(home_goals),
                "away_goals": int(away_goals),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

        browser.close()

    return matches

def save_to_excel(matches):
    if not matches:
        print("Nema novih završenih mečeva za upis.")
        return

    df = pd.DataFrame(matches)
    df.to_excel(OUTPUT_FILE, index=False)
    print(f"Sačuvano {len(matches)} mečeva u {OUTPUT_FILE}")

if __name__ == "__main__":
    finished_matches = scrape_finished_matches()
    save_to_excel(finished_matches)
