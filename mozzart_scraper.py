from playwright.sync_api import sync_playwright

MOZZART_URL = "https://www.mozzartbet.com/sr/rezultati?events=finished"

def inspect_match_blocks():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(MOZZART_URL, timeout=60000)
        page.wait_for_timeout(5000)  # čekamo JS učitavanje

        # Probaj da uhvatimo sve blokove mečeva
        match_blocks = page.locator("div")  # generalno uzimamo sve div-ove, kasnije ćemo filtrirati
        count = match_blocks.count()
        print(f"Pronađeno ukupno div-ova na stranici: {count}")

        # Iteriramo prvih 20 div-ova za pregled
        for i in range(min(count, 20)):
            block = match_blocks.nth(i)
            print(f"\n=== BLOCK {i} ===")
            # Ispisujemo sve direktne decu elemente
            children = block.locator("*")
            children_count = children.count()
            print(f"Broj child elemenata: {children_count}")
            for j in range(children_count):
                child = children.nth(j)
                tag = child.evaluate("el => el.tagName")
                class_name = child.get_attribute("class")
                text = child.text_content().strip()
                if text:  # prikazujemo samo elemente sa tekstom
                    print(f"{tag} | class='{class_name}' | text='{text}'")

        browser.close()

if __name__ == "__main__":
    inspect_match_blocks()
