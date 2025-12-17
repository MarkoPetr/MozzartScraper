from playwright.sync_api import sync_playwright
import pandas as pd
import re

URL = "https://www.mozzartbet.com/sr/rezultati?events=finished"


def scrape_first_finished_day():
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
        i = 0

        while i < total:
            text = safe_text(i)

            # PRVI DATUM (npr. "16.12. utorak")
            if re.match(r"\d{2}\.\d{2}\.", text):
                if not in_target_day:
                    in_target_day = True
                    target_date = text
                else:
                    break  # sledeći dan → STOP

            # SAMO ZAVRŠENI MEČEVI
            if in_target_day and text == "FT":
                time = safe_text(i + 1)
                home = safe_text(i + 2)
                away = safe_text(i + 3)

                ft_home = safe_text(i + 4)
                ft_away = safe_text(i + 5)
                ht_home = safe_text(i + 6)
                ht_away = safe_text(i + 7)

                if (
                    home
                    and away
                    and ft_home.isdigit()
                    and ft_away.isdigit()
                    and ht_home.isdigit()
                    and ht_away.isdigit()
                ):
                    results.append({
                        "Date": target_date,
                        "Home": home,
                        "Away": away,
                        "FT": f"{ft_home}:{ft_away}",
                        "HT": f"{ht_home}:{ht_away}",
                        "Time": time
                    })

                i += 7

            i += 1

        browser.close()

    return results


if __name__ == "__main__":
    matches = scrape_first_finished_day()

    if matches:
        df = pd.DataFrame(matches)
        df.to_excel("mozzart_finished_last_day.xlsx", index=False)
        print(f"ZAVRŠENI MEČEVI ({len(df)}) SAČUVANI.")
    else:
        print("Nema završenih mečeva.")
