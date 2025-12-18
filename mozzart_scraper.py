from playwright.sync_api import sync_playwright
import time
import os

URL = "https://www.mozzartbet.com/sr/rezultati/Fudbal/1?date=2025-12-17&events=finished"

def run():
    os.makedirs("output", exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 800})

        print("➡️ Otvaram stranicu...")
        page.goto(URL, timeout=60000)
        page.wait_for_timeout(5000)

        # prihvati cookies ako postoji
        try:
            page.click("text=Sačuvaj i zatvori", timeout=5000)
            print("🍪 Cookie popup zatvoren")
        except:
            pass

        last_height = 0

        for i in range(20):
            print(f"🔽 Skrol iteracija {i+1}")
            page.mouse.wheel(0, 5000)
            page.wait_for_timeout(3000)

            # klik na "Učitaj još" ako postoji
            try:
                page.click("text=Učitaj još", timeout=3000)
                print("➕ Klik na 'Učitaj još'")
                page.wait_for_timeout(4000)
            except:
                print("ℹ️ Nema dugmeta 'Učitaj još'")

            height = page.evaluate("document.body.scrollHeight")
            if height == last_height:
                print("🛑 Nema više novog sadržaja")
                break
            last_height = height

        print("📸 Pravim screenshot...")
        page.screenshot(path="output/full_page.png", full_page=True)

        print("💾 Snimam HTML...")
        html = page.content()
        with open("output/page.html", "w", encoding="utf-8") as f:
            f.write(html)

        print("📝 Snimam vidljiv tekst...")
        text = page.inner_text("body")
        with open("output/page.txt", "w", encoding="utf-8") as f:
            f.write(text)

        browser.close()

    print("✅ GOTOVO – svi fajlovi snimljeni u /output")

if __name__ == "__main__":
    run()
