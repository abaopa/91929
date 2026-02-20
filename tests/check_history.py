import json
import os
import sys

# Add src to path so we can import modules
sys.path.append(os.path.join(os.getcwd(), 'src'))

from card_pile import CardPile
from card_queue import CardQueue

def check_history():
    with open('src/saved_game.json', 'r') as f:
        data = json.load(f)
    
    stack = data['rg_stack_operation']
    print(f"Checking {len(stack)} history items...")
    
    for idx, item in enumerate(stack):
        cnt_hands = item['cnt_hands']
        card_queue = CardQueue(item['queue']['rg_cards'])
        
        for i, p_data in enumerate(item['piles']):
            pile = CardPile()
            pile.rg_cards = p_data['rg_cards']
            pile.n_card_count = p_data['n_card_count']
            pile.b_pile_empty = p_data['b_pile_empty']
            
            mask = pile.try_collect_cards(card_queue, False)
            if mask > 0:
                ranks = [(int(c/4)+1) for c in pile.rg_cards]
                print(f"Move found at Hand {cnt_hands}, Pile {i}, Mask {mask}")
                print(f"  Ranks: {ranks}")
                if mask & 4: print(f"    Rule 1: {[ranks[0], ranks[1], ranks[-1]]} Sum: {sum([ranks[0], ranks[1], ranks[-1]])}")
                if mask & 2: print(f"    Rule 2: {[ranks[0], ranks[-2], ranks[-1]]} Sum: {sum([ranks[0], ranks[-2], ranks[-1]])}")
                if mask & 1: print(f"    Rule 3: {[ranks[-3], ranks[-2], ranks[-1]]} Sum: {sum([ranks[-3], ranks[-2], ranks[-1]])}")

if __name__ == "__main__":
    check_history()
