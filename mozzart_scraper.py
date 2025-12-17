from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime, timedelta
import re

URL = "https://www.mozzartbet.com/sr/rezultati?events=finished"

def scrape_yesterday_finished():
    results = []

    # jučerašnji datum u formatu 'dd.mm.'
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%d.%m.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, timeout=60000)
        page.wait_for_timeout(5000)

        # uzimamo sve tekstove
        nodes = page.locator("body *")
        total = nodes.count()

        def safe_text(i):
            try:
                t = nodes.nth(i).text_content()
                return t.strip() if t else ""
            except:
                return ""

        i = 0
        in_target_day = False

        while i < total:
            text = safe_text(i)

            # pronalazimo jučerašnji datum
            if re.match(r"\d{2}\.\d{2}\.", text):
                if text.startswith(yesterday):
                    in_target_day = True
                else:
                    if in_target_day:
                        break  # izašli smo iz jučerašnjeg dana
                    in_target_day = False

            # završeni mečevi
            if in_target_day and text == "FT":
                time = safe_text(i + 1)
                home = safe_text(i + 2)
                away = safe_text(i + 3)
                ft_home = safe_text(i + 4)
                ft_away = safe_text(i + 5)
                ht_home = safe_text(i + 6)
                ht_away = safe_text(i + 7)

                if all(x.isdigit() for x in [ft_home, ft_away, ht_home, ht_away]):
                    results.append({
                        "Date": yesterday,
                        "Time": time,
                        "Home": home,
                        "Away": away,
                        "FT": f"{ft_home}:{ft_away}",
                        "HT": f"{ht_home}:{ht_away}"
                    })
                i += 7
            i += 1

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
