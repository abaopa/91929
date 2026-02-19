import os
import sys
import time
from tkinter import messagebox

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from game_ui import Game

class UIStressTest(Game):
    def __init__(self, num_games=10):
        # Prevent messagebox from blocking
        self.original_showinfo = messagebox.showinfo
        messagebox.showinfo = lambda title, message: print(f"[UI] {title}: {message}")
        
        super().__init__()
        self.target_games = num_games
        self.games_completed = 0
        self.wins = 0
        self.losses = 0
        self.start_time = time.time()
        
        # Configure for rapid auto-play
        self.b_auto_play1.set(True)
        self.b_auto_play = True
        self.auto_play_delay.set(0.0) # No delay between moves for stress test
        self.b_verbose1.set(False)
        self.b_verbose = False
        
        print("\n" + "="*60)
        print("91929 UI STRESS TEST")
        print(f"Target Games: {self.target_games}")
        print("="*60 + "\n")
        
        self.run_test_loop()

    def run_test_loop(self):
        while self.games_completed < self.target_games:
            # 1. Start a new game (resets deck and piles)
            self.new_game_command()
            
            # 2. Kickstart the auto-play by triggering the first deal
            # In Game class, deal_button_clicked starts a chain of .after() 
            # calls if b_auto_play is True.
            self.deal_button_clicked()
            
            # 3. Wait for the current game to finish
            while not self.TheGame.b_done:
                try:
                    self.root.update()
                except:
                    # Handle window close during test
                    self.report_results()
                    sys.exit(0)
                
                # Check if it got stuck (shouldn't happen with b_auto_play=True)
                # but if n_count > 0 and not b_done and nothing is happening, kick it.
                # However, deal_button_clicked is async via .after.
                time.sleep(0.01) # Tiny sleep to avoid 100% CPU in the update loop
                
            self.games_completed += 1
            if self.TheGame.b_win:
                self.wins += 1
            else:
                self.losses += 1
                
            win_rate = (self.wins / self.games_completed) * 100
            print(f"Game {self.games_completed:3}/{self.target_games} | Win Rate: {win_rate:6.2f}% | Current Status: {'WIN' if self.TheGame.b_win else 'LOSS'}")

        self.report_results()
        self.root.destroy()

    def report_results(self):
        end_time = time.time()
        duration = end_time - self.start_time
        print("\n" + "="*60)
        print("UI STRESS TEST RESULTS")
        print("="*60)
        print(f"Total Games:      {self.games_completed}")
        print(f"Total Wins:       {self.wins}")
        print(f"Total Losses:     {self.losses}")
        if self.games_completed > 0:
            print(f"Win Rate:         {(self.wins/self.games_completed)*100:.2f}%")
            print(f"Avg Time/Game:    {(duration/self.games_completed):.2f}s")
        print(f"Total Time:       {duration:.2f}s")
        print("="*60 + "\n")

if __name__ == "__main__":
    count = 10
    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
        except ValueError:
            pass
    
    # Run the test
    UIStressTest(count)
