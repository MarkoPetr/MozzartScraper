from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime, timedelta
import re

URL = "https://www.mozzartbet.com/sr/rezultati?events=finished"

def scrape_yesterday_finished():
    results = []

    # Jučerašnji datum u formatu "16.12. "
    yesterday_str = (datetime.now() - timedelta(days=1)).strftime("%d.%m. ")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, timeout=60000)
        page.wait_for_timeout(5000)  # malo čekamo da se svi elementi učitaju

        # Selektujemo sve članke mečeva
        match_articles = page.locator("article.match-item")
        total_matches = match_articles.count()

        for i in range(total_matches):
            article = match_articles.nth(i)
            
            # Datum meča
            date_text = article.locator(".match-day").text_content()
            if not date_text or not date_text.startswith(yesterday_str):
                continue  # preskoči sve koji nisu juče

            # FT status
            status = article.locator(".match-status").text_content()
            if status != "FT":
                continue  # samo završeni

            # Vreme
            time = article.locator(".match-time").text_content()

            # Timovi
            home = article.locator(".match-home").text_content()
            away = article.locator(".match-away").text_content()

            # Golovi
            ft_home = article.locator(".match-score-fullhome").text_content()
            ft_away = article.locator(".match-score-fullaway").text_content()
            ht_home = article.locator(".match-score-halfhome").text_content()
            ht_away = article.locator(".match-score-halfaway").text_content()

            if home and away and ft_home.isdigit() and ft_away.isdigit():
                results.append({
                    "Date": date_text.strip(),
                    "Time": time.strip(),
                    "Home": home.strip(),
                    "Away": away.strip(),
                    "FT": f"{ft_home}:{ft_away}",
                    "HT": f"{ht_home}:{ht_away}"
                })

        browser.close()

    return results


if __name__ == "__main__":
    matches = scrape_yesterday_finished()

    if matches:
        df = pd.DataFrame(matches)
        df.to_excel("mozzart_finished_yesterday.xlsx", index=False)
        print(f"ZAVRŠENI MEČEVI ({len(df)}) SAČUVANI.")
    else:
        print("Nema završenih mečeva za jučerašnji dan.")
