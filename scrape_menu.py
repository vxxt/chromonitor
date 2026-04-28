import json
import time
import requests
import os
from playwright.sync_api import sync_playwright

URL = "https://www.chromehearts.com"
DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK", "")
KNOWN = {"/baccarat", "/scents", "/socks", "/boxers-leggings", "/intimates", "javascript:void(0);"}
STATE_FILE = "state.json"


def load_state():
    try:
        with open(STATE_FILE) as f:
            return set(json.load(f))
    except:
        return set(KNOWN)


def save_state(hrefs):
    with open(STATE_FILE, "w") as f:
        json.dump(list(hrefs), f)


def get_hrefs():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
        page = context.new_page()
        page.goto(URL, timeout=60000)
        page.click("div.b-menu-icon")
        page.wait_for_selector(".b-dropdown-menu", state="attached", timeout=15000)
        links = page.locator(".b-dropdown-menu a.b-dropdown-menu_item")
        hrefs = set()
        for i in range(links.count()):
            href = links.nth(i).get_attribute("href")
            if href:
                hrefs.add(href)
        browser.close()
    print(f"Found hrefs: {hrefs}")
    return hrefs


if __name__ == "__main__":
    for _ in range(30): # 30 x 10 seconds = 5 minutes
        try:
            seen = load_state()
            current = get_hrefs()
            new = current - seen
            if new:
                for href in new:
                    full = URL + href if href.startswith("/") else href
                    requests.post(DISCORD_WEBHOOK, json={"content": f" @everyone 🆕 New Chrome Hearts menu item: {full}"})
                print(f"Change detected: {new}")
                save_state(current)
            else:
                print("No change.")
        except Exception as e:
            print(f"Error: {e}")
            raise
        time.sleep(10)
