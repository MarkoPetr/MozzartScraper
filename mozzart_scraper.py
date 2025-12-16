from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(
            "https://www.mozzartbet.com/sr/rezultati?events=finished",
            timeout=60000
        )

        # ČEKAMO da se pojavi BILO KOJI rezultat tipa 1:0, 2:1 itd
        page.wait_for_selector("text=:", timeout=60000)

        # Uzmi prvi element koji sadrži :
        score_element = page.locator("text=:").first
        score_text = score_element.inner_text()

        print("PRONAĐEN REZULTAT:", score_text)

        browser.close()

if __name__ == "__main__":
    main()
