import sys
import os

# Robust path handling for both running as a script and as a packaged executable
if getattr(sys, 'frozen', False):
    # If the app is running as a packaged executable
    bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(sys.executable)))
else:
    # If the app is running as a script
    bundle_dir = os.path.dirname(os.path.abspath(__file__))

# Ensure the root of the project and the 'src' directory are in the python path
if bundle_dir not in sys.path:
    sys.path.insert(0, bundle_dir)
src_dir = os.path.join(bundle_dir, "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

import flet as ft
from src.mobile_main import main

if __name__ == "__main__":
    # Correctly identify assets directory relative to the current script or executable
    assets_dir = os.path.join(bundle_dir, "assets")
    
    # Run the Flet application
    ft.app(target=main, assets_dir=assets_dir)
