class CardPile:
    def __init__(self):
        self.n_card_count = 0
        self.b_pile_empty = False
        self.rg_cards = []
        # self.rgCards.clear()

    def try_collect_cards(self, card_queue, b_collect):

        collectable = 0
        if self.n_card_count >= 3:
            if self.try_collect_3_cards(0, 1, self.n_card_count - 1, card_queue, b_collect):
                collectable += 4
        if self.n_card_count > 3:                
            if self.try_collect_3_cards(0, self.n_card_count - 2, self.n_card_count - 1, card_queue, b_collect):
                collectable += 2
            if self.try_collect_3_cards(self.n_card_count - 3, self.n_card_count - 2, self.n_card_count - 1, card_queue, b_collect):
                collectable += 1

        return collectable

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

                if self.n_card_count == 0:
                    self.b_pile_empty = True
                elif self.n_card_count < 0:
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
