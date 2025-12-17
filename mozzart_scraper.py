import requests
import pandas as pd
from datetime import datetime, timedelta

# URL mobilnog API-ja Mozzart (primer, provjereno da vraća JSON)
API_URL = "https://www.mozzartbet.com/sr/api/sports/results"

def get_finished_matches(days=1):
    results = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    for day_offset in range(days):
        date = (datetime.today() - timedelta(days=day_offset)).strftime("%Y-%m-%d")
        params = {"date": date}
        resp = requests.get(API_URL, headers=headers, params=params)
        if resp.status_code != 200:
            print(f"Greška pri preuzimanju za {date}: {resp.status_code}")
            continue

        data = resp.json()
        for league in data.get("leagues", []):
            for match in league.get("matches", []):
                if match.get("status") == "FT":  # završeni mečevi
                    results.append({
                        "Date": date,
                        "Time": match.get("time", ""),
                        "Home": match.get("home", ""),
                        "Away": match.get("away", ""),
                        "FT": f"{match.get('home_score', 0)}:{match.get('away_score', 0)}",
                        "HT": f"{match.get('home_ht_score', 0)}:{match.get('away_ht_score', 0)}",
                        "League": league.get("name", "")
                    })

    return results

if __name__ == "__main__":
    matches = get_finished_matches(days=2)

    if matches:
        df = pd.DataFrame(matches)
        df.to_excel("mozzart_finished_last_days.xlsx", index=False)
        print(f"ZAVRŠENI MEČEVI ({len(df)}) SAČUVANI.")
    else:
        print("Nema završenih mečeva.")
