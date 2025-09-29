# functions.py
import yaml
from pathlib import Path
from datetime import datetime, timedelta, timezone
import re
import json

ADVANCE_DAYS = 14

def load_storage(p, path="storage.json"):
    """Create a new context using saved cookies and local storage."""
    try:
        with open(path, "r") as f:
            storage = json.load(f)
        context = p.chromium.launch_persistent_context(
            user_data_dir="./pw-user-data",  # keeps cache, cookies, etc.
            headless=False,
            slow_mo=200,
            storage_state=path               # preload saved cookies/storage
        )
        print(f"[info] Loaded storage state from {path}")
        return context
    except FileNotFoundError:
        # First run (no storage.json yet)
        return p.chromium.launch_persistent_context(
            user_data_dir="./pw-user-data",
            headless=False,
            slow_mo=200
        )



def date_selector(page):
    target_date = datetime.now() + timedelta(days=ADVANCE_DAYS)

    today_month = datetime.now().strftime("%B")

    def target_midnight_utc_ms(days=ADVANCE_DAYS):
        # 1) Compute the local target *date* (no time)
        target_date = (datetime.now() + timedelta(days=days)).date()
        # 2) Build midnight *UTC* for that date
        target_utc_midnight = datetime(
            target_date.year, target_date.month, target_date.day, tzinfo=timezone.utc
        )
        # 3) Convert to ms since epoch
        return int(target_utc_midnight.timestamp() * 1000)
    
    timestamp_ms = target_midnight_utc_ms(ADVANCE_DAYS)
    target_month = timestamp_ms_to_month = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc).strftime("%B")
    print(f"unix timestamp (ms): {timestamp_ms}, target month: {target_month}")

    page.get_by_role("button", name="Go To Date").click()
    if today_month != target_month:
        # Find next month button and click it
        page.locator("th.next").first.click()
        selector = f"td.day[data-date='{timestamp_ms}']"
        page.locator(selector).click()
    else:
        selector = f"td.day[data-date='{timestamp_ms}']"
        page.locator(selector).click()
    


def aria_writer(room: str, start_time: str) -> str:
    """
        Build the aria-label string for a given room and start time.
        Example target:
        "2:00pm Sunday, September 21, 2025 - Geisel 2096: 2nd Floor - Available"
    """

    # Compute target date
    target_date = datetime.now() + timedelta(days=ADVANCE_DAYS)

    try:
        floor_digit = int(str(room)[0])  # take first character
    except (ValueError, IndexError):
        floor_digit = None

    if floor_digit == 1:
        floor = "1st Floor"
    elif floor_digit == 2:
        floor = "2nd Floor"
    elif floor_digit == 4:
        floor = "4th Floor"
    elif floor_digit == 5:
        floor = "5th Floor"
    elif floor_digit == 6:
        floor = "6th Floor"
    elif floor_digit == 7:
        floor = "7th Floor"
    elif floor_digit == 8:
        floor = "8th Floor"
    else:
        floor = f"{floor_digit}th Floor" if floor_digit is not None else "Unknown Floor"

    # Construct the aria-label.
    # Wing-agnostic: stop after the colon, do not append "East"/"West".
    text = (
        f"{start_time} "
        f"{target_date.strftime('%A')}, {target_date.strftime('%B')} {target_date.day}, {target_date.year} "
        f"- Geisel {room}: {floor} - Available"
    )
    print(f'Looking for: {text}')
    return text


def click_event_by_aria(page, aria_label: str):
    loc = page.locator(f"a.s-lc-eq-avail[aria-label='{aria_label}']")
    # bring it into view (horizontal scroller too)
    loc.scroll_into_view_if_needed()
    # wait until it's actually clickable
    loc.wait_for(state="visible", timeout=10000)
    try:
        loc.first.click()  # normal click
    except Exception:
        # fallback if overlapped or tiny; click center via mouse
        box = loc.first.bounding_box()
        page.mouse.click(box["x"] + box["width"]/2, box["y"] + box["height"]/2)

def select_last_end_time(page):
    sel = page.locator("select[id^='bookingend_']")
    options = sel.locator("option").all()
    last_opt = options[-1]
    label = last_opt.text_content().strip()
    value = last_opt.get_attribute("value")

    sel.select_option(value=value)
    print(f"Selected last option: '{label}'")

def submit_booking(page):
    page.get_by_role("button", name="Submit Times").click()

def fill_credentials(page, TARGET_USERNAME, TARGET_PASSWORD):

    page.locator("#ssousername").wait_for(state="visible", timeout=10000)

    page.locator("#ssousername").fill(TARGET_USERNAME)
    page.locator("#ssopassword").fill(TARGET_PASSWORD)
    page.get_by_role("button", name="Login", exact=True).click()

def confirm_duo_device(page):
    page.locator("#trust-browser-button").wait_for(state="visible", timeout=50000)
    page.locator("#trust-browser-button").click()

def submit(page):
    # page.locator("#terms_accept").click()
    # page.get_by_role("button", name="Submit my Booking").click()
    btn = page.locator("#terms_accept")
    btn.wait_for(state="visible", timeout=10000)  # wait up to 10s
    print("Button text is:", btn.text_content())
    print("Is enabled?", btn.is_enabled())
    
    btn.click()
def final_submit(page):
    page.get_by_role("button", name="Submit my Booking").click()