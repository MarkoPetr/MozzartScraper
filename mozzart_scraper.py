import requests
import pandas as pd

# Datum koji želiš da preuzmeš
DATE = "2025-12-17"

# Output Excel fajl
OUTPUT_FILE = "mozzart_finished_yesterday.xlsx"

# 🔹 Fetch URL koji vraća sve mečeve (primer iz Mozzart sajta)
URL = f"https://www.mozzartbet.com/sr/results/events?date={DATE}&sport=football&status=finished"

# Headeri da server vidi request kao pravi browser
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": f"https://www.mozzartbet.com/sr/rezultati/Fudbal/1?date={DATE}&events=finished",
    "Origin": "https://www.mozzartbet.com"
}

def scrape_finished_matches():
    response = requests.get(URL, headers=headers)
    
    if response.status_code != 200:
        print("⚠️ Greška pri preuzimanju podataka:", response.status_code)
        return []

    data = response.json()  # JSON sa svim mečevima
    results = []

    for match in data.get("matches", []):
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
