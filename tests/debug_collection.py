import json
import os
import sys

# Add src to path so we can import modules
sys.path.append(os.path.join(os.getcwd(), 'src'))

from card_pile import CardPile
from card_queue import CardQueue

def debug_saved_game(filename):
    with open(filename, 'r') as f:
        state = json.load(f)
    
    print(f"File: {filename}")
    print(f"Hands: {state['cnt_hands']}")
    print(f"Current Pile: {state['current_pile']}")
    
    card_queue = CardQueue(state['card_queue']['rg_cards'])
    
    for i, p_data in enumerate(state['card_piles']):
        pile = CardPile()
        pile.rg_cards = p_data['rg_cards']
        pile.n_card_count = p_data['n_card_count']
        pile.b_pile_empty = p_data['b_pile_empty']
        
        print(f"\nPile {i}: {pile.n_card_count} cards")
        ranks = [(int(c/4)+1) for c in pile.rg_cards]
        print(f"  Ranks: {ranks}")
        
        # Check for last pile status (simplified for debug)
        non_empty_piles_count = sum(1 for p in state['card_piles'] if not p['b_pile_empty'])
        is_last_pile = (non_empty_piles_count == 1)
        
        mask = pile.try_collect_cards(card_queue, False, b_only_pile=is_last_pile)
        print(f"  Collectable mask: {mask} (is_last_pile={is_last_pile})")
        
        if pile.n_card_count >= 3:
            r1_indices = [0, 1, pile.n_card_count - 1]
            r1 = [ranks[idx] for idx in r1_indices]
            s1 = sum(r1)
            print(f"    Rule 1 (0, 1, -1): {r1} Sum: {s1} ({s1%10})")
        if pile.n_card_count > 3:
            r2_indices = [0, pile.n_card_count - 2, pile.n_card_count - 1]
            r2 = [ranks[idx] for idx in r2_indices]
            s2 = sum(r2)
            print(f"    Rule 2 (0, -2, -1): {r2} Sum: {s2} ({s2%10})")
            r3_indices = [pile.n_card_count - 3, pile.n_card_count - 2, pile.n_card_count - 1]
            r3 = [ranks[idx] for idx in r3_indices]
            s3 = sum(r3)
            print(f"    Rule 3 (-3, -2, -1): {r3} Sum: {s3} ({s3%10})")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else 'src/saved_game.json'
    debug_saved_game(target)
