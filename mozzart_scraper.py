import requests
import pandas as pd

def main():
    # Test URL (samo za proveru)
    url = "https://www.mozzartbet.com/sr/rezultati"
    try:
        r = requests.get(url)
        if r.status_code == 200:
            print("Mozzart sajt dostupan")
        else:
            print("Problem sa sajtom:", r.status_code)
    except Exception as e:
        print("Greska:", e)

if __name__ == "__main__":
    main()
