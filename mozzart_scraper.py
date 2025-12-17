from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime, timedelta
import re
import time

URL = "https://www.mozzartbet.com/sr/rezultati"

YESTERDAY_PREFIX = (datetime.now() - timedelta(days=1)).strftime("%d.%m.")

def scrape_yesterday_finished():
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, timeout=60000)
        page.wait_for_timeout(5000)

        # Cookies
        try:
            page.locator("text=Sačuvaj i zatvori").click(timeout=3000)
        except:
            pass

        # Završeni
        page.locator("text=Završeni").first.click()
        page.wait_for_timeout(3000)

        found = False
        active_date = ""

        for _ in range(12):
            # 🔎 tražimo JEDINI vidljiv datum formata 16.12. utorak
            dates = page.locator("text=/\\d{2}\\.\\d{2}\\.\\s/")

            if dates.count() == 0:
                print("❌ Datum nije pronađen u DOM-u")
                break

            active_date = dates.first.text_content().strip()
            print("DEBUG aktivni datum:", active_date)

            if active_date.startswith(YESTERDAY_PREFIX):
                print("✅ Jučerašnji datum pronađen")
                found = True
                break

            # ⬅ klik LEVU strelicu (SVG parent)
            arrows = page.locator("svg").filter(has_text="")
            arrows.first.click()
            page.wait_for_timeout(2000)

        if not found:
            print("❌ Jučerašnji datum NIJE pronađen")
            browser.close()
            return []

        # ⬇ Parsiranje fudbala
        body = page.locator("body *")
        total = body.count()

        def t(i):
            try:
                return body.nth(i).text_content().strip()
            except:
                return ""

        i = 0
        while i < total:
            if t(i) == "Fudbal":
                i += 1
                break
            i += 1

        while i < total:
            if re.match(r"\d{2}\.\d{2}\.", t(i)):
                break

            if t(i) == "FT":
                try:
                    results.append({
                        "Date": active_date,
                        "Time": t(i+1),
                        "Home": t(i+2),
                        "Away": t(i+3),
                        "FT": f"{t(i+4)}:{t(i+5)}",
                        "HT": f"{t(i+6)}:{t(i+7)}"
                    })
                except:
                    pass
                i += 7
            i += 1

        browser.close()

    return results


if __name__ == "__main__":
    matches = scrape_yesterday_finished()

    if matches:
        df = pd.DataFrame(matches)
        df.to_excel("mozzart_finished_yesterday.xlsx", index=False)
        print(f"✅ Sačuvano {len(df)} mečeva")
    else:
        print("❌ Nema završenih fudbalskih mečeva")
