import os
import sys
import time
from typing import List

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from game_info import GameInfo

class MockGame:
    """Mock UI to satisfy GameInfo dependency without overhead."""
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

def run_stress_test(num_games: int):
    mock_game = MockGame()
    wins = 0
    losses = 0
    total_time = 0

    print("\n" + "="*60)
    print("91929 CARD GAME STRESS TEST")
    print(f"Running {num_games} random games...")
    print("="*60 + "\n")

    start_time_all = time.time()

    for i in range(1, num_games + 1):
        info = GameInfo(mock_game)
        
        game_start = time.time()
        info.play_real_init(True) # Shuffle a new deck
        info.pre_play() # Run auto-play logic
        game_end = time.time()
        
        duration = game_end - game_start
        total_time += duration

        if info.b_win:
            wins += 1
            status = "WIN"
        else:
            losses += 1
            status = "LOSS"

        if i % 100 == 0 or i == num_games:
            win_rate = (wins / i) * 100
            print(f"Game {i:5}/{num_games} | Current Win Rate: {win_rate:6.2f}%")

    end_time_all = time.time()
    total_duration = end_time_all - start_time_all

    print("\n" + "="*60)
    print("STRESS TEST RESULTS")
    print("="*60)
    print(f"Total Games:      {num_games}")
    print(f"Total Wins:       {wins}")
    print(f"Total Losses:     {losses}")
    print(f"Win Rate:         {(wins/num_games)*100:.2f}%")
    print(f"Total Time:       {total_duration:.2f}s")
    print(f"Avg Time/Game:    {(total_duration/num_games)*1000:.2f}ms")
    print("="*60 + "\n")

if __name__ == "__main__":
    count = 1000
    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
        except ValueError:
            pass
    
    run_stress_test(count)
