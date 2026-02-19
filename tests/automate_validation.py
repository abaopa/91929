import os
import re
import sys
import unittest

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from game_info import GameInfo

class MockGame:
    """Mock UI to satisfy GameInfo dependency."""
    def __init__(self):
        self.b_auto_play = True
        self.b_win_game_only = False
    def print_deck(self): pass
    def print_piles(self, cp): pass
    def print_queue(self): pass
    def print_all_piles(self): pass
    def print_game_info(self): pass
    def render_cards(self): pass
    def render_peep_card_in_queue(self, b=True): pass
    def print_peep_next_in_queue(self): pass

class TestGameAutomation(unittest.TestCase):
    def setUp(self):
        self.mock_game = MockGame()
        self.test_dir = os.path.dirname(__file__)

    def load_deck(self, filename):
        path = os.path.join(self.test_dir, filename)
        with open(path, 'r') as f:
            content = f.read()
            # Extract numbers from string like "[1, 2, 3]" or comma separated
            deck = [int(n) for n in re.findall(r'\d+', content)]
            return deck

    def run_simulation(self, deck):
        info = GameInfo(self.mock_game, deck)
        info.play_real_init(False) # Don't shuffle
        info.pre_play() # Run auto-play logic
        return info.b_win

    def test_known_decks(self):
        """Iterates through files in tests directory and validates outcome."""
        files = [f for f in os.listdir(self.test_dir) if f.endswith('.txt') and 'quick_save' not in f]
        
        results = {"pass": 0, "fail": 0, "details": []}
        
        print("\n" + "="*50)
        print(f"RUNNING 91929 AUTOMATED VALIDATION ({len(files)} files)")
        print("="*50)

        for filename in files:
            expected_win = "(win)" in filename.lower() or "_win" in filename.lower()
            
            try:
                deck = self.load_deck(filename)
                if len(deck) != 52:
                    continue
                
                actual_win = self.run_simulation(deck)
                
                if actual_win == expected_win:
                    status = "✅ PASS"
                    results["pass"] += 1
                else:
                    status = "❌ FAIL"
                    results["fail"] += 1
                
                print(f"{status} | File: {filename:<25} | Expected: {str(expected_win):<5} | Actual: {str(actual_win):<5}")
            
            except Exception as e:
                print(f"⚠️ ERROR | File: {filename} | {str(e)}")
                results["fail"] += 1

        print("="*50)
        print(f"SUMMARY: {results['pass']} Passed, {results['fail']} Failed")
        print("="*50)

if __name__ == "__main__":
    unittest.main()
