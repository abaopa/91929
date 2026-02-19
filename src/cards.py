# ----------------------------------------------------------------------
# File: cards.py
# Description: This module defines the `Cards` class, which represents a 
#              deck of cards. It provides functionality to initialize, 
#              shuffle, and display the deck of cards.
# Author: jordank
# Date: April 1, 2025
# ----------------------------------------------------------------------
# Class Overview:
# - Cards:
#   - Attributes:
#       - card_count: Total number of cards in the deck (52).
#       - rg_cards: List of card indices (0 to 51).
#       - rg_card_face: List of card face representations (e.g., "♣ 1", "♦ 13").
#   - Methods:
#       - __init__: Initializes the deck of cards, optionally using a provided deck.
#       - shuffle_cards: Shuffles the deck randomly.
#       - print_initialized_deck: Prints the initialized deck for debugging purposes.
# ----------------------------------------------------------------------

import random

class Cards:
    def __init__(self, deck):
        self.card_count = 52
        self.rg_cards = []  # 0, 2, ... 51
        self.rg_card_face = []  # C1, D1, H1, S1, ..., C13, D13, H13, S13
        self.rg_cards.clear()

        # cdhs = ['C', 'D', 'H', 'S']
        cdhs = ['♣', '♦', '♥', '♠']
        
        if deck:
            self.rg_cards = deck
            self.rg_card_face = [cdhs[deck % 4] + "%2d" % (int(deck / 4) + 1) for deck in range(self.card_count)]

        else:
            self.rg_cards = [deck for deck in range(self.card_count)]
            self.rg_card_face = [cdhs[deck % 4] + "%2d" % (int(deck / 4) + 1) for deck in range(self.card_count)]

            self.shuffle_cards()  
             
        self.print_initialized_deck()                     

    def shuffle_cards(self):
        random.shuffle(self.rg_cards)    

    def print_initialized_deck(self):
        # if self.game.b_verbose:
        print("Deck:", [self.rg_card_face[card] for card in self.rg_cards])