import sys
import os

# Robust path handling for both running as a script and as a packaged executable
if getattr(sys, 'frozen', False):
    # If the app is running as a packaged executable
    bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(sys.executable)))
else:
    # If the app is running as a script
    bundle_dir = os.path.dirname(os.path.abspath(__file__))

# Ensure the 'src' directory is in the python path
src_dir = os.path.join(bundle_dir, "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

import game_ui

if __name__ == '__main__':
    # Initialize the Tkinter GUI
    PM = game_ui.Game()
    PM.root.mainloop()
