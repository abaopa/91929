import json
import os
import sys

def dump_ranks():
    with open('src/saved_game.json', 'r') as f:
        state = json.load(f)
    
    cdhs = ['♣', '♦', '♥', '♠']
    
    for i, p_data in enumerate(state['card_piles']):
        print(f"\nPile {i}:")
        cards = p_data['rg_cards']
        faces = [cdhs[c % 4] + str(int(c/4)+1) for c in cards]
        ranks = [(int(c/4)+1) for c in cards]
        for idx, (face, rank) in enumerate(zip(faces, ranks)):
            print(f"  {idx:2}: {face} (Rank {rank})")

if __name__ == "__main__":
    dump_ranks()
