import requests
import pandas as pd

# Datum koji želiš da preuzmeš (format YYYY-MM-DD)
DATE = "2025-12-17"

# Output Excel fajl
OUTPUT_FILE = "mozzart_finished_yesterday.xlsx"

# 🔹 Skriveni Mozzart endpoint
URL = f"https://www.mozzartbet.com/api/fb/results?date={DATE}&events=finished"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def scrape_finished_matches():
    response = requests.get(URL, headers=headers)
    data = response.json()  # JSON sa svim mečevima

    results = []

    for match in data.get("matches", []):
        # Svaki meč sadrži timove, FT i HT rezultate
        results.append({
            "Time": match.get("time", ""),
            "Home": match.get("homeTeam", {}).get("name", ""),
            "Away": match.get("awayTeam", {}).get("name", ""),
            "FT": f"{match.get('score', {}).get('fullTime', {}).get('home', '-')}" \
                  f":{match.get('score', {}).get('fullTime', {}).get('away', '-')}",
            "HT": f"{match.get('score', {}).get('halfTime', {}).get('home', '-')}" \
                  f":{match.get('score', {}).get('halfTime', {}).get('away', '-')}"
        })

    return results

if __name__ == "__main__":
    matches = scrape_finished_matches()

    df = pd.DataFrame(matches)
    df.to_excel(OUTPUT_FILE, index=False)

    if matches:
        print(f"✅ Sačuvano {len(df)} završenih fudbalskih mečeva")
    else:
        print("⚠️ Nema završenih fudbalskih mečeva")
