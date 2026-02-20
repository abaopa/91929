import json
import os
import sys

def find_all_triplets():
    with open('src/saved_game.json', 'r') as f:
        state = json.load(f)
    
    for i, p_data in enumerate(state['card_piles']):
        cards = p_data['rg_cards']
        ranks = [(int(c/4)+1) for c in cards]
        n = len(ranks)
        
        print(f"\nPile {i} ({n} cards):")
        found = False
        for i1 in range(n):
            for i2 in range(i1 + 1, n):
                for i3 in range(i2 + 1, n):
                    s = ranks[i1] + ranks[i2] + ranks[i3]
                    if s % 10 == 9:
                        print(f"  Triplet found: indices ({i1}, {i2}, {i3}) ranks ({ranks[i1]}, {ranks[i2]}, {ranks[i3]}) Sum: {s}")
                        found = True
        if not found:
            print("  No triplets found.")

if __name__ == "__main__":
    find_all_triplets()
