# geisel-booker

How to use the booker!


- Ensure you have python3 installed
- make sure you have pip
- pip install -r requirements.txt
- Plug your username/passwerword in config.json of the reservations website
- Choose the room number you want and time you want for 2 weeks in advance
- Click the run script on script.py and give it a minute to run. Every one in awhile the script will wait for you to authenticate on duo.


Now the script runs! Its time to automate it so that it runs every night at 12:00am. 

- Open the Shortcuts application
- Add a new shortcut with purpose "Run Shell Script"
- In the code part, you'll replace whats there whatever your filepath is to run_booker.sh "sh /Users/examplename/Downloads/geisel-booker/run_booker.sh" or whatever 
    - set the "Shell" to "sh" and do not run as administrator
- Script finished
- To do the automation, create a new automation (not new shortcut) and attach the shortcut to the automation and set the automation to run at 12:01am everyday
