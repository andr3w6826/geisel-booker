import json
from pathlib import Path
import functions as fn
from playwright.sync_api import sync_playwright
from playwright.sync_api import TimeoutError

def load_cfg(path):
    with open(path, "r") as f:
        return json.load(f)
    
def run_step(step_name, func, *args, **kwargs):
    """
    Run a function with error handling. 
    Prints a clean message if the step fails.
    """
    try:
        print(f"[INFO] Running step: {step_name} ...")
        return func(*args, **kwargs)
    except Exception as e:
        print(f"[ERROR] Step '{step_name}' failed: {e}")
        return None


def main():
    base_dir = Path(__file__).resolve().parent        # <-- folder of script.py
    config_path = base_dir / "config.json"            # <-- geisel-booker/config.json

    profile_dir = (base_dir / "pw-user-data").resolve()
    print(f"Using profile dir: {profile_dir}")

    cfg = load_cfg(config_path)
    print(f"Using config: {config_path}")

    # inputted username and passworld
    username = cfg.get("auth", {}).get("username")
    password = cfg.get("auth", {}).get("password")

    # user preferences parameters from config.json
    location = cfg.get("requests", {}).get("location")
    room_str = cfg.get("requests", {}).get('room')
    start_time_cfg = cfg.get("requests", {}).get("hour1")
    advance_days = cfg.get("requests", {}).get("advance_days")
    print(f"Booking Room: {room_str} at {start_time_cfg}:00 in {location} {advance_days} days in advance")

    # start at this URL
    url = "https://ucsd.libcal.com/reserve"

    with sync_playwright() as p:
        
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=True,
            slow_mo=2000,  # slow down actions by 1s to make it more human-like and easier to observe
        )
        page = context.new_page()
        page.goto(url)
        print(f"Navigated to {url}")
        # Switch buildings geisel/wongavery
        location_map = {
            "Geisel": "11273",
            "WongAvery": "11274"
        }

        lid_value = location_map.get(location)

        if lid_value is None:
            raise ValueError(f"Unknown location: {location}")
        page.select_option("#lid", value=lid_value)

        # checks if we need to DUO login
        if "SAML" in page.url:
            run_step("fill_credentials", fn.fill_credentials, page, username, password)
            run_step("confirm_duo_device", fn.confirm_duo_device, page)

        # Find the correct date 
        run_step("date_selector", fn.date_selector, page, advance_days)

        # Construct the aria-label text to find the correct booking slot
        aria = run_step("aria_writer", fn.aria_writer, room_str, start_time_cfg, location, advance_days)

        # Click the booking slot
        run_step("click_event_by_aria", fn.click_event_by_aria, page, aria)
        # Select the last end time option (latest possible end time)
        run_step("select_last_end_time", fn.select_last_end_time, page)

        # old stuff below, may need to be re-integrated depending on how the booking flow changes after clicking the slot
        # run_step("submit_booking", fn.submit_booking, page)

        # # Final submission may require another SAML login 
        # try:
        #     page.wait_for_url("**SAML2**", timeout=10000)
        # except TimeoutError:
        #     pass  # it's fine if URL didn't change yet
        # # it works!
        # if ("SAML2" in page.url) or ('SSO' in page.url):
        #     print("On SAML page, proceeding to fill credentials...")
        #     run_step('fill_credentials', fn.fill_credentials, page, username, password)
        #     run_step('confirm_duo_device', fn.confirm_duo_device, page)
            
        # run_step("submit", fn.submit, page)
        # run_step('final_submit', fn.final_submit, page)

        # print("Booking process completed. Closing browser.")
        # page.close()
        # After submit_booking
        run_step("submit_booking", fn.submit_booking, page)

        # Wait a moment for any navigation to settle
        page.wait_for_load_state("domcontentloaded", timeout=10000)

        # Check if we need SAML login
        try:
            page.wait_for_url("**SAML**", timeout=5000)
            if ("SAML2" in page.url) or ('SSO' in page.url):
                print("On SAML page, proceeding to fill credentials...")
                run_step('fill_credentials', fn.fill_credentials, page, username, password)
                run_step('confirm_duo_device', fn.confirm_duo_device, page)
        except TimeoutError:
            print("No SAML redirect detected, continuing...")

        # Now check which button is available
        try:
            # Try to find the terms_accept button first
            if page.locator("#terms_accept").is_visible(timeout=2000):
                run_step("submit", fn.submit, page)
        except:
            pass

        try:
            # Try to find the final submit button
            if page.get_by_role("button", name="Submit my Booking").is_visible(timeout=2000):
                run_step('final_submit', fn.final_submit, page)
        except:
            pass

        print("Booking process completed. Closing browser.")

 
if __name__ == "__main__":
    main()
