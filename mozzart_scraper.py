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

        html = page.content()
        print(html[:5000])  # ispisujemo samo prvih 5000 karaktera

        browser.close()

if __name__ == "__main__":
    main()
