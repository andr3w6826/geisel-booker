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

    req = cfg.get("requests", {})
    room_str = req.get('room')
    print(f"Room: {room_str}")
    start_time_cfg = req.get("hour1")
    username = cfg.get("auth", {}).get("username")
    password = cfg.get("auth", {}).get("password")

    url = "https://ucsd.libcal.com/reserve"

    with sync_playwright() as p:
        
        
        # Launch Chromium in *headed* mode so you can see the browser
        #browser = p.chromium.launch(headless=False, slow_mo=200)
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=False,
            slow_mo=200
        )
        page = context.new_page()
        page.goto(url)

        if "SAML" in page.url:
            run_step("fill_credentials", fn.fill_credentials, page, username, password)
            run_step("confirm_duo_device", fn.confirm_duo_device, page)

        run_step("date_selector", fn.date_selector, page)

        aria = run_step("aria_writer", fn.aria_writer, room_str, start_time_cfg)
        run_step("click_event_by_aria", fn.click_event_by_aria, page, aria)
        run_step("select_last_end_time", fn.select_last_end_time, page)

        run_step("submit_booking", fn.submit_booking, page)

        print(page.url)

        try:
            page.wait_for_url("**SAML2**", timeout=5000)
        except TimeoutError:
            pass  # it's fine if URL didn't change yet
        if ("SAML2" in page.url) or ('SSO' in page.url):
            print("On SAML page, proceeding to fill credentials...")
            # Call your login helper
            run_step('fill_credentials', fn.fill_credentials, page, username, password)
            run_step('confirm_duo_device', fn.confirm_duo_device, page)
        
        run_step("submit", fn.submit, page)
        run_step('final_sub mit', fn.final_submit, page)

        input("Press Enter to close the browser...")
        page.close()

 
if __name__ == "__main__":
    main()
