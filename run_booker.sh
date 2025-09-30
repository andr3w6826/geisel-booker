#!/usr/bin/env bash
set -euo pipefail

# change to actual filepath of "geisel-booker" folder
cd "(Put in file path of the folder)"  # e.g. /Users/firstlastname/Downloads/geisel-booker


mkdir -p logs
/usr/bin/python3 script.py >> logs/booker.out 2>> logs/booker.err
