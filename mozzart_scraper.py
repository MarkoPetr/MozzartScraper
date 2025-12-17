from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime, timedelta
import re

URL = "https://www.mozzartbet.com/sr/rezultati?events=finished"

def scrape_yesterday_finished():
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%d.%m.")
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, timeout=60000)
        page.wait_for_timeout(5000)

        nodes = page.locator("body *")
        count = nodes.count()

        in_yesterday = False
        i = 0

        while i < count:
            text = nodes.nth(i).inner_text().strip()

            # DETEKTUJ DATUM
            if re.match(r"\d{2}\.\d{2}\.", text):
                if text.startswith(yesterday):
                    in_yesterday = True
                elif in_yesterday:
                    break  # izašli smo iz jučerašnjeg dana

            # PARSIRAJ SAMO JUČERAŠNJE FT MEČEVE
            if in_yesterday and text == "FT":
                try:
                    time = nodes.nth(i+1).inner_text().strip()
                    home = nodes.nth(i+2).inner_text().strip()
                    away = nodes.nth(i+3).inner_text().strip()

                    ft_home = nodes.nth(i+4).inner_text().strip()
                    ft_away = nodes.nth(i+5).inner_text().strip()
                    ht_home = nodes.nth(i+6).inner_text().strip()
                    ht_away = nodes.nth(i+7).inner_text().strip()

                    results.append({
                        "Home": home,
                        "Away": away,
                        "FT": f"{ft_home}:{ft_away}",
                        "HT": f"{ht_home}:{ht_away}",
                        "Time": time
                    })

                    i += 7
                except:
                    pass

            i += 1

        browser.close()

    return results


if __name__ == "__main__":
    matches = scrape_yesterday_finished()

    if matches:
        df = pd.DataFrame(matches)
        df.to_excel("mozzart_yesterday_finished.xlsx", index=False)
        print(f"JUČERAŠNJI MEČEVI: {len(df)} upisano u mozzart_yesterday_finished.xlsx")
    else:
        print("Nema jučerašnjih završenih mečeva.")
