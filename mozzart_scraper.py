from playwright.sync_api import sync_playwright
import pandas as pd
import os
import time
import random
from datetime import datetime, timedelta

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
        context = browser
