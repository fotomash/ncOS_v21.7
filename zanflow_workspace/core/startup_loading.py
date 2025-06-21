# core/startup_loading.py

import sys
import time

def animated_loading_screen():
    captain_motto = "\n🧭 Captain Zanzibar: Chart the Unknown. Conquer the Impossible.\n"
    print(captain_motto)

    loading_phrases = [
        "Charting maps",
        "Scouting tides",
        "Aligning stars",
        "Ready for launch"
    ]

    for phrase in loading_phrases:
        for i in range(4):
            sys.stdout.write(f"\r{phrase}{'.' * i}   ")
            sys.stdout.flush()
            time.sleep(0.4)
        time.sleep(0.5)

    print("\n🚀 Systems Ready. Captain Zanzibar Awaiting Orders.\n")

if __name__ == "__main__":
    animated_loading_screen()
