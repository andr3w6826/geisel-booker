# functions.py
from datetime import datetime, timedelta, timezone


def date_selector(page, advance_days):
    target_date = datetime.now() + timedelta(days=advance_days)

    today_month = datetime.now().strftime("%B")

    def target_midnight_utc_ms(days=advance_days):
        # 1) Compute the local target *date* (no time)
        target_date = (datetime.now() + timedelta(days=days)).date()
        # 2) Build midnight *UTC* for that date
        target_utc_midnight = datetime(
            target_date.year, target_date.month, target_date.day, tzinfo=timezone.utc
        )
        # 3) Convert to ms since epoch
        return int(target_utc_midnight.timestamp() * 1000)
    
    timestamp_ms = target_midnight_utc_ms(advance_days)
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
    


def aria_writer(room: str, start_time: str, location: str, advance_days) -> str:
    """
        Build the aria-label string for a given room and start time.
        Example target:
        "2:00pm Sunday, September 21, 2025 - Geisel 2096: 2nd Floor - Available"
    """

    # Compute target date
    target_date = datetime.now() + timedelta(days=advance_days)

    try:
        floor_digit = int(str(room)[0])  # take first character
    except (ValueError, IndexError):
        floor_digit = None

    if floor_digit == 1:
        floor = ": 1st Floor"
    elif floor_digit == 2:
        floor = ": 2nd Floor"
    elif floor_digit == 4:
        floor = ": 4th Floor"
    elif floor_digit == 5:
        floor = ": 5th Floor"
    elif floor_digit == 6:
        floor = ": 6th Floor"
    elif floor_digit == 7:
        floor = ": 7th Floor"
    elif floor_digit == 8:
        floor = ": 8th Floor"
    else:
        floor = f"{floor_digit}th Floor" if floor_digit is not None else ""

    text = (
        f"{start_time} "
        f"{target_date.strftime('%A')}, {target_date.strftime('%B')} {target_date.day}, {target_date.year} "
        f"- {location} {room}{floor} - Available"
    )
    print(f'Looking for: {text}')
    return text


def click_event_by_aria(page, aria_label: str):
    loc = page.locator(f"a.s-lc-eq-avail[aria-label='{aria_label}']")
    # bring it into view (horizontal scroller too)
    loc.scroll_into_view_if_needed()
    loc.wait_for(state="visible", timeout=10000)
    try:
        loc.first.click()
    except Exception:
        box = loc.first.bounding_box()
        page.mouse.click(box["x"] + box["width"]/2, box["y"] + box["height"]/2)

def select_last_end_time(page):
    sel = page.locator("select[id^='bookingend_']")
    options = sel.locator("option").all()
    # idk why theres an error here but it works!
    # print(f"Found {len(options)} end time options")
    # print(options)
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
    btn = page.locator("#terms_accept")
    btn.wait_for(state="visible", timeout=10000)  # wait up to 10s
    
    btn.click()
def final_submit(page):
    page.get_by_role("button", name="Submit my Booking").click()