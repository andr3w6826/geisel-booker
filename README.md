## geisel-booker

This script opens the Geisel study room reservations site (`https://ucsd.libcal.com/reserve`), logs in, and books a room 2 weeks in advance.


First-Time Setup (IMPORTANT — Do Not Skip)
I strongly recommend using a virtual environment (venv) so dependencies do not interfere with other Python projects on your computer.

### Setup
1. Install Python 3 if you don't have it yet: `https://www.python.org/downloads/`.
2. Download this project and open the .zip file on your computer
3. In your terminal, navigate to the `geisel-booker` folder.
   - Example: `/Users/firstlast/Downloads/geisel-booker`
4. Create a Virtual Environment (VERY IMPORTANT)
   Run: `python3 -m venv venv` then this `source venv/bin/activate` all in terminal
5. Install required packages
   Run: `python -m pip install -r requirements.txt` in terminal 
4. Install playwright browsers (REQUIRED)
   - `python -m playwright install`

### Configure
1. Open `config.json` and set your UCSD credentials under `auth.username` and `auth.password`.
2. Location: Either `Geisel` or `WongAvery` (its case sensitive oops)
3. Set your desired room: 
   - Examples: `Geisel Service Hub Room X` or `522` (only those 2 inputs are needed)
4. Set your desired starting time `requests.hour1`.
   - Keep the format of the time, all lowercase and no spaces( e.g. "3:00pm", "10:00am")
   - The program automatically books the maximum allowed duration.
   - Date is fixed to 2 weeks in advance.
   - Note WongAvery hours differ from Geisel
5. Advance Days: Days in advance to book
   - `1`: Geisel service hubs open 1 day in advance
   - `14`: All other rooms open 14 days in advance

### Run
1. From the `geisel-booker` folder, make the script executable (only needed once):
   - `chmod +x run_booker.sh`
2. Ensure `run_booker.sh` has the correct folder path in the `cd` command. It should look something like `/Users/firstlast/Downloads/geisel-booker`
3. Run it:
   - `./run_booker.sh` commond in terminal. 

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