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