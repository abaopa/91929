"""
This module defines the `CardPile` class, which represents a collection of cards
and provides methods to manage and collect cards based on specific rules. The class
interacts with a card queue to handle collected cards.

Classes:
    - CardPile: Represents a collection of cards with methods to manage and collect them.

Author: jordank
Date: April 1, 2025
"""

# ----------------------------------------------------------------------
# File: card_pile.py
# Description: This module defines the `CardPile` class, which represents
#              a collection of cards and provides methods to manage and
#              collect cards based on specific rules. The class interacts
#              with a card queue to handle collected cards.
# Author: jordank
# Date: April 1, 2025
# ----------------------------------------------------------------------
# Class Overview:
# - CardPile:
#   - Attributes:
#       - n_card_count: Tracks the number of cards in the pile.
#       - b_pile_empty: Indicates whether the pile is empty.
#       - rg_cards: List of cards in the pile.
#   - Methods:
#       - try_collect_cards: Attempts to collect cards based on rules.
#       - try_collect_3_cards: Checks if three specific cards can be collected.
#       - console_do_collect_cards: Handles card collection via console input.
#       - ask_collect_cards_option: Prompts the user to select a collection option.
#       - print_collect_3_cards: Prints details of three cards for collection.
# ----------------------------------------------------------------------

class CardPile:
    def __init__(self):
        self.n_card_count = 0
        self.b_pile_empty = False
        self.rg_cards = []
        # self.rgCards.clear()

    def try_collect_cards(self, card_queue, b_collect, rule_priority=[4, 2, 1], b_only_pile=False):

        collectable = 0
        if self.n_card_count >= 3:
            # Check if this collection would empty the only remaining pile
            if not (b_only_pile and self.n_card_count == 3):
                # Rule 1: First two + last one
                if self.try_collect_3_cards(0, 1, self.n_card_count - 1, card_queue, False):
                    collectable += 4
        if self.n_card_count > 3:
            # Rule 2: First one + last two
            if self.try_collect_3_cards(0, self.n_card_count - 2, self.n_card_count - 1, card_queue, False):
                collectable += 2
            # Rule 3: Last three
            if self.try_collect_3_cards(self.n_card_count - 3, self.n_card_count - 2, self.n_card_count - 1, card_queue, False):
                collectable += 1

        if b_collect:
            # Use the provided priority to decide which rule to execute first
            for rule_id in rule_priority:
                if collectable & rule_id:
                    self.collect_rule(rule_id, card_queue)
                    break

        return collectable

    def collect_rule(self, rule_id, card_queue):
        """Executes a specific collection rule (1, 2, or 4)."""
        if rule_id == 4:
            return self.try_collect_3_cards(0, 1, self.n_card_count - 1, card_queue, True)
        elif rule_id == 2:
            return self.try_collect_3_cards(0, self.n_card_count - 2, self.n_card_count - 1, card_queue, True)
        elif rule_id == 1:
            return self.try_collect_3_cards(self.n_card_count - 3, self.n_card_count - 2, self.n_card_count - 1, card_queue, True)
        return False

    def try_collect_3_cards(self, card1, card2, card3, card_queue, b_collect):
        if card1 < 0 or card2 < 0 or card3 < 0 :
            return False
        summation = int((self.rg_cards[card1]) / 4) + int((self.rg_cards[card2]) / 4) + int((self.rg_cards[card3]) / 4) + 3
        if (summation % 10) == 9:
            if b_collect:
                card_queue.put_a_card_to_queue(self.rg_cards.pop(card1))
                card_queue.put_a_card_to_queue(self.rg_cards.pop(card2 - 1))
                card_queue.put_a_card_to_queue(self.rg_cards.pop(card3 - 2))
                self.n_card_count = self.n_card_count - 3
                self.b_pile_empty = (self.n_card_count == 0)

                if self.n_card_count < 0:
                    assert ()

            return True
        else:
            return False

    def console_do_collect_cards(self, card_queue, option, b_auto_check):

        if b_auto_check:
            if self.try_collect_cards(card_queue, False) > 0 :
                return self.try_collect_cards(card_queue, True)
            else:
                return 0
        else:
            return self.ask_collect_cards_option(card_queue)

    def ask_collect_cards_option(self, card_queue, b_collect = True):
        if self.n_card_count >= 3:
            self.print_collect_3_cards(" 1)", 0, 1, self.n_card_count - 1)
        if self.n_card_count > 3:
            self.print_collect_3_cards(" 2)", 0, self.n_card_count - 2, self.n_card_count - 1)
            self.print_collect_3_cards(" 3)", self.n_card_count - 3, self.n_card_count - 2, self.n_card_count - 1)

        option = input("(1):, (2):, (3), (N)ext: ")
        print(option)

        collectable = 0
        if option == '1':
            if self.try_collect_3_cards(0, 1, self.n_card_count - 1, card_queue, b_collect):
                collectable = 4
        elif option == '2':
            if self.try_collect_3_cards(0, self.n_card_count - 2, self.n_card_count - 1, card_queue, b_collect):
                collectable = 2
        elif option == '3':
            if self.try_collect_3_cards(self.n_card_count - 3, self.n_card_count - 2, self.n_card_count - 1, card_queue, b_collect):
                collectable = 1

        return collectable

    def print_collect_3_cards(self, option, card1, card2, card3):
        print(option, self.rgCardFace[self.rg_cards[card1]], self.rgCardFace[self.rg_cards[card2]],
              self.rgCardFace[self.rg_cards[card3]])
