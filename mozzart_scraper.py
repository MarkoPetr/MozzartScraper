from playwright.sync_api import sync_playwright
import time

URL = "https://www.mozzartbet.com/sr/rezultati/Fudbal/1?date=2025-12-17&events=finished"

def debug_page_bottom():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(URL, timeout=60000)
        page.wait_for_timeout(8000)

        # Skroluj do dna
        last_height = 0
        for _ in range(10):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2)
            height = page.evaluate("document.body.scrollHeight")
            if height == last_height:
                break
            last_height = height

        print("\n===== VIDLJIV TEKST NA DNU STRANICE =====\n")
        text = page.evaluate("""
            () => {
                const body = document.body.innerText;
                return body.slice(body.length - 3000);
            }
        """)
        print(text)

        print("\n===== BUTTON ELEMENTI =====\n")
        buttons = page.query_selector_all("button")
        for i, b in enumerate(buttons):
            try:
                print(f"[{i}] TEXT:", b.inner_text())
            except:
                pass

        print("\n===== ELEMENTI KOJI SADRŽE 'ucitaj / jos / more' =====\n")
        matches = page.evaluate("""
            () => {
                const keywords = ['ucitaj', 'učitaj', 'još', 'jos', 'more', 'load'];
                const found = [];
                document.querySelectorAll('*').forEach(el => {
                    const t = el.innerText?.toLowerCase();
                    if (t && keywords.some(k => t.includes(k))) {
                        found.push({
                            tag: el.tagName,
                            text: el.innerText,
                            disabled: el.disabled || false
                        });
                    }
                });
                return found;
            }
        """)
        for m in matches:
            print(m)

        browser.close()

if __name__ == "__main__":
    debug_page_bottom()
