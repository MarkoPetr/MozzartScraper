from playwright.sync_api import sync_playwright
import time
import os
import random

URL = "https://www.mozzartbet.com/sr/rezultati/Fudbal/1?date=2025-12-17&events=finished"

MOBILE_UA = (
    "Mozilla/5.0 (Linux; Android 13; SM-A166B) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Mobile Safari/537.36"
)

def run():
    os.makedirs("output", exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=MOBILE_UA,
            viewport={"width": 412, "height": 915},  # real Android rezolucija
            locale="sr-RS",
        )
        page = context.new_page()

        print("📱 Otvaram Mozzart kao ANDROID browser...")
        page.goto(URL, timeout=60000)
        page.wait_for_timeout(7000)

        # cookie popup
        try:
            page.click("text=Sačuvaj i zatvori", timeout=5000)
            print("🍪 Cookie popup zatvoren")
            page.wait_for_timeout(3000)
        except:
            pass

        last_count = 0

        for cycle in range(1, 25):
            print(f"\n🔄 CIKLUS {cycle}")

            # mali scroll (kao prst)
            for _ in range(4):
                page.mouse.wheel(0, random.randint(400, 700))
                page.wait_for_timeout(random.randint(1200, 2000))

            # klik "Učitaj još" ako postoji
            clicked = False
            try:
                page.click("text=Učitaj još", timeout=4000)
                clicked = True
                print("➕ Klik na 'Učitaj još'")
            except:
                print("ℹ️ Dugme 'Učitaj još' nije dostupno")

            wait_time = random.randint(6000, 9000)
            print(f"⏳ Čekam {wait_time/1000:.1f}s da backend učita...")
            page.wait_for_timeout(wait_time)

            # brojimo FT (završene mečeve)
            count = page.evaluate("""
                () => document.body.innerText.split('\\n').filter(x => x.trim() === 'FT').length
            """)

            print(f"📊 Trenutno učitano mečeva: {count}")

            if count <= last_count:
                print("🛑 Nema novih mečeva — backend stao")
                break

            last_count = count

        print("\n📸 Snimam kompletan prikaz...")
        page.screenshot(path="output/full_page.png", full_page=True)

        print("💾 Snimam HTML...")
        with open("output/page.html", "w", encoding="utf-8") as f:
            f.write(page.content())

        print("📝 Snimam sav vidljiv tekst...")
        with open("output/page.txt", "w", encoding="utf-8") as f:
            f.write(page.inner_text("body"))

        browser.close()

    print("\n✅ GOTOVO — mobile + sporo scrape završen")

if __name__ == "__main__":
    run()
