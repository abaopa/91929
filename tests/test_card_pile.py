import pytest
from card_pile import CardPile
from card_queue import CardQueue

class MockQueue:
    def __init__(self):
        self.cards = []
    def put_a_card_to_queue(self, card):
        self.cards.append(card)

def test_try_collect_3_cards_success():
    """Test that 3 cards summing to X9 are collected correctly."""
    pile = CardPile()
    # Values: 10 (card 40), 10 (card 41), 9 (card 36)
    # Cards: (idx/4)+1
    # 36/4 + 1 = 10
    # 20/4 + 1 = 6
    # 12/4 + 1 = 4
    # 10 + 6 + 4 + 3 = 23 (Mod 10 != 9) -> No
    
    # 8/4+1=3, 12/4+1=4, 36/4+1=10
    # 3 + 4 + 10 + 3 = 20 (Mod 10 == 0) -> No

    # Let's pick cards:
    # Card 0: (0/4)+1 = 1
    # Card 4: (4/4)+1 = 2
    # Card 12: (12/4)+1 = 4
    # 1 + 2 + 4 + 3 = 10 (No)
    
    # Need sum = 6, 16, 26...
    # Card 0 (1), Card 4 (2), Card 40 (11)? No, only up to 40.
    # Card 0 (1), Card 4 (2), Card 12 (4) -> Sum 7 + 3 = 10
    # Card 0 (1), Card 4 (2), Card 20 (6) -> Sum 9 + 3 = 12
    # Card 4 (2), Card 8 (3), Card 4 (2) -> Sum 7 + 3 = 10
    
    # Let's use 2, 3, 4 (Ranks 1, 2, 3):
    # Card 4 (rank 1)
    # Card 8 (rank 2)
    # Card 12 (rank 3)
    # 1 + 2 + 3 + 3 = 9! Success.
    
    pile.rg_cards = [4, 8, 12]
    pile.n_card_count = 3
    queue = MockQueue()
    
    assert pile.try_collect_3_cards(0, 1, 2, queue, True) is True
    assert pile.n_card_count == 0
    assert pile.b_pile_empty is True
    assert len(queue.cards) == 3

def test_try_collect_3_cards_failure():
    """Test that 3 cards NOT summing to X9 are rejected."""
    pile = CardPile()
    pile.rg_cards = [0, 4, 12] # 1, 2, 4
    # 1 + 2 + 4 + 3 = 10
    pile.n_card_count = 3
    queue = MockQueue()
    
    assert pile.try_collect_3_cards(0, 1, 2, queue, True) is False
    assert pile.n_card_count == 3
    assert len(queue.cards) == 0

def test_rule_priority_execution():
    """Test that the highest priority rule is executed first."""
    pile = CardPile()
    # We want a state where multiple rules could apply
    # Rule 4: 0, 1, last
    # Rule 2: 0, last-1, last
    # Rule 1: last-2, last-1, last
    
    # Let's make all three rules valid?
    # Actually, let's just test that rule_priority list is respected.
    pile.rg_cards = [0, 4, 8, 12, 16] # 1, 2, 3, 4, 5
    # Rule 1 (last 3): 3, 4, 5 -> 3+4+5+3 = 15 (No)
    
    # Set up specific cards for Rule 4 (0, 1, 4): 1, 2, 5 -> 1+2+5+3 = 11 (No)
    # Let's use 1, 2, 3 for Rule 4:
    # index 0, 1, 4:
    # rg_cards[0]=4 (Rank 1), rg_cards[1]=8 (Rank 2), rg_cards[4]=12 (Rank 3)
    # 1+2+3+3 = 9. Rule 4 works.
    
    pile.rg_cards = [4, 8, 20, 20, 12] # Ranks 1, 2, 5, 5, 3
    pile.n_card_count = 5
    # Rule 4 (0,1,4): 1, 2, 3 -> 1+2+3+3 = 9 (YES)
    # Rule 1 (2,3,4): 6, 6, 3 -> 6+6+3+3 = 18 (NO)
    
    queue = MockQueue()
    # Try collect with Rule 4 priority
    mask = pile.try_collect_cards(queue, True, rule_priority=[4])
    assert mask & 4
    assert pile.n_card_count == 2
    assert pile.rg_cards == [20, 20]
