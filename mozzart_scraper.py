from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime, timedelta
import re
import time

URL = "https://www.mozzartbet.com/sr/rezultati"


def get_yesterday_label():
    yesterday = datetime.now() - timedelta(days=1)
    return yesterday.strftime("%d.%m.")


def scrape_yesterday_finished():
    results = []
    date_prefix = get_yesterday_label()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, timeout=60000)
        page.wait_for_timeout(5000)

        # Klik na "Završeni"
        page.locator("text=Završeni").first.click()
        page.wait_for_timeout(3000)

        # Klik na jučerašnji datum (npr. "16.12. utorak")
        date_locator = page.locator(
            f"xpath=//text()[contains(., '{date_prefix}')]"
        ).first

        if not date_locator.count():
            print("❌ Jučerašnji datum nije pronađen")
            browser.close()
            return []

        date_text = date_locator.text_content().strip()
        date_locator.click()
        page.wait_for_timeout(4000)

        # Uzmi samo Fudbal sekciju
        body = page.locator("body *")
        total = body.count()

        def safe(i):
            try:
                return body.nth(i).text_content().strip()
            except:
                return ""

        i = 0
        while i < total:
            text = safe(i)

            # preskačemo sve dok ne naiđemo na "Fudbal"
            if text == "Fudbal":
                i += 1
                break
            i += 1

        while i < total:
            text = safe(i)

            if re.match(r"\d{2}\.\d{2}\.", text):
                break  # sledeći dan → STOP

            if text == "FT":
                time_ = safe(i + 1)
                home = safe(i + 2)
                away = safe(i + 3)

                ft_h = safe(i + 4)
                ft_a = safe(i + 5)
                ht_h = safe(i + 6)
                ht_a = safe(i + 7)

                if (
                    home and away
                    and ft_h.isdigit()
                    and ft_a.isdigit()
                ):
                    results.append({
                        "Date": date_text,
                        "Time": time_,
                        "Home": home,
                        "Away": away,
                        "FT": f"{ft_h}:{ft_a}",
                        "HT": f"{ht_h}:{ht_a}" if ht_h.isdigit() and ht_a.isdigit() else ""
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
        print(f"✅ Sačuvano {len(df)} fudbalskih mečeva.")
    else:
        print("❌ Nema završenih fudbalskih mečeva za jučerašnji dan.")
