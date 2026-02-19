"""
This module defines the `Game` class, which implements the graphical user interface (GUI)
for the card game using the Tkinter library. It integrates with the `GameInfo` class to
manage game logic and provides user interaction through buttons, menus, and mouse/keyboard events.

Classes:
    - Game: Implements the GUI for the card game and integrates with game logic.

Author: jordank
Date: April 1, 2025
"""

import os
import re
import sys

from time import time
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from game_info import GameInfo


class Game():
    """Implements a game class."""

    def __init__(self):

        self.pile_label = ['0', '0', '0', '0']
        self.deal_label = '0'
        self.hands_label = '0'
        self.queue_label = '40'
        self.peep_next_label = None
        
        if hasattr(sys, '_MEIPASS'):
            # Bundled by PyInstaller
            self.gif_dir = os.path.join(sys._MEIPASS, "assets/images/")
        else:
            # Development mode
            script_dir = os.path.dirname(os.path.abspath(__file__))
            self.gif_dir = os.path.join(script_dir, "../assets/images/")
            
        self.card_img = []
        self.card_check_boxes = []
        self.card_queue_xypos = []

        self.card_placeholder = None
        self.label_hands = None
        self.label_queue = None
        self.label_piles = [None, None, None, None]
        self.highlight_box = None
        
        self.label_undealt = None
        self.undealt_check_boxes = []

        self.cwd = os.getcwd()

        self.TheGame = GameInfo(self, None)

        self.setup_widgets()

        self.new_game_command()

    def setup_widgets(self):
        """Sets up the Tkinter user interface."""

        self.root = Tk()
        self.root.title('91929')
        self.root.resizable(False, False)
        self.root.configure(bg='#369')

        # Set up menu_bar

        menu_bar = Menu(self.root)

        game_menu = Menu(menu_bar, tearoff=0)
        game_menu.add_command(
            label="New Game", command=self.new_game_command, accelerator="Ctrl+N")
        game_menu.add_command(
            label="Replay", command=self.replay_button_clicked)
        game_menu.add_separator()
        game_menu.add_command(
            label="Save Game", command=self.save_game_clicked)
        game_menu.add_command(
            label="Load Game", command=self.load_game_clicked)
        game_menu.add_separator()
        game_menu.add_command(label="Quit", command=sys.exit)
        menu_bar.add_cascade(label="Game", menu=game_menu)

        self.b_auto_check1 = BooleanVar(self.root, False)
        self.b_auto_play1 = BooleanVar(self.root, False)
        self.b_peep_next_in_queue1 = BooleanVar(self.root, False)
        self.b_display_short_pile1 = BooleanVar(self.root, True)
        self.b_win_game_only1 = BooleanVar(self.root, False)
        self.b_verbose1 = BooleanVar(self.root, True)
        self.auto_play_delay = DoubleVar(self.root, 0.2)

        options_menu = Menu(menu_bar, tearoff=0)
        options_menu.add_checkbutton(label="Assistant Alert", onvalue=True, offvalue=False,
                                     variable=self.b_auto_check1, command=self.toggle_auto_check_option)
        options_menu.add_checkbutton(label="Auto Play", onvalue=True, offvalue=False,
                                     variable=self.b_auto_play1, command=self.toggle_auto_play_option)
        options_menu.add_separator()
        options_menu.add_checkbutton(label="Peep Next", onvalue=True, offvalue=False,
                                     variable=self.b_peep_next_in_queue1, command=self.toggle_peep_next_option)
        options_menu.add_checkbutton(label="Display Short List", onvalue=True, offvalue=False,
                                     variable=self.b_display_short_pile1, command=self.toggle_display_short_list_option)
        options_menu.add_separator()
        options_menu.add_checkbutton(label="Play Win Only Hand", onvalue=True, offvalue=False,
                                     variable=self.b_win_game_only1, command=self.toggle_win_game_only_option)
        options_menu.add_checkbutton(label="Display Detail Info", onvalue=True, offvalue=False,
                                     variable=self.b_verbose1, command=self.toggle_display_detail_info_option)
        
        priority_menu = Menu(options_menu, tearoff=0)
        self.rule_priority_var = StringVar(self.root, "3 > 2 > 1")
        priority_options = [
            ("1 > 2 > 3", [4, 2, 1]),
            ("3 > 2 > 1", [1, 2, 4]),
        ]
        for label, priority in priority_options:
            priority_menu.add_radiobutton(label=label, variable=self.rule_priority_var, 
                                         value=label, command=lambda p=priority: self.set_rule_priority(p))
        options_menu.add_cascade(label="Collection Priority", menu=priority_menu)
        
        menu_bar.add_cascade(label="Options", menu=options_menu)

        help_menu = Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.help_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menu_bar)

        self.b_auto_check = self.b_auto_check1.get()
        self.b_auto_play = self.b_auto_play1.get()
        self.b_peep_next_in_queue = self.b_peep_next_in_queue1.get()
        self.b_win_game_only = self.b_win_game_only1.get()
        self.b_display_short_pile = self.b_display_short_pile1.get()
        self.b_verbose = self.b_verbose1.get()
        self.set_rule_priority([4, 2, 1])
        # self.print_options()

        # Set up card images resource

        self.frontImg = PhotoImage(file="{0}j.gif".format(self.gif_dir))
        self.backimg = PhotoImage(file="{0}b.gif".format(self.gif_dir))

        for card in range(52):
            self.card_img.append(PhotoImage(
                file="{0}%d.gif".format(self.gif_dir) % (card + 1)))

        # application window

        self.card_height = self.backimg.height()
        self.card_width = self.backimg.width()

        self.width_gap = self.card_width // 4
        self.height_gap = self.card_height // 4

        self.window_height = (self.card_height + self.height_gap * 9) * 2
        self.window_width = self.card_width * 6 + self.width_gap * 7 

        self.root.geometry(str(self.window_width) + "x" + str(self.window_height))

        self.canvas = Canvas(self.root, bg="blue", width=self.window_width, height=self.window_height)
        self.canvas.place(x=0, y=0)
        self.canvas.pack()

        self.canvas.bind('<Motion>', self.mouse_move)
        self.canvas.bind('<Button-1>', self.mouse_button1_down)
        
        self.root.bind('<Button-2>', self.mouse_button2_down)
        self.root.bind('<Button-3>', self.mouse_button3_down)
        self.root.bind('<Button-4>', self.mouse_button4_down)
        self.root.bind('<Button-5>', self.mouse_button5_down)

        self.root.bind_all("<Key>", self.keys_event)
        self.root.bind_all("<Return>", self.keys_event)
        self.root.bind_all("<Control-n>", self.new_game_event)

    def initial_gui_ctrls(self):

        # draw pile labels
        for pile in range(4):
            self.draw_label(
                None,
                (self.width_gap + self.card_width) * pile + self.width_gap,
                0,
                self.card_width,
                self.height_gap,
                f"P{pile+1}",
                background='#369',
                text_color='white')

            self.label_piles[pile] = self.draw_label(
                self.label_piles[pile],
                (self.width_gap + self.card_width) * pile + self.width_gap,
                self.height_gap,
                self.card_width,
                self.height_gap,
                '0')

        # draw peep next card
        x1 = (self.width_gap + self.card_width) * 4 + self.width_gap + self.card_width // 2
        y1 = self.height_gap * 3 + self.card_height // 2

        image = self.backimg
        self.peep_next_label = self.draw_card(self.peep_next_label, x1, y1, image)

        # draw hands count label
        self.draw_label(
            None,
            (self.width_gap + self.card_width) * 4 + self.width_gap,
            0,
            self.card_width,
            self.height_gap,
            "HANDS",
            background='#369',
            text_color='white')

        self.label_hands = self.draw_label(
            self.label_hands,
            (self.width_gap + self.card_width) * 4 + self.width_gap,
            self.height_gap,
            self.card_width,
            self.height_gap,
            '0')

        # draw card in queue label
        bx = (self.width_gap + self.card_width) * 4 + self.width_gap
        h2 = self.height_gap * 2

        self.label_queue = self.draw_label(
            self.label_queue,
            bx,
            self.window_height - h2 * 4 - self.height_gap - 24,
            self.card_width,
            self.height_gap,
            '40')
            
        dx = (self.width_gap + self.card_width) * 5 + self.width_gap
        self.draw_label(
            None,
            dx,
            0,
            self.card_width,
            self.height_gap,
            "DEBUG",
            background='#369',
            text_color='white')

        self.label_undealt = self.draw_label(
            self.label_undealt,
            dx,
            self.height_gap,
            self.card_width,
            self.height_gap,
            "UNDEALT")

        self.deal_card_box = self.canvas.create_image(
            bx + self.card_width // 2, 
            self.window_height - h2 * 6 - 30 + h2 // 2, 
            image=self.backimg, 
            tags="deal_card"
        )
        self.canvas.tag_bind("deal_card", "<Button-1>", lambda e: self.deal_button_clicked())

        self.rewind_button = Button(
            self.canvas, text="Rewind", command=self.smart_undo_button_clicked)
        self.rewind_button.place(x=bx, y=self.window_height - h2 * 2 - 8, width=self.card_width, height=h2)

        self.undo_button = Button(
            self.canvas, text="Undo", command=self.undo_button_clicked)
        self.undo_button.place(x=bx, y=self.window_height - h2 - 4, width=self.card_width, height=h2)

        self.draw_label(
            None,
            dx,
            self.window_height - h2 * 2 - 8,
            self.card_width,
            self.height_gap,
            "DELAY (s)",
            background='#369',
            text_color='white')
            
        self.delay_spinbox = Spinbox(self.root, from_=0.0, to=5.0, increment=0.1, format="%.1f",
                                     textvariable=self.auto_play_delay)
        self.delay_spinbox.place(x=dx, y=self.window_height - h2 - 4, width=self.card_width, height=h2)

    def is_in_inner_canvas(self, x, y):
        x1 = self.width_gap
        y1 = self.height_gap * 3
        x2 = x1 + self.width_gap * 3 + self.card_width * 4
        y2 = y1 + self.height_gap * 5 + self.card_height
        return True if (x1 < x < x2) and (y1 < y < y2) else False

    def is_in_pile_n(self, x, y):
        for pile in range(4):
            if (self.width_gap + (self.width_gap + self.card_width) * pile < x < (self.width_gap + self.card_width) * (pile + 1)):
                return pile
        return -1

    def mouse_move(self, event):
        pile = self.is_in_pile_n(event.x, event.y)
        if (self.is_in_inner_canvas(event.x, event.y)):
            if pile >= 0:
                y_in_pile_area = event.y - self.height_gap * 3
                i = int(y_in_pile_area / self.height_gap)
                cards_in_pile = len(self.TheGame.card_piles[pile].rg_cards)
                if cards_in_pile > 0:
                    if self.b_display_short_pile and cards_in_pile > 5:
                        if i >= 6: i = 5
                    else:
                        if i >= cards_in_pile: i = cards_in_pile - 1
                    if i < 0: i = 0
                    xx = (self.width_gap + self.card_width) * pile + self.width_gap
                    yy = self.height_gap * (i+3)
                    x1, y1 = xx, yy
                    x2, y2 = xx + self.card_width, yy + self.card_height
                    if self.highlight_box is None:
                        self.highlight_box = self.canvas.create_rectangle(x1, y1, x2, y2, outline="red", width=3)
                    else:
                        self.canvas.coords(self.highlight_box, x1, y1, x2, y2)
                        self.canvas.tag_raise(self.highlight_box)
                else:
                    if self.highlight_box:
                        self.canvas.delete(self.highlight_box)
                        self.highlight_box = None
            else:
                if self.highlight_box:
                    self.canvas.delete(self.highlight_box)
                    self.highlight_box = None
        else:
            if self.highlight_box:
                self.canvas.delete(self.highlight_box)
            self.highlight_box = None

    def mouse_button1_down(self, event):
        if self.is_in_inner_canvas(event.x, event.y):
            pile_idx = self.is_in_pile_n(event.x, event.y)
            if pile_idx >= 0:
                self.collect_from_pile(pile_idx)

    def mouse_button2_down(self, event): pass
    def mouse_button3_down(self, event): pass
    def mouse_button4_down(self, event): pass
    def mouse_button5_down(self, event): pass

    def keys_event(self, event):
        if event.keysym == 'Return':
            self.deal_button_clicked()
        elif event.char == ' ':
            self.collect_button_clicked()
        elif event.char in ['1', '2', '3']:
            self.handle_digit_key(event.char)
        elif event.char in ['q', 'w', 'e', 'r']:
            pile_idx = {'q': 0, 'w': 1, 'e': 2, 'r': 3}[event.char]
            self.collect_from_pile(pile_idx)
        elif event.keysym == 'Escape':
            if self.b_auto_play:
                self.b_auto_play = False
                self.b_auto_play1.set(False)
            
    def handle_digit_key(self, char):
        rule_map = {'1': 4, '2': 2, '3': 1}
        rule_id = rule_map.get(char)
        self.apply_rule_to_pile(rule_id, self.TheGame.current_pile, char)

    def apply_rule_to_pile(self, rule_id, pile_idx, char_label):
        pile = self.TheGame.card_piles[pile_idx]
        non_empty_piles = [p for p in self.TheGame.card_piles if not p.b_pile_empty]
        next_card_is_3 = False
        if self.TheGame.card_queue.n_count > 0:
            if (int(self.TheGame.card_queue.rg_cards[0] / 4) + 1) == 3:
                next_card_is_3 = True
        is_last_pile = len(non_empty_piles) == 1 and \
                       (self.TheGame.cnt_hands < 40 or (self.TheGame.card_queue.n_count > 0 and not next_card_is_3))
        mask = pile.try_collect_cards(self.TheGame.card_queue, False, self.TheGame.rule_priority, is_last_pile)
        if mask & rule_id:
            pile.collect_rule(rule_id, self.TheGame.card_queue)
            self.render_cards()
            return True
        return False

    def new_game_event(self, event):
        self.new_game_command()

    def new_game_command(self):
        self.initial_gui_ctrls()
        self.TheGame.start_game(True)
        self.render_cards()

    def replay_button_clicked(self):
        self.initial_gui_ctrls()
        self.TheGame.start_game(False)
        self.render_cards()

    def load_game_clicked(self):
        filepath = filedialog.askopenfilename(initialdir=self.cwd, title="Select file",
                                             filetypes=(("Game Save Files", "*.json"), ("All files", "*.*")),
                                             defaultextension=[("Game Save Files", "*.json")])
        if filepath:
            try:
                self.TheGame.load_game_state(filepath)
                self.render_cards()
                messagebox.showinfo("Load Game", "Game loaded successfully!")
            except Exception as ex:
                messagebox.showerror("Load Game Error", f"Error loading game: {ex}")

    def save_game_clicked(self):
        filepath = filedialog.asksaveasfilename(initialdir=self.cwd, title="Save Game As",
                                               filetypes=(("Game Save Files", "*.json"), ("All files", "*.*")),
                                               defaultextension=[("Game Save Files", "*.json")])
        if filepath:
            try:
                self.TheGame.save_game_state(filepath)
                messagebox.showinfo("Save Game", "Game saved successfully!")
            except Exception as ex:
                messagebox.showerror("Save Game Error", f"Error saving game: {ex}")

    def auto_save_if_over(self):
        if self.TheGame.b_done and not self.TheGame.b_auto_saved:
            self.TheGame.b_auto_saved = True
            status = "win" if self.TheGame.b_win else "bad"
            filename = f"{self.TheGame.cnt_hands} ({status}).json"
            filepath = os.path.join(self.cwd, filename)
            try:
                self.TheGame.save_game_state(filepath)
            except Exception: pass

    def check_and_report_win(self):
        self.TheGame.check_win_status()
        if self.TheGame.b_win:
            self.render_cards()
            messagebox.showinfo("Victory!", "Congratulations! You have won the game!\nThe next card is indeed a 3.")
            self.auto_save_if_over()
            return True
        return False

    def animate_move(self, image, x1, y1, x2, y2, steps=12, delay=15, callback=None):
        item = self.canvas.create_image(x1, y1, image=image)
        dx, dy = (x2 - x1) / steps, (y2 - y1) / steps
        def step(count):
            if count < steps:
                self.canvas.move(item, dx, dy)
                self.canvas.update()
                self.root.after(delay, lambda: step(count + 1))
            else:
                self.canvas.delete(item)
                if callback: callback()
        step(0)

    def deal_button_clicked(self):
        if self.b_auto_check:
            missed = []
            non_empty_piles = [p for p in self.TheGame.card_piles if not p.b_pile_empty]
            next_card_is_3 = False
            if self.TheGame.card_queue.n_count > 0:
                if (int(self.TheGame.card_queue.rg_cards[0] / 4) + 1) == 3:
                    next_card_is_3 = True
            is_last_pile = len(non_empty_piles) == 1 and \
                           (self.TheGame.cnt_hands < 40 or (self.TheGame.card_queue.n_count > 0 and not next_card_is_3))
            for i in range(4):
                mask = self.TheGame.card_piles[i].try_collect_cards(self.TheGame.card_queue, False, self.TheGame.rule_priority, is_last_pile)
                if mask > 0: missed.append((i, mask))
            if missed:
                dlg = self.show_assistant_alert(missed)
                self.root.wait_window(dlg)
                return

        if not self.TheGame.b_done and self.TheGame.card_queue.n_count > 0:
            next_pile_idx = (self.TheGame.current_pile + 1) % 4
            checked = 0
            while self.TheGame.card_piles[next_pile_idx].b_pile_empty and checked < 4:
                next_pile_idx = (next_pile_idx + 1) % 4
                checked += 1
            if checked == 4:
                self.check_and_report_win()
                return
            bx = (self.width_gap + self.card_width) * 4 + self.width_gap
            h2 = self.height_gap * 2
            start_x, start_y = bx + self.card_width // 2, self.window_height - h2 * 6 - 30 + h2 // 2
            dest_x = (self.width_gap + self.card_width) * next_pile_idx + self.width_gap + self.card_width // 2
            cards_in_dest = len(self.TheGame.card_piles[next_pile_idx].rg_cards)
            display_idx = min(cards_in_dest, 5) if self.b_display_short_pile else cards_in_dest
            dest_y = self.height_gap * (display_idx + 3) + self.card_height // 2
            card_val = self.TheGame.card_queue.rg_cards[0]
            image = self.card_img[card_val]
            def after_deal_anim():
                if self.TheGame.deal_one_card(True):
                    self.render_cards()
                    self.check_and_report_win()
                    if self.b_auto_play:
                        self.finish_auto_collect()
                else:
                    self.TheGame.check_win_status()
                    self.auto_save_if_over()
            self.animate_move(image, start_x, start_y, dest_x, dest_y, callback=after_deal_anim)
        else:
            self.TheGame.check_win_status()
            self.auto_save_if_over()

    def finish_auto_collect(self):
        self.render_cards()
        moved = True
        while moved:
            if not self.b_auto_play: break
            moved = False
            non_empty_piles = [p for p in self.TheGame.card_piles if not p.b_pile_empty]
            next_card_is_3 = False
            if self.TheGame.card_queue.n_count > 0:
                if (int(self.TheGame.card_queue.rg_cards[0] / 4) + 1) == 3:
                    next_card_is_3 = True
            is_last_pile = len(non_empty_piles) == 1 and \
                           (self.TheGame.cnt_hands < 40 or (self.TheGame.card_queue.n_count > 0 and not next_card_is_3))
            for i in range(4):
                collectable_mask = self.TheGame.card_piles[i].try_collect_cards(self.TheGame.card_queue, False, self.TheGame.rule_priority, is_last_pile)
                if collectable_mask > 0:
                    rule_to_apply = 0
                    for r in self.TheGame.rule_priority:
                        if collectable_mask & r:
                            rule_to_apply = r
                            break
                    if rule_to_apply > 0:
                        delay_ms = int(self.auto_play_delay.get() * 1000)
                        self.root.after(delay_ms, lambda: self.animate_collection(i, rule_to_apply, lambda: self.finish_auto_collect()))
                        moved = True
                        return
            if not moved:
                if self.b_auto_play and not self.TheGame.b_done:
                    delay_ms = int(self.auto_play_delay.get() * 1000)
                    self.root.after(delay_ms, self.deal_button_clicked)
                else:
                    self.TheGame.play_game_automatically(True)
                    self.render_cards()
                    if self.TheGame.b_done: self.auto_save_if_over()

    def animate_collection(self, pile_idx, rule_id, callback=None):
        pile = self.TheGame.card_piles[pile_idx]
        n = pile.n_card_count
        indices = []
        if rule_id == 4: indices = [0, 1, n - 1]
        elif rule_id == 2: indices = [0, n - 2, n - 1]
        elif rule_id == 1: indices = [n - 3, n - 2, n - 1]
        if not indices:
            if callback: callback()
            return
        bx = (self.width_gap + self.card_width) * 4 + self.width_gap
        h2 = self.height_gap * 2
        dest_x, dest_y = bx + self.card_width // 2, self.window_height - h2 * 4 - self.height_gap - 24 + self.height_gap // 2
        pile_x = (self.width_gap + self.card_width) * pile_idx + self.width_gap + self.card_width // 2
        cards_to_animate = []
        for idx in indices:
            card_val = pile.rg_cards[idx]
            display_idx = idx
            if self.b_display_short_pile and n > 5:
                if idx < 2: display_idx = idx
                elif idx == n-1: display_idx = 5
                elif idx == n-2: display_idx = 4
                elif idx == n-3: display_idx = 3
                else: continue
            y = self.height_gap * (display_idx + 3) + self.card_height // 2
            cards_to_animate.append((self.card_img[card_val], y))
        completed = [0]
        def on_one_done():
            completed[0] += 1
            if completed[0] == len(cards_to_animate):
                pile.collect_rule(rule_id, self.TheGame.card_queue)
                if callback: callback()
        for img, y in cards_to_animate:
            self.animate_move(img, pile_x, y, dest_x, dest_y, steps=15, callback=on_one_done)

    def collect_button_clicked(self):
        if self.b_auto_play: self.finish_auto_collect()
        else: self.collect_from_pile(self.TheGame.current_pile)

    def collect_from_pile(self, pile_idx):
        pile = self.TheGame.card_piles[pile_idx]
        non_empty_piles = [p for p in self.TheGame.card_piles if not p.b_pile_empty]
        next_card_is_3 = False
        if self.TheGame.card_queue.n_count > 0:
            if (int(self.TheGame.card_queue.rg_cards[0] / 4) + 1) == 3:
                next_card_is_3 = True
        is_last_pile = len(non_empty_piles) == 1 and \
                       (self.TheGame.cnt_hands < 40 or (self.TheGame.card_queue.n_count > 0 and not next_card_is_3))
        collectable = pile.try_collect_cards(self.TheGame.card_queue, False, self.TheGame.rule_priority, is_last_pile)
        if collectable == 0: return
        dlg = self.show_collection_dialog(collectable, pile_idx)
        self.root.wait_window(dlg)
        self.render_cards()
        self.check_and_report_win()
        if self.TheGame.b_done: self.auto_save_if_over()

    def center_window(self, win):
        win.update_idletasks()
        root_w, root_h, root_x, root_y = self.root.winfo_width(), self.root.winfo_height(), self.root.winfo_x(), self.root.winfo_y()
        win_w, win_h = win.winfo_width(), win.winfo_height()
        x, y = root_x + (root_w // 2) - (win_w // 2), root_y + (root_h // 2) - (win_h // 2)
        win.geometry(f"+{x}+{y}")

    def show_collection_dialog(self, mask, pile_idx):
        dialog = Toplevel(self.root)
        dialog.title(f"Choose Move - Pile {pile_idx}")
        dialog.transient(self.root)
        dialog.grab_set()
        Label(dialog, text="Choose Move", font=("Arial", 10, "bold"), pady=10).pack(side=TOP)
        pile = self.TheGame.card_piles[pile_idx]
        def select(rule_id):
            dialog.destroy()
            self.animate_collection(pile_idx, rule_id, lambda: self.render_cards())
        best_p_idx, best_rule = (None, 0)
        non_empty_piles = [p for p in self.TheGame.card_piles if not p.b_pile_empty]
        next_card_is_3 = False
        if self.TheGame.card_queue.n_count > 0:
            if (int(self.TheGame.card_queue.rg_cards[0] / 4) + 1) == 3:
                next_card_is_3 = True
        is_last_pile = len(non_empty_piles) == 1 and \
                       (self.TheGame.cnt_hands < 40 or (self.TheGame.card_queue.n_count > 0 and not next_card_is_3))
        for i in range(4):
            m_mask = self.TheGame.card_piles[i].try_collect_cards(self.TheGame.card_queue, False, self.TheGame.rule_priority, is_last_pile)
            for r in self.TheGame.rule_priority:
                if m_mask & r:
                    best_p_idx, best_rule = (i, r)
                    break
            if best_p_idx is not None: break
        options_container = Frame(dialog)
        options_container.pack(expand=True, fill=BOTH, padx=10, pady=10)
        rules_meta_data = {
            1: ("3", lambda p: [p[-3], p[-2], p[-1]]),
            2: ("2", lambda p: [p[0], None, p[-2], p[-1]] if len(p) > 3 else [p[0], p[1], p[2]]),
            4: ("1", lambda p: [p[0], p[1], None, p[-1]] if len(p) > 3 else [p[0], p[1], p[2]])
        }
        for r_id in self.TheGame.rule_priority:
            if mask & r_id:
                label_char, get_display_list = rules_meta_data[r_id]
                is_rec = (best_p_idx == pile_idx and best_rule == r_id)
                opt_frame = Frame(options_container, bd=2, relief=GROOVE, bg="#dfd" if is_rec else "#f0f0f0")
                opt_frame.pack(side=LEFT, padx=5, fill=Y)
                btn_txt = f"Option {label_char}" + ("\n(Recommended)" if is_rec else "")
                Button(opt_frame, text=btn_txt, command=lambda r=r_id: select(r),
                       bg="#afa" if is_rec else "white", font=("Arial", 9, "bold")).pack(side=TOP, pady=5, fill=X)
                display_list = get_display_list(pile.rg_cards)
                c_width, c_height = self.card_width + 10, self.card_height + (len(display_list) - 1) * self.height_gap + 10
                canv = Canvas(opt_frame, width=c_width, height=c_height, bg="#dfd" if is_rec else "#f0f0f0", highlightthickness=0)
                canv.pack(pady=10)
                for i, card_val in enumerate(display_list):
                    img = self.card_img[card_val] if card_val is not None else self.backimg
                    canv.create_image(c_width//2, self.card_height//2 + i * self.height_gap + 5, image=img)
                canv.bind("<Button-1>", lambda e, r=r_id: select(r))
        dialog.bind("1", lambda e: select(4) if mask & 4 else None)
        dialog.bind("2", lambda e: select(2) if mask & 2 else None)
        dialog.bind("3", lambda e: select(1) if mask & 1 else None)
        dialog.bind("<Escape>", lambda e: dialog.destroy())
        self.center_window(dialog)
        return dialog

    def show_assistant_alert(self, missed_info):
        dialog = Toplevel(self.root)
        dialog.title("Assistant Alert")
        dialog.transient(self.root)
        dialog.grab_set()
        Label(dialog, text="Missed Moves", font=("Arial", 12, "bold"), fg="red", pady=15).pack(side=TOP)
        main_frame = Frame(dialog)
        main_frame.pack(expand=True, fill=BOTH, padx=10, pady=10)
        content_frame = Frame(main_frame)
        content_frame.pack(side=TOP, fill=BOTH, expand=True)
        rules_meta_data = {
            1: ("3", lambda p: [p[-3], p[-2], p[-1]]),
            2: ("2", lambda p: [p[0], None, p[-2], p[-1]] if len(p) > 3 else [p[0], p[1], p[2]]),
            4: ("1", lambda p: [p[0], p[1], None, p[-1]] if len(p) > 3 else [p[0], p[1], p[2]])
        }
        def select(p_idx, r_id):
            dialog.destroy()
            self.animate_collection(p_idx, r_id, lambda: self.render_cards())
        for pile_idx, mask in missed_info:
            pile = self.TheGame.card_piles[pile_idx]
            pile_frame = Frame(content_frame, bd=1, relief=SOLID, padx=5, pady=5)
            pile_frame.pack(side=TOP, pady=10, fill=X)
            Label(pile_frame, text=f"Pile {pile_idx}", font=("Arial", 10, "bold")).pack(side=LEFT, padx=5)
            rules_container = Frame(pile_frame)
            rules_container.pack(side=LEFT, expand=True, fill=X)
            for r_id in self.TheGame.rule_priority:
                if mask & r_id:
                    label_char, get_display_list = rules_meta_data[r_id]
                    opt_frame = Frame(rules_container, bd=1, relief=RIDGE, padx=5, pady=5)
                    opt_frame.pack(side=LEFT, padx=5)
                    Button(opt_frame, text=f"Collect Rule {label_char}", command=lambda p=pile_idx, r=r_id: select(p, r), font=("Arial", 8)).pack(side=TOP, pady=2)
                    display_list = get_display_list(pile.rg_cards)
                    canv = Canvas(opt_frame, width=self.card_width + 10, height=self.card_height + (len(display_list)-1)*self.height_gap + 10, highlightthickness=0)
                    canv.pack(pady=5)
                    for i, card_val in enumerate(display_list):
                        img = self.card_img[card_val] if card_val is not None else self.backimg
                        canv.create_image(self.card_width//2 + 5, self.card_height//2 + i * self.height_gap + 5, image=img)
                    canv.bind("<Button-1>", lambda e, p=pile_idx, r=rule_id: select(p, r))
        Button(dialog, text="Cancel / Go Back", command=dialog.destroy, height=2, bg="#fbb").pack(side=BOTTOM, fill=X, padx=20, pady=10)
        self.center_window(dialog)
        return dialog

    def undo_button_clicked(self):
        self.TheGame.pop_stack_operations()
        self.render_cards()

    def smart_undo_button_clicked(self):
        self.root.config(cursor="watch")
        self.root.update()
        try:
            rewound_count = 0
            while len(self.TheGame.rg_stack_operation) > 0:
                has_move = False
                non_empty_piles = [p for p in self.TheGame.card_piles if not p.b_pile_empty]
                next_card_is_3 = False
                if self.TheGame.card_queue.n_count > 0:
                    if (int(self.TheGame.card_queue.rg_cards[0] / 4) + 1) == 3: next_card_is_3 = True
                is_last_pile = len(non_empty_piles) == 1 and \
                               (self.TheGame.cnt_hands < 40 or (self.TheGame.card_queue.n_count > 0 and not next_card_is_3))
                for i in range(4):
                    if self.TheGame.card_piles[i].try_collect_cards(self.TheGame.card_queue, False, self.TheGame.rule_priority, is_last_pile) > 0:
                        has_move = True
                        break
                if has_move: break
                self.TheGame.pop_stack_operations()
                rewound_count += 1
            self.render_cards()
        finally:
            self.root.config(cursor="")

    def toggle_auto_check_option(self): self.b_auto_check = self.b_auto_check1.get()
    def toggle_auto_play_option(self): self.b_auto_play = self.b_auto_play1.get()
    def toggle_win_game_only_option(self): self.b_win_game_only = self.b_win_game_only1.get()
    def toggle_peep_next_option(self):
        self.b_peep_next_in_queue = self.b_peep_next_in_queue1.get()
        self.render_peep_card_in_queue(self.b_peep_next_in_queue)
    def toggle_display_short_pile_option(self):
        self.b_display_short_pile = self.b_display_short_pile1.get()
        self.render_cards()
    def toggle_display_short_list_option(self):
        self.b_display_short_pile = self.b_display_short_pile1.get()
        self.render_cards()
    def toggle_display_detail_info_option(self): self.b_verbose = self.b_verbose1.get()
    def set_rule_priority(self, priority): self.TheGame.rule_priority = priority

    def draw_card(self, card, x, y, image):
        if card: self.canvas.delete(card)
        card = self.canvas.create_image(x, y, image=image)
        self.canvas.addtag_withtag('image', card)
        return card

    def draw_label(self, label, x, y, w, h, text, background='white', text_color='#000'):
        if label: self.canvas.delete(label)
        self.canvas.create_rectangle(x, y, x + w, y + h, fill=background)
        return self.canvas.create_text(x + w / 2, y + h / 2, text=text, fill=text_color)

    def render_peep_card_in_queue(self, b_peep_next_in_queue=True):
        x1, y1 = (self.width_gap + self.card_width) * 4 + self.width_gap + self.card_width // 2, self.height_gap * 3 + self.card_height // 2
        if (self.b_peep_next_in_queue or self.TheGame.b_win) and len(self.TheGame.card_queue.rg_cards) > 0:
            image = self.card_img[self.TheGame.card_queue.rg_cards[0]]
            self.peep_next_label = self.draw_card(self.peep_next_label, x1, y1, image)
        else:
            if self.peep_next_label: self.canvas.delete(self.peep_next_label)
            self.peep_next_label = None

    def render_cards(self):
        for card in self.card_check_boxes + self.undealt_check_boxes: self.canvas.delete(card)
        self.card_check_boxes.clear()
        self.undealt_check_boxes.clear()
        for pile in range(4):
            cards_in_deck = len(self.TheGame.card_piles[pile].rg_cards)
            if self.label_piles[pile]: self.canvas.delete(self.label_piles[pile])
            non_empty_piles = [p for p in self.TheGame.card_piles if not p.b_pile_empty]
            next_card_is_3 = False
            if self.TheGame.card_queue.n_count > 0:
                if (int(self.TheGame.card_queue.rg_cards[0] / 4) + 1) == 3: next_card_is_3 = True
            is_last_pile = len(non_empty_piles) == 1 and \
                           (self.TheGame.cnt_hands < 40 or (self.TheGame.card_queue.n_count > 0 and not next_card_is_3))
            mask = self.TheGame.card_piles[pile].try_collect_cards(self.TheGame.card_queue, False, self.TheGame.rule_priority, is_last_pile)
            bg, fg = 'white', '#0F0'
            if pile == self.TheGame.current_pile: bg, fg = 'yellow', '#F00'
            elif mask > 0: bg, fg = '#ADD8E6', '#00F'
            self.label_piles[pile] = self.draw_label(None, (self.width_gap + self.card_width) * pile + self.width_gap, self.height_gap, self.card_width, self.height_gap, str(cards_in_deck), background=bg, text_color=fg)
            display_indices = range(min(cards_in_deck, 6)) if self.b_display_short_pile and cards_in_deck > 5 else range(cards_in_deck)
            for i in display_indices:
                xx = (self.width_gap + self.card_width) * pile + self.width_gap
                yy = self.height_gap * (i+3)
                if self.b_display_short_pile and cards_in_deck > 5:
                    if i < 2: card_val = self.TheGame.card_piles[pile].rg_cards[i]
                    elif i == 2: image = self.backimg
                    else: card_val = self.TheGame.card_piles[pile].rg_cards[i + (cards_in_deck - 6)]
                else: card_val = self.TheGame.card_piles[pile].rg_cards[i]
                if not (self.b_display_short_pile and cards_in_deck > 5 and i == 2):
                    image = self.card_img[card_val]
                self.card_check_boxes.append(self.draw_card(None, xx + self.card_width // 2, yy + self.card_height // 2, image))
        self.label_hands = self.draw_label(self.label_hands, (self.width_gap + self.card_width) * 4 + self.width_gap, self.height_gap, self.card_width, self.height_gap, str(self.TheGame.cnt_hands))
        bx, h2 = (self.width_gap + self.card_width) * 4 + self.width_gap, self.height_gap * 2
        self.label_queue = self.draw_label(self.label_queue, bx, self.window_height - h2 * 4 - self.height_gap - 24, self.card_width, self.height_gap, str(self.TheGame.card_queue.n_count))
        dx = (self.width_gap + self.card_width) * 5 + self.width_gap
        total_undealt = len(self.TheGame.card_queue.rg_cards)
        if total_undealt > 0:
            indices = [(j, True) for j in range(min(total_undealt, 12))] if total_undealt <= 12 else [(j, True) for j in range(6)] + [(6, False)] + [(j, True) for j in range(total_undealt - 6, total_undealt)]
            for idx, (deck_idx, reveal) in enumerate(indices):
                image = self.card_img[self.TheGame.card_queue.rg_cards[deck_idx]] if reveal else self.backimg
                self.undealt_check_boxes.append(self.draw_card(None, dx + self.card_width // 2, self.height_gap * (idx + 3) + self.card_height // 2, image))
        self.render_peep_card_in_queue()
        self.root.update()

    def help_about(self): pass

    def print_deck(self):
        print("Deck:", [self.TheGame.cards.rg_card_face[card]
              for card in self.TheGame.cards.rg_cards])

    def print_game_info(self):
        if self.b_verbose:
            print("Total Hands:", self.TheGame.cnt_hands, ", Current Pile:", self.TheGame.current_pile, ", Card Queue:",
                  self.TheGame.card_queue.n_count)

    def print_pile(self, pile):
        if self.b_verbose:
            self.print_one_pile(pile, self.TheGame.current_pile)

    def print_current_pile(self):
        if self.b_verbose:
            self.print_pile(self.TheGame.current_pile)

    def print_all_piles(self):
        if self.b_verbose:
            for pile in range(0, 4):
                self.print_pile(pile)

    def print_one_pile(self, pile, current_pile):
        if self.b_verbose:
            s_prompt = ">Pile" if pile == current_pile else " Pile"
            print(s_prompt, pile, ":", len(self.TheGame.card_piles[pile].rg_cards),
                  [self.TheGame.cards.rg_card_face[card] for card in self.TheGame.card_piles[pile].rg_cards])

    def print_piles(self, current_pile):
        if self.b_verbose:
            for pile in range(4):
                self.print_one_pile(pile, current_pile)

    def print_queue(self):
        if self.b_verbose:
            print("CardQ:", self.TheGame.card_queue.n_count,
                  [self.TheGame.cards.rg_card_face[card] for card in self.TheGame.card_queue.rg_cards])
            
    def print_peep_next_in_queue(self):
        if self.b_verbose and len(self.TheGame.card_queue.rg_cards) > 0:
            print(self.TheGame.cards.rg_card_face[self.TheGame.card_queue.rg_cards[0]])

    def print_options(self):
        if self.b_verbose:
            print("Assistant Alert:", self.b_auto_check)
            print("Auto Run:", self.b_auto_play)
            print("Peep Next In Queue:", self.b_peep_next_in_queue)
            print("Play Win Only Hand:", self.b_win_game_only)
            print("Display Short List:", self.b_display_short_pile)
            print("Display Detail Info:", self.b_verbose)
