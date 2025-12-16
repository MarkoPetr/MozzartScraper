from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(
            "https://www.mozzartbet.com/sr/rezultati?events=finished",
            timeout=60000
        )

        page.wait_for_timeout(3000)

        match = page.locator("div.match-row").first

        home = match.locator(".home-team").inner_text()
        away = match.locator(".away-team").inner_text()
        score = match.locator(".final-score").inner_text()

        print("DOMACIN:", home)
        print("GOST:", away)
        print("REZULTAT:", score)

        browser.close()

if __name__ == "__main__":
    main()
