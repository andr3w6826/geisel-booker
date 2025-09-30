## geisel-booker

This script opens the Geisel study room reservations site (`https://ucsd.libcal.com/reserve`), logs in, and books a room 2 weeks in advance.

### Setup
1. Install Python 3: `https://www.python.org/downloads/`.
2. In your terminal, navigate to the `geisel-booker` folder.
   - Example: `/Users/firstlast/Downloads/geisel-booker`
3. Install dependencies, so run this in your terminal:
   - `pip install -r requirements.txt`

### Configure
1. Open `config.json` and set your UCSD credentials under `auth.username` and `auth.password`.
2. Set your desired `requests.room` and starting time `requests.hour1`.
   - Keep the format of the time, all lowercase and no spaces( e.g. "3:00pm", "10:00am")
   - The program automatically books the maximum allowed duration.
   - Date is fixed to 2 weeks in advance.

### Run
1. From the `geisel-booker` folder, run:
   - `sh run_booker.sh`
2. Ensure `run_booker.sh` has the correct folder path in the `cd` command. It should look something like `/Users/firstlast/Downloads/geisel-booker`

### Notes
- You may be prompted for Duo authentication periodically (as normal).

### Automate with Shortcuts (macOS)
1. Open the Shortcuts app on your Mac.
2. Create a new shortcut with the action "Run Shell Script".
3. Set Shell to `sh` and use a command like:
   - `sh /Users/yourname/Downloads/geisel-booker/run_booker.sh`
4. Create a new Automation (not a new Shortcut) that runs this shortcut daily at 12:01 AM.

### Contact
Questions or suggestions? Email: anc062@ucsd.edu