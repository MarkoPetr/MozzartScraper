from playwright.sync_api import sync_playwright
import time

URL = "https://www.mozzartbet.com/sr/rezultati/Fudbal/1?date=2025-12-17&events=finished"

def click_load_more():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, timeout=60000)
        time.sleep(5)

        # skrol do dna
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2)

        # pokušaj da klikne dugme koje sadrži 'Učitaj'
        try:
            load_button = page.locator("text=Učitaj")
            if load_button.count() > 0:
                print(f"⚡ Dugme pronađeno, klikću...")
                load_button.first.click()
                time.sleep(3)
                print("✅ Klik izvršen")
            else:
                print("⚠️ Dugme 'Učitaj još' nije pronađeno")
        except Exception as e:
            print("⚠️ Greška pri kliku:", e)

        # ispiši poslednjih 500 karaktera DOM teksta
        body_text = page.evaluate("document.body.innerText")
        print("\n===== TEKST NA DNU STRANICE POSLE KLIKA =====\n")
        print(body_text[-500:])

        browser.close()

if __name__ == "__main__":
    click_load_more()
