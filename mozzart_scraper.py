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
        total = nodes.count()

        in_yesterday = False
        i = 0

        def safe_text(idx):
            try:
                t = nodes.nth(idx).text_content()
                return t.strip() if t else ""
            except:
                return ""

        while i < total:
            text = safe_text(i)

            # DETEKCIJA DATUMA (npr. "16.12.")
            if re.match(r"\d{2}\.\d{2}\.", text):
                if text.startswith(yesterday):
                    in_yesterday = True
                elif in_yesterday:
                    break  # izlazak iz jučerašnjeg bloka

            # PARSIRANJE ZAVRŠENIH MEČEVA
            if in_yesterday and text == "FT":
                time = safe_text(i + 1)
                home = safe_text(i + 2)
                away = safe_text(i + 3)

                ft_home = safe_text(i + 4)
                ft_away = safe_text(i + 5)
                ht_home = safe_text(i + 6)
                ht_away = safe_text(i + 7)

                # VALIDACIJA (da ne uleti liga ili glup tekst)
                if (
                    home
                    and away
                    and ft_home.isdigit()
                    and ft_away.isdigit()
                    and ht_home.isdigit()
                    and ht_away.isdigit()
                ):
                    results.append({
                        "Home": home,
                        "Away": away,
                        "FT": f"{ft_home}:{ft_away}",
                        "HT": f"{ht_home}:{ht_away}",
                        "Time": time,
                        "Date": yesterday
                    })

                i += 7

            i += 1

        browser.close()

    return results


if __name__ == "__main__":
    matches = scrape_yesterday_finished()

    if matches:
        df = pd.DataFrame(matches)
        df.to_excel("mozzart_yesterday_finished.xlsx", index=False)
        print(f"JUČERAŠNJI ZAVRŠENI MEČEVI: {len(df)}")
    else:
        print("Nema jučerašnjih završenih mečeva.")
