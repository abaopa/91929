# card queue keeps remaining cards

class CardQueue:
    def __init__(self, rg_cards):
        self.b_verbose = False
        self.n_count = 0
        self.rg_cards = []
        CARDS_USED_IN_GAME = 40

        # rgCards: the entire deck, 52 cards
        # self.rgCards: the entire deck in CardQ, 40 cards   

        if self.b_verbose:
            print(rg_cards)

        for card in rg_cards:
            if card < CARDS_USED_IN_GAME:     # remove Jacks, Queens, Kings
                self.rg_cards.append(card)
                self.n_count = self.n_count + 1
                 
        if self.b_verbose:
            print(self.rg_cards)
            print(self.n_count)

    def get_a_card_from_queue(self):
        if self.rg_cards:
            card_from_queue = self.rg_cards[0]
            self.rg_cards.remove(card_from_queue)
            self.n_count = self.n_count - 1
            assert(self.n_count == len(self.rg_cards))
            return card_from_queue
        else:
            return None

    def put_a_card_to_queue(self, card_to_queue):
        self.rg_cards.append(card_to_queue)
        self.n_count = self.n_count + 1
        assert(self.n_count == len(self.rg_cards))

