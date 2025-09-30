#!/usr/bin/env bash
set -euo pipefail

cd "(Put in file path of the folder)" # change to actual filepath of "geisel-booker" folder

# Run your script; change the python path if yours is different (check with: which python3)
# First run should be headed so you can trust Duo; later you can flip to headless in code.
mkdir -p logs
/usr/bin/python3 script.py >> logs/booker.out 2>> logs/booker.err
