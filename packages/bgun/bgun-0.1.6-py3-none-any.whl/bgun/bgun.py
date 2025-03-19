#!/usr/bin/env python3


import os
import json

# Get the path of bgen.json (ensure it's in the same directory as this script)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "bgen.json")

def main():
    """Entry point for the script."""
    print("bgen.py script is running!!!!!! V2")
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
            print("Loaded config:", config)
    else:
        print("bgen.json not found!")

if __name__ == "__main__":
    main()



