from playwright.sync_api import sync_playwright

URL = "https://www.mozzartbet.com/sr/rezultati"

def run_debug():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(URL, timeout=60000)
        page.wait_for_timeout(7000)

        # Klik na "Završeni" (ako postoji)
        try:
            page.locator("text=Završeni").first.click()
            page.wait_for_timeout(5000)
        except:
            print("⚠️ Dugme 'Završeni' nije kliknuto")

        # Screenshot cele stranice
        page.screenshot(path="debug_page.png", full_page=True)

        # Snimanje HTML-a
        html = page.content()
        with open("debug_page.html", "w", encoding="utf-8") as f:
            f.write(html)

        print("✅ DEBUG fajlovi sačuvani:")
        print(" - debug_page.png")
        print(" - debug_page.html")

        browser.close()


if __name__ == "__main__":
    run_debug()
