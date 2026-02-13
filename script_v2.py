from pathlib import Path
from playwright.sync_api import sync_playwright
import utils.payload_utils as payload_utils
import utils.user_utils as user_utils
import utils.datetime_utils as datetime_utils



RESERVE_URL = "https://ucsd.libcal.com/reserve"
GRID_URL = "https://ucsd.libcal.com/spaces/availability/grid"
ADD_URL = "https://ucsd.libcal.com/spaces/availability/booking/add"
TIMES_URL = "https://ucsd.libcal.com/ajax/space/times"
CHECKOUT_URL = 'https://ucsd.libcal.com/ajax/equipment/checkout'
profile_dir = Path.cwd() / "pw-user-data"

GRID_PAYLOAD, grid_payload_dict = payload_utils.construct_grid_payload()
user_profile = user_utils.user_profile()

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=str(profile_dir),
        headless=False,
        args=["--start-maximized"],
    )
    page = context.new_page()
    page.goto(RESERVE_URL, wait_until="domcontentloaded")

 
    grid_resp = context.request.post(
        GRID_URL,
        headers={
            "X-Requested-With": "XMLHttpRequest",
            "Referer": RESERVE_URL,
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept": "application/json, text/javascript, */*; q=0.01",
        },
        data=GRID_PAYLOAD,  # string, not dict
    )

    if grid_resp.status == 200:
        print('Code 200: Successfully fetched grid data.')


    start_str, end_str = datetime_utils.build_start_end_datetime(grid_payload_dict['start'], user_profile['hour1'])
    print(f"Start: {start_str}, End: {end_str}")

    eid = grid_payload_dict['eid']
    grid_data = grid_resp.json()['slots']

    # Find the slot that matches our desired start time and eid
    grid_resp_checksum= payload_utils.find_checksum(grid_data, start_str, int(eid))
    print(f'Desired slot checksum: {grid_resp_checksum}')

    ADD_PAYLOAD, add_payload_dict = payload_utils.construct_add_payload(grid_resp_checksum, grid_payload_dict, start_str)

    add_resp = context.request.post(
        ADD_URL,
        headers={
            "X-Requested-With": "XMLHttpRequest",
            "Referer": RESERVE_URL,
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept": "application/json, text/javascript, */*; q=0.01"
        },
        data = ADD_PAYLOAD,
    )
    if add_resp.status == 200:
        print("add response 200")

    add_resp = add_resp.json()

    # take add_resp, extract information, construct add(update) payload
    update_payload_dict = payload_utils.extract_add_response(add_resp, grid_payload_dict)
    UPDATE_PAYLOAD = payload_utils.construct_update_payload(update_payload_dict)

    update_resp = context.request.post(
        ADD_URL,
        headers={
            "X-Requested-With": "XMLHttpRequest",
            "Referer": RESERVE_URL,
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept": "application/json, text/javascript, */*; q=0.01"
        },
        data = UPDATE_PAYLOAD,
    )
    if update_resp.status == 200:
        print("update response 200")
    
    update_resp = update_resp.json()
    time_payload_dict = payload_utils.extract_update_response(update_resp)
    TIME_PAYLAOD = payload_utils.construct_time_payload(time_payload_dict)
    time_resp = context.request.post(
        TIMES_URL,
        headers={
            "X-Requested-With": "XMLHttpRequest",
            "Referer": RESERVE_URL,
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept": "application/json, text/javascript, */*; q=0.01"
        },
        data = TIME_PAYLAOD,
    )
    if time_resp.status == 200:
        print("time response 200")

    print(time_resp.json())

    if "redirect" in time_resp.json():
        page.goto("https://ucsd.libcal.com" + time_resp.json()["redirect"], wait_until="domcontentloaded")
        if page.url.startswith("https://a5.ucsd"):
            input()
            # user_utils.fill_credentials(page)
            # user_utils.confirm_duo_device(page)
            # page.goto("https://ucsd.libcal.com" + time_resp.json()["redirect"], wait_until="domcontentloaded")

    page.goto(f"https://ucsd.libcal.com" + time_resp.json()['redirect'], wait_until="domcontentloaded")


    session_id = payload_utils.extract_session_id(page)
    print("session_id:", session_id)


    checkout_payload = payload_utils.construct_checkout_payload(session_id)

    checkout_resp = context.request.post(
        CHECKOUT_URL,  # <-- use the real checkout URL you captured
        headers={
            "X-Requested-With": "XMLHttpRequest",
            "Referer": RESERVE_URL,
            "Accept": "application/json, text/javascript, */*; q=0.01",
            # DO NOT set Content-Type here
        },
        data=checkout_payload  # pass dict, not string
    )

    print("checkout status:", checkout_resp.status)
    print(checkout_resp.text()[:300])

    context.close()
