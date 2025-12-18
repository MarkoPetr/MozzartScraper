from playwright.sync_api import sync_playwright
import time

URL = "https://www.mozzartbet.com/sr/rezultati/Fudbal/1?date=2025-12-17&events=finished"

def scrape_first_5_matches():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # headless=False da možeš videti šta se dešava
        page = browser.new_page()
        page.goto(URL, timeout=60000)

        # čekamo da se svi mečevi učitaju
        page.wait_for_timeout(8000)

        # dohvat celog tela stranice
        body_html = page.locator("body").inner_html()
        body_text = page.locator("body").inner_text()

        print("===== CELO BODY INNER_HTML =====")
        print(body_html[:5000])  # ispis prvih 5000 karaktera HTML-a
        print("\n===== CELO BODY INNER_TEXT =====")
        print(body_text[:3000])  # ispis prvih 3000 karaktera teksta

        # pokušaj da dohvatimo prve 5 završenih mečeva
        matches_elements = page.locator("div.match-row")  # proveri tačan selektor
        count = min(matches_elements.count(), 5)

        print("\n===== PRVIH 5 MEČEVA =====")
        for i in range(count):
            match = matches_elements.nth(i)
            try:
                print("----- MEČ", i+1, "-----")
                print(match.inner_text())
            except Exception as e:
                print("⚠️ Greška pri dohvaćanju meča:", e)

        browser.close()

if __name__ == "__main__":
    scrape_first_5_matches()
