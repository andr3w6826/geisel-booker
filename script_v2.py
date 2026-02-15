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

    # ============================================================
    # DEBUG: print all libcal cookies after page load
    # if PHPSESSID is missing or id comes back as 1, this is why
    # cookies = context.cookies(["https://ucsd.libcal.com"])
    # print("libcal cookies after page.goto:")
    # for c in cookies:
    #     print(f"  {c['name']} | expires={c['expires']} | domain={c['domain']}")
    # ============================================================

    grid_resp = context.request.post(
        GRID_URL,
        headers={
            "X-Requested-With": "XMLHttpRequest",
            "Referer": RESERVE_URL,
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept": "application/json, text/javascript, */*; q=0.01",
        },
        data=GRID_PAYLOAD,
    )

    if grid_resp.status == 200:
        print('Code 200: Successfully fetched grid data.')


    start_str, end_str = datetime_utils.build_start_end_datetime(grid_payload_dict['start'], user_profile['hour1'])
    print(f"Start: {start_str}, End: {end_str}")

    eid = grid_payload_dict['eid']
    grid_data = grid_resp.json()['slots']

    # Find the slot that matches our desired start time and eid
    grid_resp_checksum = payload_utils.find_checksum(grid_data, start_str, int(eid))
    print(f'Desired slot checksum: {grid_resp_checksum}')

    ADD_PAYLOAD, add_payload_dict = payload_utils.construct_add_payload(grid_resp_checksum, grid_payload_dict, start_str)
    print(f'add_payload_dict: {add_payload_dict}')

    add_resp = page.evaluate("""
    async (payload) => {
        const r = await fetch('/spaces/availability/booking/add', {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Accept': 'application/json, text/javascript, */*; q=0.01'
            },
            body: payload
        });
        return r.json();
    }
""", ADD_PAYLOAD)


    # ============================================================
    # DEBUG: if id=1 here, the add POST is not authenticated
    # print(f"add_resp: {add_resp}")
    # print(f"add_resp booking id: {add_resp['bookings'][0]['id']}")
    # ============================================================

    # take add_resp, extract information, construct add(update) payload
    update_payload_dict = payload_utils.extract_add_response(add_resp, grid_payload_dict)
    print(f"update_payload_dict: {update_payload_dict}")
    UPDATE_PAYLOAD = payload_utils.construct_update_payload(update_payload_dict)

    update_resp = page.evaluate("""
        async (payload) => {
            const r = await fetch('/spaces/availability/booking/add', {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'Accept': 'application/json, text/javascript, */*; q=0.01'
                },
                body: payload
            });
            return r.json();
        }
    """, UPDATE_PAYLOAD)
    
    print(f"update_resp: {update_resp}")
    time_payload_dict = payload_utils.extract_update_response(update_resp)
    print(f"time_payload_dict: {time_payload_dict}")
    TIME_PAYLAOD = payload_utils.construct_time_payload(time_payload_dict)
    time_resp = page.evaluate("""
        async (payload) => {
            const r = await fetch('/ajax/space/times', {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'Accept': 'application/json, text/javascript, */*; q=0.01'
                },
                body: payload
            });
            return r.json();
        }
    """, TIME_PAYLAOD)
    auth_url = "https://ucsd.libcal.com" + time_resp["redirect"]
    auth_resp = page.evaluate(f"""
        async () => {{
            const r = await fetch('{auth_url}');
            return r.text();
        }}
    """)

    session_id = payload_utils.extract_session_id_from_html(auth_resp)
    print("session_id:", session_id)

    checkout_payload = payload_utils.construct_checkout_payload(session_id)

    checkout_resp = page.evaluate("""
        async (payload) => {
            const formData = new FormData();
            for (const [key, value] of Object.entries(payload)) {
                formData.append(key, value);
            }
            const r = await fetch('/ajax/equipment/checkout', {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'application/json, text/javascript, */*; q=0.01'
                },
                body: formData
            });
            return r.text();
        }
    """, checkout_payload)

    print(checkout_resp[:300])

    context.close()