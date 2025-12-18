from playwright.sync_api import sync_playwright
import time
import os
import random
import pandas as pd
import re

URL = "https://www.mozzartbet.com/sr/rezultati/Fudbal/1?date=2025-12-17&events=finished"

MOBILE_UA = (
    "Mozilla/5.0 (Linux; Android 13; SM-A166B) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Mobile Safari/537.36"
)

OUTPUT_DIR = "output"
EXCEL_FILE = "output/mozzart_184_matches.xlsx"


def scrape_text():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=MOBILE_UA,
            viewport={"width": 412, "height": 915},
            locale="sr-RS",
        )
        page = context.new_page()

        page.goto(URL, timeout=60000)
        page.wait_for_timeout(7000)

        try:
            page.click("text=Sačuvaj i zatvori", timeout=5000)
            page.wait_for_timeout(3000)
        except:
            pass

        last_count = 0

        for _ in range(30):
            page.mouse.wheel(0, random.randint(400, 700))
            page.wait_for_timeout(random.randint(1200, 2000))

            try:
                page.click("text=Učitaj još", timeout=3000)
            except:
                pass

            page.wait_for_timeout(random.randint(6000, 9000))

            count = page.evaluate("""
                () => document.body.innerText.split('\\n').filter(x => x.trim() === 'FT').length
            """)

            if count <= last_count:
                break
            last_count = count

        text = page.inner_text("body")
        browser.close()

    return text


def parse_matches(text):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    matches = []

    i = 0
    while i < len(lines):
        if lines[i] == "FT":
            try:
                time_m = lines[i - 1]
                home = lines[i + 1]
                away = lines[i + 2]

                # tražimo dva reda sa po dva broja
                scores = []
                j = i + 3
                while j < len(lines) and len(scores) < 2:
                    nums = re.findall(r"\b\d+\b", lines[j])
                    if len(nums) == 2:
                        scores.append((int(nums[0]), int(nums[1])))
                    j += 1

                if len(scores) != 2:
                    i += 1
                    continue

                ft_home, ft_away = scores[0]
                ht_home, ht_away = scores[1]

                sh_home = ft_home - ht_home
                sh_away = ft_away - ht_away

                matches.append({
                    "Time": time_m,
                    "Home": home,
                    "Away": away,
                    "FT": f"{ft_home}:{ft_away}",
                    "HT": f"{ht_home}:{ht_away}",
                    "SH": f"{sh_home}:{sh_away}",
                })

            except:
                pass
        i += 1

    return matches


def main():
    print("📱 Preuzimam stranicu...")
    text = scrape_text()

    print("🧠 Parsiram mečeve...")
    matches = parse_matches(text)

    df = pd.DataFrame(matches)
    df.to_excel(EXCEL_FILE, index=False)

    print(f"✅ Sačuvano {len(df)} mečeva u {EXCEL_FILE}")


if __name__ == "__main__":
    main()
