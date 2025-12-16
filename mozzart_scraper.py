from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta

OUTPUT_FILE = "debug_matches.txt"

def get_mozzart_url_previous_day():
    yesterday = datetime.now() - timedelta(days=1)
    date_str = yesterday.strftime("%Y-%m-%d")
    return f"https://www.mozzartbet.com/sr/rezultati?date={date_str}&events=finished"

def debug_extract_first_matches(num_matches=10):
    url = get_mozzart_url_previous_day()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # headless za Actions / server
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_timeout(5000)  # čekanje učitavanja JS

        all_divs = page.locator("div, span")
        total_divs = all_divs.count()
        print(f"Ukupno div/span elemenata na stranici: {total_divs}\n")

        matches_found = 0
        debug_lines = []

        for i in range(total_divs):
            txt = all_divs.nth(i).text_content().strip()
            if not txt:
                continue
            # filtriramo očigledno nebitne tekstove
            if txt.lower() in ["live", "uživo", "dodaj u favorite"]:
                continue

            debug_lines.append(f"[{i}] {txt}")

            # Grubo računanje broja mečeva po FT ili ":" oznaci
            if "FT" in txt or ":" in txt:
                matches_found += 1
                debug_lines.append("--- KRAJ MEČA ---\n")
            if matches_found >= num_matches:
                break

        browser.close()

    # Upis u fajl radi lakšeg pregleda
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for line in debug_lines:
            f.write(line + "\n")

    print(f"Debug tekst prvih {matches_found} mečeva sačuvan u {OUTPUT_FILE}")

if __name__ == "__main__":
    debug_extract_first_matches()
