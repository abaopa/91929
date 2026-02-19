import pytest
from cards import Cards
from card_queue import CardQueue

def test_cards_initialization():
    """Verify that Cards class shuffles and contains 52 cards."""
    c = Cards(None)
    assert len(c.rg_cards) == 52
    # Check for uniqueness
    assert len(set(c.rg_cards)) == 52

def test_card_queue_filtering():
    """Verify that CardQueue only keeps cards < 40."""
    # Deck with all cards
    deck = list(range(52))
    q = CardQueue(deck)
    assert q.n_count == 40
    for card in q.rg_cards:
        assert card < 40

def test_card_queue_operations():
    """Test getting and putting cards in the queue."""
    q = CardQueue([0, 1, 2])
    assert q.get_a_card_from_queue() == 0
    assert q.n_count == 2
    q.put_a_card_to_queue(10)
    assert q.n_count == 3
    assert q.rg_cards[-1] == 10
