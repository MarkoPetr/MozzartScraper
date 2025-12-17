from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime, timedelta
import re
import time

URL = "https://www.mozzartbet.com/sr/rezultati"


def yesterday_prefix():
    return (datetime.now() - timedelta(days=1)).strftime("%d.%m.")


def scrape_yesterday_finished():
    results = []
    date_prefix = yesterday_prefix()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, timeout=60000)
        page.wait_for_timeout(5000)

        # 1️⃣ Klik "Završeni"
        page.locator("text=Završeni").first.click()
        page.wait_for_timeout(3000)

        # 2️⃣ Scroll da bi se učitali dani
        page.mouse.wheel(0, 3000)
        page.wait_for_timeout(3000)

        # 3️⃣ Pronađi JUČERAŠNJI DATUM (npr. "16.12. utorak")
        date_elements = page.locator(f"text=/^{date_prefix}.*$/")

        if date_elements.count() == 0:
            print("❌ Jučerašnji datum NIJE pronađen na stranici")
            browser.close()
            return []

        # klik na PRVI takav datum
        date_text = date_elements.first.text_content().strip()
        date_elements.first.click()
        page.wait_for_timeout(4000)

        print(f"✅ Otvoren datum: {date_text}")

        # 4️⃣ Parsiranje – samo Fudbal, samo FT
        nodes = page.locator("body *")
        total = nodes.count()

        def txt(i):
            try:
                return nodes.nth(i).text_content().strip()
            except:
                return ""

        i = 0
        # preskoči sve do "Fudbal"
        while i < total:
            if txt(i) == "Fudbal":
                i += 1
                break
            i += 1

        while i < total:
            t = txt(i)

            if re.match(r"\d{2}\.\d{2}\.", t):
                break  # sledeći dan

            if t == "FT":
                time_ = txt(i + 1)
                home = txt(i + 2)
                away = txt(i + 3)
                ft_h = txt(i + 4)
                ft_a = txt(i + 5)
                ht_h = txt(i + 6)
                ht_a = txt(i + 7)

                if home and away and ft_h.isdigit() and ft_a.isdigit():
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
