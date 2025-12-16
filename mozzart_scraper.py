from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime, timedelta

OUTPUT_FILE = "sofascore_live.xlsx"

# URL sa završnim mečevima prethodnog dana
def get_mozzart_url_previous_day():
    yesterday = datetime.now() - timedelta(days=1)
    date_str = yesterday.strftime("%Y-%m-%d")
    # Mozzart koristi query parametre za datum i filter finished
    return f"https://www.mozzartbet.com/sr/rezultati?date={date_str}&events=finished"

def scrape_finished_matches():
    matches = []
    url = get_mozzart_url_previous_day()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_timeout(5000)  # čekamo da se JS sadržaj učita

        # Selektujemo sve blokove mečeva
        match_blocks = page.locator("div.event-row")  # generalno blok meča
        total_blocks = match_blocks.count()
        print(f"Pronađeno blokova mečeva: {total_blocks}")

        for i in range(total_blocks):
            block = match_blocks.nth(i)

            # Dohvat svih <div> elemenata unutar bloka
            divs = block.locator("div")
            div_count = divs.count()

            # Moramo dohvatiti timove i golove po poziciji
            try:
                # Pretpostavljamo: prva dva div-a sa tekstom su timovi
                home_team = None
                away_team = None
                home_goals = None
                away_goals = None

                # Tražimo prvi div sa tekstom koji nije prazan
                text_divs = [divs.nth(j).text_content().strip() for j in range(div_count) if divs.nth(j).text_content().strip()]
                if len(text_divs) >= 4:
                    home_team = text_divs[0]
                    away_team = text_divs[1]
                    home_goals = int(text_divs[2])
                    away_goals = int(text_divs[3])

                    matches.append({
                        "home_team": home_team,
                        "away_team": away_team,
                        "home_goals": home_goals,
                        "away_goals": away_goals,
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
    df.to_excel(OUTPUT_FILE, index=False)
    print(f"Sačuvano {len(matches)} mečeva u {OUTPUT_FILE}")

if __name__ == "__main__":
    finished_matches = scrape_finished_matches()
    save_to_excel(finished_matches)
