import pytest
from game_info import GameInfo

class MockGame:
    def print_deck(self): pass
    def print_piles(self, cp): pass
    def print_queue(self): pass
    def render_cards(self): pass
    def render_peep_card_in_queue(self, b=True): pass
    def print_peep_next_in_queue(self): pass

def test_game_init():
    game = MockGame()
    info = GameInfo(game)
    info.play_real_init(False)
    
    assert info.cnt_hands == 0
    assert info.card_queue.n_count == 40
    assert len(info.card_piles) == 4

def test_deal_one_card():
    game = MockGame()
    info = GameInfo(game)
    info.play_real_init(False)
    
    success = info.deal_one_card(False)
    assert success is True
    assert info.cnt_hands == 1
    assert info.current_pile == 0
    assert info.card_piles[0].n_card_count == 1
    assert info.card_queue.n_count == 39

def test_win_status_empty_queue():
    game = MockGame()
    info = GameInfo(game)
    info.play_real_init(False)
    
    # Mock empty queue, no moves possible
    info.card_queue.n_count = 0
    # ensure no moves are possible
    for p in info.card_piles:
        p.b_pile_empty = True
        p.n_card_count = 0
        p.rg_cards = []
        
    info.check_win_status()
    assert info.b_done is True
    assert info.b_win is False

def test_win_condition_a():
    """Win Condition A: 40 cards in queue, table empty, cnt_hands >= 40."""
    game = MockGame()
    info = GameInfo(game)
    info.play_real_init(False)
    
    info.card_queue.n_count = 40
    info.cnt_hands = 40
    for p in info.card_piles:
        p.b_pile_empty = True
        
    info.check_win_status()
    assert info.b_win is True
    assert info.b_done is True

def test_win_condition_b_scenario_1():
    """Win Condition B Scenario 1: 39 cards in queue, 1 card on table is a '3', cnt_hands >= 40."""
    game = MockGame()
    info = GameInfo(game)
    info.play_real_init(False)
    
    info.card_queue.n_count = 39
    info.cnt_hands = 40
    
    # Rank 3 is values 8, 9, 10, 11 (8/4 + 1 = 3)
    info.card_piles[0].rg_cards = [8]
    info.card_piles[0].n_card_count = 1
    info.card_piles[0].b_pile_empty = False
    
    for i in range(1, 4):
        info.card_piles[i].b_pile_empty = True
        
    info.check_win_status()
    assert info.b_win is True
    assert info.b_done is True

def test_no_win_if_hands_less_than_40():
    """Verify that no win is declared if cnt_hands < 40 even if table is clear."""
    game = MockGame()
    info = GameInfo(game)
    info.play_real_init(False)
    
    # Table clear, all 40 cards in queue
    info.card_queue.n_count = 40
    info.cnt_hands = 20 # LESS THAN 40
    
    for p in info.card_piles:
        p.b_pile_empty = True
        
    info.check_win_status()
    assert info.b_win is False
    assert info.b_done is False

def test_last_pile_rule_blocking():
    """Verify that clearing the last pile is blocked if it's NOT a win."""
    game = MockGame()
    info = GameInfo(game)
    info.play_real_init(False)
    
    # Only one pile left
    for i in range(1, 4):
        info.card_piles[i].b_pile_empty = True
    
    info.card_piles[0].b_pile_empty = False
    # Ranks: 2 (val 4), 3 (val 8), 1 (val 0), 4 (val 12). 
    # Rule 1 (0,1,3) ranks: 2, 3, 4. Sum = 9. OK.
    info.card_piles[0].rg_cards = [4, 8, 0, 12]
    info.card_piles[0].n_card_count = 4
    
    # Cards remain in queue
    info.card_queue.n_count = 10
    
    # Next card is NOT a 3 (rank 1)
    info.card_queue.rg_cards[0] = 0
    
    # is_last_pile logic
    non_empty_piles = [p for p in info.card_piles if not p.b_pile_empty]
    next_card = info.card_queue.rg_cards[0]
    next_card_is_3 = (int(next_card / 4) + 1) == 3
    is_last_pile = len(non_empty_piles) == 1 and \
                   (info.cnt_hands < 40 or info.card_queue.n_count > 0) and \
                   not next_card_is_3
                   
    assert is_last_pile is True
    
    # Rule 1 (4) needs 3 cards to remain if is_last_pile is True
    # Pile has 4 cards. Rule 1 collects 3. 1 remains. OK.
    mask = info.card_piles[0].try_collect_cards(info.card_queue, False, [4, 2, 1], is_last_pile)
    assert mask & 4 # Rule 1 should be allowed as it leaves 1 card
    
    # Set pile to 3 cards. Rule 1 would clear it. Should be blocked.
    # Ranks: 3, 3, 3. Sum = 9.
    info.card_piles[0].rg_cards = [8, 9, 10]
    info.card_piles[0].n_card_count = 3
    mask = info.card_piles[0].try_collect_cards(info.card_queue, False, [4, 2, 1], is_last_pile)
    assert mask == 0 # All rules should be blocked because they would clear the board

def test_last_pile_rule_allowing_win_b():
    """Verify that clearing the last pile is ALLOWED if it's a win B (hands >= 40)."""
    game = MockGame()
    info = GameInfo(game)
    info.play_real_init(False)
    
    # Only one pile left
    for i in range(1, 4):
        info.card_piles[i].b_pile_empty = True
    
    info.card_piles[0].b_pile_empty = False
    # Ranks: 3, 3, 3. Sum = 9.
    info.card_piles[0].rg_cards = [8, 9, 10]
    info.card_piles[0].n_card_count = 3
    
    # Cards remain in queue
    info.card_queue.n_count = 10
    info.cnt_hands = 40 # DEALT FULL DECK
    
    # Next card IS a 3 (rank 3)
    info.card_queue.rg_cards[0] = 11 # Rank 3
    
    # is_last_pile logic
    non_empty_piles = [p for p in info.card_piles if not p.b_pile_empty]
    next_card = info.card_queue.rg_cards[0]
    next_card_is_3 = (int(next_card / 4) + 1) == 3
    is_last_pile = len(non_empty_piles) == 1 and \
                   (info.cnt_hands < 40 or info.card_queue.n_count > 0) and \
                   not next_card_is_3
                   
    assert is_last_pile is False # Should be false because next_card_is_3 is true
    
    mask = info.card_piles[0].try_collect_cards(info.card_queue, False, [4, 2, 1], is_last_pile)
    assert mask > 0 # Moves should be allowed because it leads to Win B
