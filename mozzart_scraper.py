import requests
import pandas as pd
import os
from datetime import datetime, timedelta

OUTPUT_DIR = "output"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13; SM-A166B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
}

def fetch_matches(date_str):
    url = f"https://api.sofascore.com/api/v1/sport/football/scheduled-events/{date_str}"
    print(f"🌐 Skidam: {url}")

    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()

    data = r.json()
    return data.get("events", [])

def parse_matches(events, date_str):
    matches = []

    for ev in events:
        try:
            home = ev["homeTeam"]["name"]
            away = ev["awayTeam"]["name"]

            league = ev["tournament"]["name"]
            country = ev["tournament"]["category"]["name"]

            score = ev.get("score", {})
            ft_home = score.get("current", {}).get("home")
            ft_away = score.get("current", {}).get("away")

            ht_home = score.get("period1", {}).get("home")
            ht_away = score.get("period1", {}).get("away")

            status = ev.get("status", {}).get("description", "")

            # samo završene utakmice
            if status.lower() != "ended":
                continue

            matches.append({
                "Datum": date_str,
                "Država": country,
                "Liga": league,
                "Home": home,
                "Away": away,
                "FT": f"{ft_home}:{ft_away}" if ft_home is not None else "",
                "HT": f"{ht_home}:{ht_away}" if ht_home is not None else "",
            })

        except Exception:
            continue

    return matches

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # ✅ UVEK UZIMA JUČERAŠNJI DATUM
    yesterday = datetime.now() - timedelta(days=1)
    date_str = yesterday.strftime("%Y-%m-%d")

    print(f"\n📅 Skidam SofaScore podatke za: {date_str}")

    events = fetch_matches(date_str)
    print(f"   ➜ ukupno događaja: {len(events)}")

    matches = parse_matches(events, date_str)

    print(f"   ➜ završenih mečeva: {len(matches)}")

    if not matches:
        print("❌ Nije pronađen nijedan završen meč!")
        return

    df = pd.DataFrame(matches)

    output_file = os.path.join(
        OUTPUT_DIR,
        f"sofascore_results_{date_str}.xlsx"
    )

    df.to_excel(output_file, index=False)

    print("\n✅ GOTOVO!")
    print(f"📊 Ukupno mečeva: {len(df)}")
    print(f"📁 Sačuvano u: {output_file}")

if __name__ == "__main__":
    main()
