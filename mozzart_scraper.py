from playwright.sync_api import sync_playwright
import pandas as pd
import os
import time
import random

OUTPUT_DIR = "output"

MOBILE_UA = (
    "Mozilla/5.0 (Linux; Android 13; SM-A166B) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Mobile Safari/537.36"
)

def human_sleep(min_sec=5, max_sec=10):
    time.sleep(random.uniform(min_sec, max_sec))

def scrape_text(date_str):
    url = f"https://www.mozzartbet.com/sr/rezultati/Fudbal/1?date={date_str}&events=finished"
    print(f"🌐 Otvaram: {url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=MOBILE_UA,
            viewport={"width": 412, "height": 915},
            locale="sr-RS"
        )
        page = context.new_page()
        page.goto(url, timeout=60000)
        human_sleep(6, 9)

        # cookies popup    
        try:    
            page.click("text=Sačuvaj i zatvori", timeout=5000)    
            human_sleep(2, 4)    
        except:    
            pass    

        # učitaj sve mečeve    
        while True:    
            try:    
                page.evaluate("window.scrollBy(0, 600)")    
                human_sleep(1, 2)    
                page.click("text=Učitaj još", timeout=3000)    
                human_sleep(4, 8)    
            except:    
                break    

        text = page.inner_text("body")    
        browser.close()    
        return text

def parse_matches(text, date_str):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    matches = []
    current_league = ""
    i = 0

    while i < len(lines):
        if not lines[i].isdigit() and "FT" not in lines[i] and ":" not in lines[i]:
            current_league = lines[i]
            i += 1
            if i < len(lines) and lines[i].isdigit():
                i += 1
            continue

        if lines[i] == "FT":    
            try:    
                time_m = lines[i + 1]    
                home = lines[i + 2]    
                away = lines[i + 3]    
                ft_home = int(lines[i + 4])    
                ft_away = int(lines[i + 5])    
                ht_home = int(lines[i + 6])    
                ht_away = int(lines[i + 7])    

                sh_home = ft_home - ht_home    
                sh_away = ft_away - ht_away    

                matches.append({    
                    "Datum": date_str,    
                    "Time": time_m,    
                    "Liga": current_league,    
                    "Home": home,    
                    "Away": away,    
                    "FT": f"{ft_home}:{ft_away}",    
                    "HT": f"{ht_home}:{ht_away}",    
                    "SH": f"{sh_home}:{sh_away}",    
                })    
            except:    
                pass    

            i += 8    
        else:    
            i += 1

    return matches

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # ✅ FIXIRANI DATUM
    date_str = "2026-02-20"

    print(f"\n📅 Skidam podatke za: {date_str}")

    text = scrape_text(date_str)
    matches = parse_matches(text, date_str)

    print(f"   ➜ pronađeno {len(matches)} mečeva")

    if not matches:
        print("❌ Nije pronađen nijedan meč!")
        return

    df = pd.DataFrame(matches)

    output_file = os.path.join(
        OUTPUT_DIR,
        f"mozzart_results_{date_str}.xlsx"
    )

    df.to_excel(output_file, index=False)

    print("\n✅ GOTOVO!")
    print(f"📊 Ukupno mečeva: {len(df)}")
    print(f"📁 Sačuvano u: {output_file}")

if __name__ == "__main__":
    main()
