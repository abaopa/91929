import time
# from typing import List

from card_pile import CardPile
from card_queue import CardQueue
from cards import Cards

class GameInfo:
    # current_pile: int
    # card_queue: CardQueue
    # card_piles: List[CardPile]

    # # b_auto_play: bool
    # # b_auto_check: bool
    # # b_peep_next_in_queue: bool
    # # b_display_short_pile: bool
    # # b_win_game_only: bool

    # b_verbose: bool

    # b_win: bool
    # b_done: bool

    def __init__(self, deck, game):
        self.game = game

        self.b_win = False
        self.b_done = False
        self.cnt_hands = 0
        self.current_pile = -1

        # self.card_count = 52
        # self.rg_cards = []  # 0, 2, ... 51
        # self.rg_card_face = []  # C1, D1, H1, S1, ..., C13, D13, H13, S13
        # self.rg_cards.clear()
        self.rg_stack_operation = []

        self.cards = Cards(deck)

        # # cdhs = ['C', 'D', 'H', 'S']
        # cdhs = ['♣', '♦', '♥', '♠']

        # if deck:
        #     self.rg_cards = deck
        #     self.rg_card_face = [cdhs[deck % 4] + "%2d" % (int(deck / 4) + 1) for deck in range(self.card_count)]

        # else:
        #     self.rg_cards = [deck for deck in range(self.card_count)]
        #     self.rg_card_face = [cdhs[deck % 4] + "%2d" % (int(deck / 4) + 1) for deck in range(self.card_count)]

        #     # random.shuffle(self.rg_cards)
        #     self.shuffle_cards()

        # self.print_initialized_deck()

    # def print_initialized_deck(self):
    #     # if self.game.b_verbose:
    #     print("Deck:", [self.rg_card_face[card] for card in self.rg_cards])

    # def shuffle_cards(self):
    #     random.shuffle(self.rg_cards)

    def play_real_init(self, b_shuffle_cards):
        self.b_done = False
        self.b_win = False
        self.cnt_hands = 0
        self.current_pile = -1
        self.rg_stack_operation.clear()

        if b_shuffle_cards:
            self.cards.shuffle_cards()

        # initialize a card queue
        self.card_queue = CardQueue(self.cards.rg_cards)

        # initialize 4 empty piles
        self.card_piles = []
        for pile in range(4):
            self.card_piles.append(CardPile())

        self.game.print_deck()
        self.game.print_piles(self.current_pile)
        self.game.print_queue()

        # self.cHands, self.CurrentPile = self.DealFirst8Cards(bPlayReal)   

    def push_stack_operations(self):
        self.rg_stack_operation.append((self.current_pile, self.cnt_hands,
                                        (self.card_piles[0].rg_cards.copy(), self.card_piles[0].n_card_count,
                                         self.card_piles[0].b_pile_empty),
                                        (self.card_piles[1].rg_cards.copy(), self.card_piles[1].n_card_count,
                                         self.card_piles[1].b_pile_empty),
                                        (self.card_piles[2].rg_cards.copy(), self.card_piles[2].n_card_count,
                                         self.card_piles[2].b_pile_empty),
                                        (self.card_piles[3].rg_cards.copy(), self.card_piles[3].n_card_count,
                                         self.card_piles[3].b_pile_empty),
                                        (self.card_queue.rg_cards.copy(), self.card_queue.n_count)))

    def pop_stack_operations(self):
        if len(self.rg_stack_operation) > 0:

            pile_rd_cards = []
            for pile in range(4):
                pile_rd_cards.append([])
            card_q_rd_cards = []

            (self.current_pile, self.cnt_hands,
             (pile_rd_cards[0], self.card_piles[0].n_card_count, self.card_piles[0].b_pile_empty),
             (pile_rd_cards[1], self.card_piles[1].n_card_count, self.card_piles[1].b_pile_empty),
             (pile_rd_cards[2], self.card_piles[2].n_card_count, self.card_piles[2].b_pile_empty),
             (pile_rd_cards[3], self.card_piles[3].n_card_count, self.card_piles[3].b_pile_empty),
             (card_q_rd_cards, self.card_queue.n_count)) = self.rg_stack_operation.pop()

            for pile in range(4):
                self.card_piles[pile].rg_cards.clear()
                [self.card_piles[pile].rg_cards.append(card) for card in pile_rd_cards[pile]]

            # if (self.CardQ.rgCards != card_q_rd_cards):
            self.card_queue.rg_cards.clear()
            [self.card_queue.rg_cards.append(card) for card in card_q_rd_cards]

            if self.card_queue.n_count == 40:
                # assert (self.cnt_hands != 0)
                self.current_pile = -1
                self.cnt_hands = 0
            else:
                self.current_pile = self.current_pile + 3
                self.current_pile = self.current_pile % 4
                while self.card_piles[self.current_pile].b_pile_empty:
                    self.current_pile = self.current_pile + 3
                    self.current_pile = self.current_pile % 4

    def deal_first_8_cards(self, b_play_real):

        # Deal first 8 cards

        # self.current_pile = -1
        while self.cnt_hands < 8:
            self.deal_one_card(b_play_real)

            if b_play_real:
                self.game.print_piles(self.current_pile)
                self.game.print_queue()

        return self.cnt_hands, self.current_pile

    def deal_one_card(self, b_play_real):

        # AdvanceToNextPile
        self.current_pile = self.current_pile + 1
        self.current_pile = self.current_pile % 4

        while self.card_piles[self.current_pile].b_pile_empty:
            self.check_win_status()
            if self.b_done:
                break
            self.current_pile = self.current_pile + 1
            self.current_pile = self.current_pile % 4

            # Deal a card from card queue
        if not self.card_piles[self.current_pile].b_pile_empty and self.card_queue.n_count > 0:
            # Save current status
            if b_play_real:
                self.push_stack_operations()
            self.card_piles[self.current_pile].rg_cards.append(self.card_queue.get_a_card_from_queue())
            self.card_piles[self.current_pile].n_card_count = self.card_piles[self.current_pile].n_card_count + 1
            self.cnt_hands = self.cnt_hands + 1
            return True
        else:
            return False

    def pre_play(self):
        # self.cHands, self.CurrentPile = self.DealFirst8Cards(bPlayReal)

        self.play_game_automatically(False)

    def play_game_automatically(self, b_verbose):
        while self.deal_one_card(False):
            if b_verbose:
                self.game.print_all_piles()
                self.game.print_game_info()
                # time.sleep(1)
                # self.game.render_cards()

            while self.card_piles[self.current_pile].try_collect_cards(self.card_queue, True) > 0:
                if b_verbose:
                    self.game.print_all_piles()
                    self.game.print_game_info()
                    # time.sleep(1)                    
                    # self.game.render_cards()

            # Check status
            self.check_win_status()

            if self.b_done or self.cnt_hands > 10000:
                break

    def check_win_status(self):
        if self.card_queue.n_count == 0:
            self.b_done = True
        elif self.card_queue.n_count == 40 and self.cnt_hands > 1:
            # the next card in queue will be a "Three"
            self.game.render_peep_card_in_queue()
            self.game.print_peep_next_in_queue()
            self.b_win = True
            self.b_done = True
        elif self.card_queue.n_count == 39 and self.cnt_hands > 1:
            # there is one card left in the table and it will be a "Three"
            for pile in range(0, 4):
                if not self.card_piles[pile].b_pile_empty and \
                        self.card_piles[pile].n_card_count > 0 and \
                        (int((self.card_piles[pile].rg_cards[0]) / 4) + 1) == 3:
                    self.b_win = True
                    self.b_done = True
                    break

    def start_game(self, shuffle_cards):
        # print(" starting a new game", shuffle_cards, self.game.b_win_game_only, self.b_win, self.b_done, self.cnt_hands)
        self.game.print_deck()

        if shuffle_cards:
            if self.game.b_win_game_only:
                self.b_win = False
                # check if this is a WIN game
                while not self.b_win:

                    self.play_real_init(shuffle_cards)
                    self.game.print_deck()
                    self.pre_play()
                    print("=>Done:", self.b_done, ", Win:", self.b_win, ", Hands:", self.cnt_hands)

        # print(" start a new game", shuffle_cards, self.game.b_win_game_only, self.b_win, self.b_done, self.cnt_hands)

        # start play game
        self.play_real_init(False)
        self.game.print_deck()
        self.game.print_all_piles()
        self.game.print_game_info()
        self.game.render_cards()
