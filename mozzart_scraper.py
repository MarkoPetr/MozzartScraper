from playwright.sync_api import sync_playwright
import time

URL = "https://www.mozzartbet.com/sr/rezultati/Fudbal/1?date=2025-12-17&events=finished"

def scrape_first_5_matches():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # headless zbog servera/Actions
        page = browser.new_page()
        page.goto(URL, timeout=60000)

        # čekamo da se AJAX sadržaj učita
        page.wait_for_timeout(8000)

        # dohvat celog tela stranice
        body_text = page.locator("body").inner_text()
        print("===== CELO BODY TEXT =====")
        print(body_text[:5000])  # ispis prvih 5000 karaktera, dovoljno da vidimo strukturu

        # pokušaj da dohvatimo prve 5 završenih mečeva po HTML elementima
        matches_elements = page.locator("div.match-row")  # primer selektora, proverićemo sa outputom
        count = min(matches_elements.count(), 5)

        print("\n===== PRVIH 5 MEČEVA =====")
        for i in range(count):
            match = matches_elements.nth(i)
            try:
                print("----- MEČ", i+1, "-----")
                print(match.inner_text())  # ispisuje sve što je u tom div-u
            except Exception as e:
                print("⚠️ Greška pri dohvaćanju meča:", e)

        browser.close()

if __name__ == "__main__":
    scrape_first_5_matches()
