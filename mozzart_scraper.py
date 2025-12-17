from playwright.sync_api import sync_playwright
import pandas as pd
import time

URL = "https://www.mozzartbet.com/sr/rezultati?events=finished"

OUTPUT_FILE = "mozzart_finished_yesterday.xlsx"


def scrape_yesterday_finished():
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, timeout=60000)

        # čekamo da se stranica stabilizuje
        page.wait_for_timeout(6000)

        # klik na TAB "Završeni" (ako već nije aktivan)
        try:
            page.locator("text=Završeni").first.click()
            page.wait_for_timeout(3000)
        except:
            pass

        # klik LEVO – jučerašnji datum (strelica)
        try:
            page.locator("button", has_text="‹").first.click()
        except:
            try:
                page.locator("button", has_text="<").first.click()
            except:
                pass

        page.wait_for_timeout(4000)

        # samo FUDBAL
        try:
            page.locator("text=Fudbal").first.click()
            page.wait_for_timeout(3000)
        except:
            pass

        # uzimamo tekst cele stranice
        body_text = page.locator("body").inner_text()

        lines = [l.strip() for l in body_text.splitlines() if l.strip()]

        i = 0
        while i < len(lines) - 6:
            if lines[i] == "FT":
                try:
                    time_match = lines[i - 1]
                    home = lines[i + 1]
                    away = lines[i + 2]
                    ft = lines[i + 3]

                    if ":" in ft:
                        results.append({
                            "Time": time_match,
                            "Home": home,
                            "Away": away,
                            "FT": ft
                        })
                except:
                    pass
            i += 1

        browser.close()

    return results


if __name__ == "__main__":
    matches = scrape_yesterday_finished()

    df = pd.DataFrame(matches)
    df.to_excel(OUTPUT_FILE, index=False)

    if matches:
        print(f"✅ Sačuvano {len(df)} završenih fudbalskih mečeva")
    else:
        print("⚠️ Nema završenih fudbalskih mečeva za jučerašnji dan")
