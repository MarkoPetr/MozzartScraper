from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime, timedelta

OUTPUT_FILE = "sofascore_live.xlsx"

def get_mozzart_url_previous_day():
    yesterday = datetime.now() - timedelta(days=1)
    date_str = yesterday.strftime("%Y-%m-%d")
    # Mozzart URL sa filterom završenih mečeva i datumom
    return f"https://www.mozzartbet.com/sr/rezultati?date={date_str}&events=finished"

def scrape_finished_matches():
    matches = []
    url = get_mozzart_url_previous_day()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_timeout(5000)  # čekamo učitavanje JS sadržaja

        # Dohvat svih div elemenata na stranici
        all_divs = page.locator("div")
        total_divs = all_divs.count()
        print(f"Pronađeno ukupno div-ova: {total_divs}")

        # Pravilo: tražimo 4 uzastopna div-a sa tekstom: tim1, tim2, home_goals, away_goals
        text_divs = []
        for i in range(total_divs):
            txt = all_divs.nth(i).text_content().strip()
            if txt:
                text_divs.append(txt)

        i = 0
        while i + 3 < len(text_divs):
            home_team = text_divs[i]
            away_team = text_divs[i + 1]
            home_goals = text_divs[i + 2]
            away_goals = text_divs[i + 3]

            # Proveravamo da li su golovi cifre
            if home_goals.isdigit() and away_goals.isdigit():
                matches.append({
                    "home_team": home_team,
                    "away_team": away_team,
                    "home_goals": int(home_goals),
                    "away_goals": int(away_goals),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                i += 4  # preskakanje na sledeći blok
            else:
                i += 1  # pomeramo se za 1 ako nije validan blok

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
