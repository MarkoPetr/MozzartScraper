from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta

def get_mozzart_url_previous_day():
    yesterday = datetime.now() - timedelta(days=1)
    date_str = yesterday.strftime("%Y-%m-%d")
    return f"https://www.mozzartbet.com/sr/rezultati?date={date_str}&events=finished"

def debug_extract_first_matches(num_matches=10):
    url = get_mozzart_url_previous_day()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # headless=False da vidimo stranicu ako treba
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_timeout(5000)  # čekanje JS

        # Dohvat svih div elemenata
        all_divs = page.locator("div")
        total_divs = all_divs.count()
        print(f"Ukupno div elemenata na stranici: {total_divs}\n")

        matches_found = 0
        for i in range(total_divs):
            txt = all_divs.nth(i).text_content().strip()
            if not txt:
                continue
            # filtriramo live i nebitne tekstove
            if txt.lower() in ["live", "uživo", "dodaj u favorite"]:
                continue

            print(f"[{i}] {txt}")

            # Broj prikazanih mečeva (grubo) po FT oznaci
            if "FT" in txt or ":" in txt:
                matches_found += 1
                print("--- KRAJ MEČA ---\n")
            if matches_found >= num_matches:
                break

        browser.close()

if __name__ == "__main__":
    debug_extract_first_matches()
