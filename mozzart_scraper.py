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
        page.wait_for_timeout(5000)

        # Selektujemo sve roditeljske blokove mečeva
        match_blocks = page.locator("div.event-row")  # probati sa stvarnom klasom za blok meča
        total_blocks = match_blocks.count()
        print(f"Pronađeno blokova mečeva: {total_blocks}")

        for i in range(total_blocks):
            block = match_blocks.nth(i)

            try:
                # Unutar bloka dohvatiti sve div/span elemente sa tekstom
                elements = block.locator("div, span")
                text_elements = [elements.nth(j).text_content().strip() for j in range(elements.count()) if elements.nth(j).text_content().strip()]

                # Pravilo za fudbalski meč: najmanje 4 teksta, prva dva su timovi, sledeća dva su golovi
                if len(text_elements) >= 4:
                    home_team = text_elements[0]
                    away_team = text_elements[1]
                    home_goals = text_elements[2]
                    away_goals = text_elements[3]

                    if home_goals.isdigit() and away_goals.isdigit():
                        matches.append({
                            "home_team": home_team,
                            "away_team": away_team,
                            "home_goals": int(home_goals),
                            "away_goals": int(away_goals),
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
            except Exception as e:
                print(f"Greška kod bloka {i}: {e}")
                continue

        browser.close()
    return matches

def save_to_excel(matches):
    if not matches:
        print("Nema novih završenih mečeva za upis.")
        return
    df = pd.DataFrame(matches)
    # Sortiranje po imenu domaćina radi preglednosti
    df = df.sort_values(by=["home_team", "away_team"])
    df.to_excel(OUTPUT_FILE, index=False)
    print(f"Sačuvano {len(matches)} mečeva u {OUTPUT_FILE}")

if __name__ == "__main__":
    finished_matches = scrape_finished_matches()
    save_to_excel(finished_matches)
