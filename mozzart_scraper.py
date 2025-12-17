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
    target_prefix = yesterday_prefix()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, timeout=60000)
        page.wait_for_timeout(5000)

        # Cookie
        try:
            page.locator("text=Sačuvaj i zatvori").click(timeout=3000)
        except:
            pass

        # Završeni
        page.locator("text=Završeni").first.click()
        page.wait_for_timeout(3000)

        # 🔁 HORIZONTALNI KARUSEL – klik strelicu LEVO dok ne dođemo do juče
        for _ in range(10):
            active_date = page.locator(
                "[class*=active], [class*=selected]"
            ).first.text_content().strip()

            print(f"DEBUG aktivni datum: {active_date}")

            if active_date.startswith(target_prefix):
                print("✅ Pronađen jučerašnji datum")
                break

            # klik strelicu levo
            page.locator("button:has-text('‹'), button:has-text('<')").first.click()
            page.wait_for_timeout(2000)
        else:
            print("❌ Jučerašnji datum nije pronađen u karuselu")
            browser.close()
            return []

        # ⬇ Parsiranje
        nodes = page.locator("body *")
        total = nodes.count()

        def txt(i):
            try:
                return nodes.nth(i).text_content().strip()
            except:
                return ""

        i = 0
        while i < total:
            if txt(i) == "Fudbal":
                i += 1
                break
            i += 1

        while i < total:
            t = txt(i)

            if re.match(r"\d{2}\.\d{2}\.", t):
                break

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
                        "Date": active_date,
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
