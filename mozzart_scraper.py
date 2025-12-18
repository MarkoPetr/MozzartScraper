from playwright.sync_api import sync_playwright
import pandas as pd

DATE = "2025-12-17"
URL = f"https://www.mozzartbet.com/sr/rezultati/Fudbal/1?date={DATE}&events=finished"
OUTPUT_FILE = "mozzart_finished_yesterday.xlsx"

def scrape_finished_matches():
    results = []
    all_requests = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Presretanje svih XHR/Fetch request-a
        def capture_request(route, request):
            if "results" in request.url or "events" in request.url:
                all_requests.append(request.url)
            route.continue_()

        page.route("**/*", capture_request)

        page.goto(URL, timeout=60000)
        page.wait_for_timeout(8000)  # čekamo da svi requesti prođu

        # 🔹 Sada iteriramo sve presretnute URL-ove da dohvatimo JSON sa mečevima
        import requests

        for req_url in all_requests:
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "application/json, text/plain, */*",
                    "Referer": URL,
                    "Origin": "https://www.mozzartbet.com"
                }
                resp = requests.get(req_url, headers=headers, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    matches = data.get("matches", [])
                    for match in matches:
                        results.append({
                            "Time": match.get("time", ""),
                            "Home": match.get("homeTeam", {}).get("name", ""),
                            "Away": match.get("awayTeam", {}).get("name", ""),
                            "FT": f"{match.get('score', {}).get('fullTime', {}).get('home', '-')}" \
                                  f":{match.get('score', {}).get('fullTime', {}).get('away', '-')}",
                            "HT": f"{match.get('score', {}).get('halfTime', {}).get('home', '-')}" \
                                  f":{match.get('score', {}).get('halfTime', {}).get('away', '-')}"
                        })
            except Exception as e:
                continue

        browser.close()

    # Ukloni duplikate ako ih ima
    unique_results = [dict(t) for t in {tuple(d.items()) for d in results}]
    return unique_results

if __name__ == "__main__":
    matches = scrape_finished_matches()

    df = pd.DataFrame(matches)
    df.to_excel(OUTPUT_FILE, index=False)

    if matches:
        print(f"✅ Sačuvano {len(df)} završenih fudbalskih mečeva")
    else:
        print("⚠️ Nema završenih fudbalskih mečeva")
