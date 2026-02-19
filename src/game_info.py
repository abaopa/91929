# ----------------------------------------------------------------------
# File: game_info.py
# Description: This module defines the `GameInfo` class, which manages the 
#              state and logic of the card game. It integrates with the 
#              `CardPile`, `CardQueue`, and `Cards` classes to handle 
#              gameplay, including dealing cards, managing piles, and 
#              checking win conditions.
# Author: jordank
# Date: April 1, 2025
# ----------------------------------------------------------------------
# Class Overview:
# - GameInfo:
#   - Attributes:
#       - game: Reference to the game object for rendering and printing.
#       - b_win: Indicates if the game has been won.
#       - b_done: Indicates if the game is finished.
#       - cnt_hands: Tracks the number of hands dealt.
#       - current_pile: Tracks the current pile being played.
#       - rg_stack_operation: Stack for saving and restoring game states.
#       - cards: Instance of the `Cards` class representing the deck.
#       - card_queue: Instance of the `CardQueue` class for managing the queue.
#       - card_piles: List of `CardPile` instances representing the piles.
#   - Methods:
#       - __init__: Initializes the game state and deck.
#       - play_real_init: Sets up the game state for a new game.
#       - push_stack_operations: Saves the current game state to a stack.
#       - pop_stack_operations: Restores the last saved game state.
#       - deal_first_8_cards: Deals the first 8 cards to the piles.
#       - deal_one_card: Deals one card to the current pile.
#       - pre_play: Prepares the game for automatic play.
#       - play_game_automatically: Plays the game automatically.
#       - check_win_status: Checks if the game has been won or finished.
#       - start_game: Starts a new game with optional shuffling.
# ----------------------------------------------------------------------

