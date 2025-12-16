import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

# --- CONFIG ---
OUTPUT_FILE = "sofascore_live.xlsx"
MOZZART_URL = "https://www.mozzartbet.com/sr/sport/fudbal"  # primer URL za fudbal

# --- FUNKCIJE ---
def fetch_finished_matches():
    """
    Preuzima HTML sa Mozzart sajta i vraća listu završenih mečeva.
    Svaki meč je dict: {'date', 'league', 'home_team', 'away_team', 'score'}
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    
    resp = requests.get(MOZZART_URL, headers=headers)
    resp.raise_for_status()
    
    soup = BeautifulSoup(resp.text, "html.parser")
    
    matches = []

    # Mozzart koristi klase za mečeve i rezultate, primer:
    match_containers = soup.select(".event-row")  # proveri stvarnu klasu
    for mc in match_containers:
        # status meča
        status = mc.select_one(".event-status")  # proveri klasu za status
        if not status or "Finished" not in status.text:
            continue
        
        date_elem = mc.select_one(".event-date")  # datum meča
        league_elem = mc.select_one(".event-league")  # liga
        teams = mc.select(".event-team-name")  # home/away
        score_elem = mc.select_one(".event-score")  # rezultat

        if not (date_elem and league_elem and len(teams) == 2 and score_elem):
            continue

        match = {
            "date": date_elem.text.strip(),
            "league": league_elem.text.strip(),
            "home_team": teams[0].text.strip(),
            "away_team": teams[1].text.strip(),
            "score": score_elem.text.strip()
        }
        matches.append(match)
    
    return matches

def save_to_excel(matches):
    """Snima listu mečeva u Excel"""
    if not matches:
        print("Nema novih završenih mečeva za upis.")
        return

    df = pd.DataFrame(matches)
    df["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df.to_excel(OUTPUT_FILE, index=False)
    print(f"Sačuvano {len(matches)} mečeva u {OUTPUT_FILE}")

# --- MAIN ---
if __name__ == "__main__":
    finished_matches = fetch_finished_matches()
    save_to_excel(finished_matches)
