from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime, timedelta

OUTPUT_FILE = "sofascore_live.xlsx"

def get_mozzart_url_previous_day():
    yesterday = datetime.now() - timedelta(days=1)
    date_str = yesterday.strftime("%Y-%m-%d")
    return f"https://www.mozzartbet.com/sr/rezultati?date={date_str}&events=finished"

def scrape_finished_matches():
    matches = []
    url = get_mozzart_url_previous_day()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_timeout(5000)  # čekanje učitavanja JS

        # Dohvat svih div i span elemenata
        all_elements = page.locator("div, span")
        total_elements = all_elements.count()
        print(f"Pronađeno ukupno div/span elemenata: {total_elements}")

        # Dohvat svih tekstova i filtriranje praznih ili irelevantnih
        texts = []
        for i in range(total_elements):
            txt = all_elements.nth(i).text_content().strip()
            if txt and txt.lower() not in ["live", "ft", "dodaj u favorite", "uživo"]:
                texts.append(txt)

        # Pravilo: tražimo grupe od 4 uzastopna teksta: [home_team, away_team, home_goals, away_goals]
        i = 0
        while i + 3 < len(texts):
            home_team = texts[i]
            away_team = texts[i + 1]
            home_goals = texts[i + 2]
            away_goals = texts[i + 3]

            if home_goals.isdigit() and away_goals.isdigit():
                matches.append({
                    "home_team": home_team,
                    "away_team": away_team,
                    "home_goals": int(home_goals),
                    "away_goals": int(away_goals),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                i += 4  # preskakanje na sledeći meč
            else:
                i += 1  # pomeranje za 1 ako nije validan blok

        browser.close()
    return matches

def save_to_excel(matches):
    if not matches:
        print("Nema novih završenih mečeva za upis.")
        return
    df = pd.DataFrame(matches)
    # Opcionalno: sortiranje radi preglednosti
    df = df.sort_values(by=["home_team", "away_team"])
    df.to_excel(OUTPUT_FILE, index=False)
    print(f"Sačuvano {len(matches)} mečeva u {OUTPUT_FILE}")

if __name__ == "__main__":
    finished_matches = scrape_finished_matches()
    save_to_excel(finished_matches)