import json
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

    def __init__(self, game, deck=None):
        self.game = game

        self.b_win = False
        self.b_done = False
        self.b_auto_saved = False
        self.cnt_hands = 0
        self.current_pile = -1

        self.rg_stack_operation = []
        
        self.cards = Cards(deck)
        self.rule_priority = [4, 2, 1] # Default: Rule 1 > Rule 2 > Rule 3

    def save_game_state(self, filepath):
        game_state = {
            'b_win': self.b_win,
            'b_done': self.b_done,
            'b_auto_saved': self.b_auto_saved,
            'cnt_hands': self.cnt_hands,
            'current_pile': self.current_pile,
            'cards_deck': self.cards.rg_cards, # The initial shuffled deck
            'card_queue': {
                'rg_cards': self.card_queue.rg_cards,
                'n_count': self.card_queue.n_count
            },
            'card_piles': [
                {'rg_cards': p.rg_cards, 'n_card_count': p.n_card_count, 'b_pile_empty': p.b_pile_empty}
                for p in self.card_piles
            ],
            'rg_stack_operation': []
        }

        # Serialize rg_stack_operation
        for item in self.rg_stack_operation:
            stack_item_data = {
                'current_pile': item[0],
                'cnt_hands': item[1],
                'piles': [
                    {'rg_cards': item[2][0], 'n_card_count': item[2][1], 'b_pile_empty': item[2][2]},
                    {'rg_cards': item[3][0], 'n_card_count': item[3][1], 'b_pile_empty': item[3][2]},
                    {'rg_cards': item[4][0], 'n_card_count': item[4][1], 'b_pile_empty': item[4][2]},
                    {'rg_cards': item[5][0], 'n_card_count': item[5][1], 'b_pile_empty': item[5][2]}
                ],
                'queue': {
                    'rg_cards': item[6][0],
                    'n_count': item[6][1]
                }
            }
            game_state['rg_stack_operation'].append(stack_item_data)

        with open(filepath, 'w') as f:
            json.dump(game_state, f, indent=4)

    def load_game_state(self, filepath):
        with open(filepath, 'r') as f:
            game_state = json.load(f)

        # Restore initial deck and restart from beginning
        deck = game_state.get('cards_deck')
        if deck:
            self.cards = Cards(deck)
            self.play_real_init(False) # Don't shuffle, use the loaded deck
            self.game.print_deck()
            self.game.print_all_piles()
            self.game.print_game_info()
        else:
            raise ValueError("No deck information found in save file.")

    def play_real_init(self, b_shuffle_cards):
        self.b_done = False
        self.b_win = False
        self.b_auto_saved = False
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
            self.b_done = False
            self.b_win = False

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
            self.card_queue.n_count = len(self.card_queue.rg_cards)

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
        # Save current status BEFORE any changes
        if b_play_real:
            self.push_stack_operations()

        # Advance to the next pile
        self.current_pile = (self.current_pile + 1) % 4

        # Skip piles that have been cleared, but avoid infinite loop
        checked_piles = 0
        while self.card_piles[self.current_pile].b_pile_empty and checked_piles < 4:
            self.check_win_status()
            if self.b_done:
                return False
            self.current_pile = (self.current_pile + 1) % 4
            checked_piles += 1
        
        if checked_piles == 4:
            # All piles are empty! check_win_status should have caught this, but safety first
            self.check_win_status()
            return False

        # Deal a card from the card queue
        if self.card_queue.n_count > 0:
            self.card_piles[self.current_pile].rg_cards.append(self.card_queue.get_a_card_from_queue())
            self.card_piles[self.current_pile].n_card_count += 1
            self.card_piles[self.current_pile].b_pile_empty = False
            self.cnt_hands += 1
            return True
        else:
            # Can't deal, but game might not be 'done' if collections are possible
            self.check_win_status()
            return False

    def pre_play(self):
        # self.cHands, self.CurrentPile = self.DealFirst8Cards(bPlayReal)

        self.play_game_automatically(False)

    def play_game_automatically(self, b_verbose):
        while self.deal_one_card(False):
            if b_verbose and not self.game.b_auto_play:
                break

            if b_verbose:
                self.game.print_all_piles()
                self.game.print_game_info()
                # self.game.render_cards()
                time.sleep(0.1)

            # Global Auto-Play Loop: Check all piles for collections
            moved = True
            while moved:
                if b_verbose and not self.game.b_auto_play:
                    break
                
                moved = False
                
                # Check for last pile status
                non_empty_piles = [p for p in self.card_piles if not p.b_pile_empty]
                
                # Refined Last Pile Rule: 
                # Clearing the final pile is prohibited UNLESS it results in a win.
                # Win requires hands >= 40.
                next_card_is_3 = False
                if self.card_queue.n_count > 0:
                    next_card = self.card_queue.rg_cards[0]
                    if (int(next_card / 4) + 1) == 3:
                        next_card_is_3 = True
                
                # Block if it's the last pile AND (not fully dealt OR (cards remain AND it's not a '3' win)).
                is_last_pile = len(non_empty_piles) == 1 and \
                               (self.cnt_hands < 40 or (self.card_queue.n_count > 0 and not next_card_is_3))

                # Preliminary check: count all available moves across all piles
                all_moves = []
                for i in range(4):
                    mask = self.card_piles[i].try_collect_cards(self.card_queue, False, self.rule_priority, is_last_pile)
                    for r in self.rule_priority:
                        if mask & r:
                            all_moves.append((i, r))
                
                if not all_moves:
                    break
                
                # Pick the first available move (no AI)
                p_idx, r_id = all_moves[0]
                self.card_piles[p_idx].collect_rule(r_id, self.card_queue)
                moved = True
                
                if moved and b_verbose:
                    self.game.print_all_piles()
                    self.game.print_game_info()
                    # self.game.render_cards()
                    time.sleep(0.1)

            # Check status
            self.check_win_status()

            if self.b_done or self.cnt_hands > 10000:
                if b_verbose:
                    self.game.print_all_piles()
                    self.game.print_game_info()
                    # self.game.render_cards()
                    self.game.print_queue()
                break

    def check_win_status(self):
        # ALL WIN CONDITIONS REQUIRE THE FULL DECK TO BE DEALT AT LEAST ONCE
        b_win_possible = self.cnt_hands >= 40

        # Check if all piles are empty
        non_empty_piles = [p for p in self.card_piles if not p.b_pile_empty]
        if not non_empty_piles:
            self.b_done = True
            # WIN CONDITION A: Table is clear and all 40 cards are back in queue
            if b_win_possible and self.card_queue.n_count == 40:
                self.game.render_peep_card_in_queue()
                self.game.print_peep_next_in_queue()
                self.b_win = True
            return

        # WIN CONDITION B: 39 cards in queue, and exactly one card (rank "3") on the table
        if b_win_possible and self.card_queue.n_count == 39:
            for pile in range(0, 4):
                if not self.card_piles[pile].b_pile_empty and \
                        self.card_piles[pile].n_card_count == 1:
                    card_rank = (int((self.card_piles[pile].rg_cards[0]) / 4) + 1)
                    if card_rank == 3:
                        self.b_win = True
                        self.b_done = True
                        return
        
        # LOSS / STUCK CONDITION
        if self.card_queue.n_count == 0:
            non_empty_piles = [p for p in self.card_piles if not p.b_pile_empty]
            # If queue is empty, is_last_pile constraint is False because clearing it ends the game correctly (Win A or B)
            has_move = False
            for i in range(4):
                if self.card_piles[i].try_collect_cards(self.card_queue, False, self.rule_priority, False) > 0:
                    has_move = True
                    break
            
            if not has_move:
                self.b_done = True

    def start_game(self, shuffle_cards):
        # print(" starting a new game", shuffle_cards, self.game.b_win_game_only, self.b_win, self.b_done, self.cnt_hands)
        self.game.print_deck()

        if shuffle_cards:
            if self.game.b_win_game_only:
                self.b_win = False
                print("Searching for a winnable deck...")
                deck_count = 0
                # check if this is a WIN game
                while not self.b_win:
                    deck_count += 1
                    if deck_count % 10 == 0:
                        print(f"  Decks checked: {deck_count}...")
                    self.play_real_init(shuffle_cards)
                    self.pre_play()
                print(f"Found winnable deck after {deck_count} shuffles.")

        # print(" start a new game", shuffle_cards, self.game.b_win_game_only, self.b_win, self.b_done, self.cnt_hands)

        # start play game
        # Pass shuffle_cards here to ensure we get a new deck if requested
        self.play_real_init(shuffle_cards and not self.game.b_win_game_only)
        self.game.print_deck()
        self.game.print_all_piles()
        self.game.print_game_info()
        # self.game.render_cards()

    # (solve_for_best_move removed)

