# geisel-booker

This script automatically opens the Geisel study room reservations site, logs in, and books a room 2 weeks in advance! Guaranteeing constant availability :)

How to set up:
    1. Make sure you have python3 installed (https://www.python.org/downloads/)
    2. Inside your terminal, nagivate to the folder geisel-reservations
        - Your file path will look something like /User/firstlast/Downloads/geisel-reservation
    3. Run this command in the terminal to install the necessary packages "pip install -r requirements.txt"

How to use this script:
    1. You'll want to navigate to the config.json file first and plug in your username/password you use with UCSD authentication
    2. Plug in the room you want and the time of day you want to start at
        - The program will automatically book for maximum time allowed
        - The option to choose the date is not available as it will always be 2 weeks in advance
    3. Test out the script! Just run script.py either with a play but

Notes:
    - It will ask you to duo authenticate every once in awhile (just like you have to normally)

How to automate it! 
    (Our next step is to get this running at 12:00am every day so we'll "permanently" have a Geisel room available!)

- Open the Shortcuts application on your Mac
- Add a new shortcut with task "Run Shell Script"
- In the code part, you'll replace whats there whatever your filepath is to run_booker.sh. It should look something like "sh /Users/examplename/Downloads/geisel-booker/run_booker.sh" or whatever 
- set the "Shell" to "sh" and do not run as administrator
- Now that script is complete
- To do the automation, create a new automation (not new shortcut) and attach the shortcut to the automation and set the automation to run at 12:01am everyday

Let me know if you run into any issues, have suggestions, or questions! Email me at anc062@ucsd.edu