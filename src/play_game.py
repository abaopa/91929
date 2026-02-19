# ----------------------------------------------------------------------
# File: play_game.py
# Description: This script serves as the entry point for launching the card 
#              game application. It initializes the graphical user interface 
#              (GUI) by creating an instance of the `Game` class from the 
#              `game_ui` module and starts the Tkinter main event loop.
# Author: jordank
# Date: April 1, 2025
# ----------------------------------------------------------------------
# Functionality:
# - Imports the `game_ui` module to access the `Game` class.
# - Creates an instance of the `Game` class to initialize the GUI.
# - Starts the Tkinter main event loop to handle user interactions.
# ----------------------------------------------------------------------

import game_ui

# Entry point to main() function

if __name__ == '__main__':

    PM = game_ui.Game()
    
    PM.root.mainloop()