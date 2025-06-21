# core/startup_splash.py

import time
import os

# Configuration
LOGO_PATH = "assets/branding/captain_zanzibar.gif"  # Adjust path as needed
ANIMATION_DISPLAY_SECONDS = 3  # How long to show the animation

# Optional: a simple textual splash if logo is unavailable
TEXT_SPLASH = """

    🌊🚀🧭
    WELCOME ABOARD, CAPTAIN ZANZIBAR
    Chart the Unknown. Conquer the Impossible.

"""

def display_splash():
    print("\nLoading Captain Zanzibar...")
    
    # Check if logo animation file exists
    if os.path.exists(LOGO_PATH):
        try:
            from PIL import Image
            img = Image.open(LOGO_PATH)
            img.show()
            time.sleep(ANIMATION_DISPLAY_SECONDS)
            img.close()
        except Exception as e:
            print(f"[Splash] Couldn't load animated logo. Reason: {e}")
            print(TEXT_SPLASH)
    else:
        # Fallback to text splash
        print(TEXT_SPLASH)

if __name__ == "__main__":
    display_splash()