import json
from pathlib import Path



def load_cfg(path):
    with open(path, "r") as f:
        return json.load(f)

def user_profile():
    base_dir = Path(__file__).resolve().parent.parent
    config_path = base_dir / "config_v2.json"

    cfg = load_cfg(config_path)

    auth = cfg["auth"]
    req = cfg["requests"]

    profile = {
        "username": auth["username"],
        "password": auth["password"],
        "building": req["building"],
        "room": req["room"],
        "hour1": req["hour1"],
        "advance_days": req["advance_days"],
    }

    return profile

def fill_credentials(page):

    TARGET_USERNAME = user_profile()['username']
    TARGET_PASSWORD = user_profile()['password']

    page.locator("#ssousername").wait_for(state="visible", timeout=10000)

    page.locator("#ssousername").fill(TARGET_USERNAME)
    page.locator("#ssopassword").fill(TARGET_PASSWORD)
    page.get_by_role("button", name="Login", exact=True).click()

def confirm_duo_device(page):
    page.locator("#trust-browser-button").wait_for(state="visible", timeout=50000)
    page.locator("#trust-browser-button").click()
