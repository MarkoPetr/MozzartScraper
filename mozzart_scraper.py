from playwright.sync_api import sync_playwright
import pandas as pd
import re

URL = "https://www.mozzartbet.com/sr/rezultati?events=finished"


def safe_int(val):
    """Pretvara tekst u int, vraća 0 ako nije moguće."""
    try:
        return int(re.sub(r"\D", "", val))
    except:
        return 0


def scrape_finished_days(days=2):
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, timeout=60000)
        page.wait_for_timeout(5000)

        nodes = page.locator("body *")
        total = nodes.count()

        def safe_text(i):
            try:
                t = nodes.nth(i).text_content()
                return t.strip() if t else ""
            except:
                return ""

        in_target_day = False
        target_date = None
        day_count = 0
        i = 0

        while i < total and day_count < days:
            text = safe_text(i)

            # Datum npr. "16.12. utorak"
            if re.match(r"\d{2}\.\d{2}\.", text):
                if not in_target_day:
                    in_target_day = True
                    target_date = text
                    day_count += 1
                else:
                    in_target_day = True
                    target_date = text
                    day_count += 1

            # Završeni mečevi FT
            if in_target_day and text == "FT":
                time = safe_text(i + 1)
                home = safe_text(i + 2)
                away = safe_text(i + 3)

                ft_home = safe_int(safe_text(i + 4))
                ft_away = safe_int(safe_text(i + 5))
                ht_home = safe_int(safe_text(i + 6))
                ht_away = safe_int(safe_text(i + 7))

                if home and away:
                    results.append({
                        "Date": target_date,
                        "Time": time,
                        "Home": home,
                        "Away": away,
                        "FT": f"{ft_home}:{ft_away}",
                        "HT": f"{ht_home}:{ht_away}"
                    })

                i += 7  # preskakanje parsiranih nodova

            i += 1

        browser.close()

    return results


if __name__ == "__main__":
    matches = scrape_finished_days(days=2)

    if matches:
        df = pd.DataFrame(matches)
        df.to_excel("mozzart_finished_last_days.xlsx", index=False)
        print(f"ZAVRŠENI MEČEVI ({len(df)}) SAČUVANI.")
    else:
        print("Nema završenih mečeva.")
