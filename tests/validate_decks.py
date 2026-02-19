import os
import re
import sys
from typing import List, Tuple, Set

# Add src to path for absolute imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from game_info import GameInfo

# Increase recursion depth for deep game trees
sys.setrecursionlimit(5000)

class HeadlessGame:
    """Mock UI to satisfy GameInfo's rendering calls without a GUI."""
    def __init__(self):
        self.b_auto_play = True
    def print_deck(self): pass
    def print_piles(self, cp): pass
    def print_queue(self): pass
    def print_all_piles(self): pass
    def print_game_info(self): pass
    def render_cards(self): pass
    def render_peep_card_in_queue(self, b=True): pass
    def print_peep_next_in_queue(self): pass

def load_deck_from_file(filepath: str) -> List[int]:
    with open(filepath, 'r') as f:
        content = f.read()
        deck = [int(n) for n in re.findall(r'\d+', content)]
        return deck

def get_state_key(engine: GameInfo) -> Tuple:
    """Creates a hashable representation of the current game state."""
    piles_tuple = tuple(tuple(p.rg_cards) for p in engine.card_piles)
    queue_tuple = tuple(engine.card_queue.rg_cards)
    # Include current_pile and cnt_hands to distinguish between dealing cycles
    return (engine.current_pile, engine.cnt_hands, piles_tuple, queue_tuple)

def solve_recursive(engine: GameInfo, visited: Set[Tuple]) -> bool:
    """Recursively explores all legal moves to find a win path."""
    state = get_state_key(engine)
    if state in visited:
        return False
    visited.add(state)

    # 1. Check win
    engine.check_win_status()
    if engine.b_win:
        return True
    
    # 2. Check loss/done
    if engine.b_done:
        return False

    # 3. Find all possible collection moves across all piles
    moves = []
    for i in range(4):
        mask = engine.card_piles[i].try_collect_cards(engine.card_queue, False)
        if mask & 4: moves.append((i, 4))
        if mask & 2: moves.append((i, 2))
        if mask & 1: moves.append((i, 1))

    # Optimization: If there are many moves, try them one by one.
    # We use engine.push/pop to backtrack.
    for p_idx, r_id in moves:
        engine.push_stack_operations()
        engine.card_piles[p_idx].collect_rule(r_id, engine.card_queue)
        if solve_recursive(engine, visited):
            return True
        engine.pop_stack_operations()

    # Branch B: Try dealing the next card
    if engine.card_queue.n_count > 0:
        engine.push_stack_operations()
        if engine.deal_one_card(True):
            if solve_recursive(engine, visited):
                return True
        engine.pop_stack_operations()

    return False

def validate_all_decks():
    test_dir = os.path.dirname(__file__)
    files = [f for f in os.listdir(test_dir) if f.endswith('.txt') and 'quick_save' not in f]
    files.sort()

    passed = 0
    total = 0

    print("\n" + "="*80)
    print(f"{'FILE':<25} | {'EXP':<8} | {'SOLVER':<8} | {'RESULT'}")
    print("-"*80)

    for filename in files:
        is_win_file = "(win)" in filename.lower() or "_win" in filename.lower()
        expected = "WIN" if is_win_file else "BAD"
        
        filepath = os.path.join(test_dir, filename)
        try:
            deck = load_deck_from_file(filepath)
            if len(deck) != 52: continue
            total += 1
            
            engine = GameInfo(HeadlessGame(), deck)
            engine.play_real_init(False)
            
            # Start solving from the initial state
            is_winnable = solve_recursive(engine, set())
            
            actual = "WIN" if is_winnable else "BAD"
            
            # If the file says it was a WIN, the solver MUST find a win path.
            # If the file says BAD, the solver shouldn't find a path (unless it's actually winnable).
            status = "✅ PASS" if actual == expected else "❌ FAIL"
            if actual == expected: passed += 1
            
            print(f"{filename:<25} | {expected:<8} | {actual:<8} | {status}")

        except Exception as e:
            print(f"{filename:<25} | ERROR: {str(e)}")

    print("-"*80)
    print(f"SUMMARY: {passed} / {total} Passed (Full Branch Explorer)")
    print("="*80 + "\n")

if __name__ == "__main__":
    validate_all_decks()
