import os
import re
import sys

from tkinter import *
# from tkinter import Tk, Menu, Label, Button, Entry, sys, PhotoImage, Frame, Checkbutton, Canvas
# from tkinter import N, E, S, self.card_width, SUNKEN, RAISED, NORMAL, DISABLED, NE
# from tkinter import StringVar, Toplevel, mainloop
# from tkinter import messagebox
from tkinter import filedialog
from turtle import color
from typing import List, Any

# import game_info
from game_info import GameInfo

class Game():
    """Implements a game class."""

    pile_label: List[str]
    deal_label: str
    hands_label: str
    queue_label: str
    peep_next_label: str

    gif_dir: str

    card_img: List[Any]
    card_check_boxes: List[Any]

    b_auto_play: bool
    b_auto_check: bool
    b_peep_next_in_queue: bool
    b_display_short_pile: bool
    b_win_game_only: bool
    b_verbose: bool

    def __init__(self):

        self.pile_label = ['0', '0', '0', '0']
        self.deal_label = '0'
        self.hands_label = '0'
        self.queue_label = '40'
        self.peep_next_label = None
        self.gif_dir = "./images/"
        self.card_img = []
        self.card_check_boxes = []
        self.card_queue_xypos = []

        self.card_placeholder = None
        self.label_hands = None
        self.label_queue = None
        self.label_piles = [None, None, None, None]

        self.cwd = os.getcwd()

        self.TheGame = GameInfo(None, self)

        """Instance initialization function."""

        # Set up variables

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
        game_menu.add_command(label="New Game", command=self.new_game_command, accelerator="Ctrl+N")
        game_menu.add_command(label="Replay", command=self.replay_button_clicked)
        game_menu.add_separator()
        game_menu.add_command(label="Save Game", command=self.save_game_clicked)
        game_menu.add_command(label="Load Game", command=self.load_game_clicked)
        game_menu.add_separator()
        game_menu.add_command(label="Quit", command=sys.exit)
        menu_bar.add_cascade(label="Game", menu=game_menu)

        self.b_auto_check1 = BooleanVar(self.root, False)
        self.b_auto_play1 = BooleanVar(self.root, False)
        self.b_peep_next_in_queue1 = BooleanVar(self.root, False)
        self.b_display_short_pile1 = BooleanVar(self.root, True)
        self.b_win_game_only1 = BooleanVar(self.root, True)        
        self.b_verbose1 = BooleanVar(self.root, True)    

        options_menu = Menu(menu_bar, tearoff=0)
        options_menu.add_checkbutton(label="Auto Check", onvalue=True, offvalue=False, variable=self.b_auto_check1, command=self.toggle_auto_check_option)
        options_menu.add_checkbutton(label="Auto Play", onvalue=True, offvalue=False, variable=self.b_auto_play1, command=self.toggle_auto_play_option)
        options_menu.add_separator()
        options_menu.add_checkbutton(label="Peep Next", onvalue=True, offvalue=False, variable=self.b_peep_next_in_queue1, command=self.toggle_peep_next_option)
        options_menu.add_checkbutton(label="Display Short List", onvalue=True, offvalue=False, variable=self.b_display_short_pile1, command=self.toggle_display_short_list_option)
        options_menu.add_separator()         
        options_menu.add_checkbutton(label="Play Win Only Hand", onvalue=True, offvalue=False, variable=self.b_win_game_only1, command=self.toggle_win_game_only_option)                                         
        options_menu.add_checkbutton(label="Display Detail Info", onvalue=True, offvalue=False, variable=self.b_verbose1, command=self.toggle_display_detail_info_option)    
        menu_bar.add_cascade(label="Options", menu=options_menu)

        help_menu = Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.help_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menu_bar)
  
        # mouse and keyboard event handlers

        self.root.bind('<Motion>', self.mouse_move)
        self.root.bind('<Button-1>', self.mouse_button1_down)
        self.root.bind('<Button-2>', self.mouse_button2_down)
        self.root.bind('<Button-3>', self.mouse_button3_down)
        self.root.bind('<Button-4>', self.mouse_button4_down)
        self.root.bind('<Button-5>', self.mouse_button5_down)

        self.root.bind_all("<Key>", self.keys_event)
        self.root.bind_all("<Return>", self.keys_event)
        self.root.bind_all("<Control-n>", self.new_game_event)


        self.b_auto_check = self.b_auto_check1.get()
        self.b_auto_play = self.b_auto_play1.get()
        self.b_peep_next_in_queue = self.b_peep_next_in_queue1.get()
        self.b_win_game_only = self.b_win_game_only1.get()
        self.b_display_short_pile = self.b_display_short_pile1.get()                
        self.b_verbose = self.b_verbose1.get()    
        self.print_options()  

        # Set up card images resource

        self.frontImg = PhotoImage(file="{0}j.gif".format(self.gif_dir))
        self.backimg = PhotoImage(file="{0}b.gif".format(self.gif_dir))

        for card in range(52):
            self.card_img.append(PhotoImage(file="{0}%d.gif".format(self.gif_dir) % (card + 1)))

        # application window

        self.card_height = self.backimg.height()
        self.card_width = self.backimg.width()

        self.width_gap = self.card_width // 4
        self.height_gap = self.card_height // 4

        self.window_height = (self.card_height + self.height_gap * 9) * 2
        self.window_width = self.card_width * 5 + self.width_gap * 6

        # Application window
        self.root.geometry(str(self.window_width) + "x" + str(self.window_height))

        # application canvas
        self.canvas = Canvas(self.root, bg="blue", width=self.window_width, height=self.window_height)
        self.canvas.place(x=0, y=0)
        self.canvas.pack()        

    def initial_gui_ctrls(self):    

        # draw pile labels
        for pile in range(4):
            self.label_piles[pile] = self.draw_label(
                self.label_piles[pile],
                (self.width_gap + self.card_width) * pile + self.width_gap, 
                self.height_gap, 
                self.card_width, 
                self.height_gap,
                str(self.label_piles[pile]))            

        # draw peep next card
        x1=(self.width_gap + self.card_width) * 4 + self.width_gap
        y1=self.height_gap * 3
        image = self.backimg
        self.peep_next_label = self.draw_card(self.peep_next_label, x1, y1, image)

        # draw hands count label
        self.label_hands = self.draw_label(
            self.label_hands,
            (self.width_gap + self.card_width) * 4 + self.width_gap, 
            self.height_gap, 
            self.card_width, 
            self.height_gap,
            str(self.hands_label))

        # draw card in queue label
        self.label_queue = self.draw_label(
            self.label_queue, 
            (self.width_gap + self.card_width) * 4 + self.width_gap, 
            self.window_height - self.height_gap - self.height_gap - self.height_gap - self.height_gap - self.height_gap - 12, 
            self.card_width,
            self.height_gap,
            str(self.queue_label))

        self.undo_button = Button(self.canvas, text="Undo", command=self.undo_button_clicked)
        self.undo_button.place(x=(self.width_gap + self.card_width) * 4 + self.width_gap, y=self.window_height - self.height_gap - self.height_gap, width=self.card_width, height=self.height_gap)

        self.collect_button = Button(self.canvas, text="Collect", command=self.collect_button_clicked)
        self.collect_button.place(x=(self.width_gap + self.card_width) * 4 + self.width_gap, y=self.window_height - self.height_gap - self.height_gap - self.height_gap - 4, width=self.card_width, height=self.height_gap)

        self.deal_button = Button(self.canvas, text="Deal", command=self.deal_button_clicked)
        self.deal_button.place(x=(self.width_gap + self.card_width) * 4 + self.width_gap, y=self.window_height - self.height_gap - self.height_gap - self.height_gap - self.height_gap - 8, width=self.card_width, height=self.height_gap)

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
        # print(event)
        # print([event.type])
        # print(event, self.card_width, self.card_height, self.width_gap, self.height_gap)

        pile = self.is_in_pile_n(event.x, event.y)

        if (self.is_in_inner_canvas(event.x, event.y)):
            if pile >=0:
                if self.card_placeholder == None:
                    x1 = event.x
                    y1 = event.y               
                    x1 = event.x - self.width_gap
                    y1 = event.y - self.height_gap * 3
                    x1 = self.width_gap + int(x1 / (self.width_gap + self.card_width)) * (self.width_gap + self.card_width)
                    y1 = self.height_gap * 3 + int(y1 / self.height_gap) * self.height_gap
                    if (y1 > self.height_gap * 8):
                        y1 = self.height_gap * 8                
                    image = self.frontImg
                    self.card_placeholder = self.draw_card(self.card_placeholder, x1, y1, image)
                else:
                    x1 = event.x
                    y1 = event.y               
                    x1 = event.x - self.width_gap
                    y1 = event.y - self.height_gap * 3
                    x1 = self.width_gap + int(x1 / (self.width_gap + self.card_width)) * (self.width_gap + self.card_width)
                    y1 = self.height_gap * 3 + int(y1 / self.height_gap) * self.height_gap
                    if (y1 > self.height_gap * 8):
                        y1 = self.height_gap * 8
                    self.canvas.moveto(self.card_placeholder, x1, y1)
        else:
            if self.card_placeholder != None:
                self.canvas.delete(self.card_placeholder)
            self.card_placeholder = None

    def mouse_button1_down(self, event):
        if self.b_verbose:        
            print('mouse_button1_down') 
            print(event)
            print([event.type])

    def mouse_button2_down(self, event):
        if self.b_verbose:
            print('mouse_button2_down') 
            print(event)
            print([event.type])

    def mouse_button3_down(self, event):
        if self.b_verbose:        
            print('mouse_button3_down') 
            print(event)
            print([event.type])

    def mouse_button4_down(self, event):
        if self.b_verbose:        
            print('mouse_button4_down')    
            print(event)
            print([event.type])
        

    def mouse_button5_down(self, event):
        if self.b_verbose:        
            print('mouse_button5_down')
            print(event)
            print([event.type])
        

    def keys_event(self, event):
        if self.b_verbose:        
            print(event)
            print([event.type])
        if event.type == EventType.KeyPress:
            if event.char:
                print([event.char])

    def new_game_event(self, event):
        if self.b_verbose:
            print(event)
            print([event.type])
            print(self.TheGame.cards.rg_cards)
        self.initial_gui_ctrls()            
        self.TheGame.start_game(True)

    def new_game_command(self):
        if self.b_verbose:    
            print(self.TheGame.cards.rg_cards)
        self.initial_gui_ctrls()
        self.TheGame.start_game(True)

    def replay_button_clicked(self):
        self.initial_gui_ctrls()        
        self.TheGame.start_game(False)

    def load_game_clicked(self):
        thisdir = filedialog.askopenfilename(initialdir=self.cwd, title="Select file",
                                             filetypes=(("Card files", "*.txt"), ("all files", "*.*")))

        if self.load_file(thisdir):
            self.TheGame.start_game(False)
        else:
            print("No file loaded")

    def save_game_clicked(self):
        thisdir = filedialog.asksaveasfilename(initialdir=self.cwd, title="Select file",
                                               filetypes=(("Card files", "*.txt"), ("all files", "*.*")))

        self.save_file(thisdir)

    def load_file(self, thisdir):
        print(thisdir)

        if os.path.isfile(thisdir):  # single file
            checkset = set({})
            for i in range(52):
                checkset.add(i)

            # print (checkset)
            # print(thisdir)
            # load file
            deck = []
            infile = open(thisdir, 'r')
            for line in infile:
                # deck = [int(card) for card in line.split(",")]
                deck = [re.sub("\D", "", card) for card in line.split(",")]
                deck = [int(card) for card in deck if card]

                # if (there are 52 cards AND number are in the range of (0, 51) AND every number in the range of (0, 51) exists)
                # if len(deck) == 52 and (card for card in deck if 0 <= card <= 51):
                # if len(deck) == 52 and sorted(deck)==list(range(max(deck)+1)):
                if len(deck) == 52 and set(deck) == checkset:
                    # self.TheGame = GameInfo(deck, self)
                    # print(self.TheGame.cards.rg_cards)
                    self.TheGame.cards.rg_cards = deck
                    return True

        return False

    def save_file(self, thisdir):
        print(thisdir)

        ftext = open(thisdir, 'self.card_width', encoding="utf-8")
        # ftext = sys.stdout

        print(self.TheGame.cards.rg_cards, file=ftext)

        ftext.close()

    def deal_button_clicked(self):

        if not self.TheGame.b_done and self.TheGame.deal_one_card(True):
            self.print_all_piles()
            self.print_game_info()
            self.render_cards()            
            collectable = self.TheGame.card_piles[self.TheGame.current_pile].try_collect_cards(self.TheGame.card_queue, False)
            if collectable > 0:
                print("===", self.TheGame.current_pile, collectable)

            if self.b_auto_check or self.b_auto_play:
                while self.TheGame.card_piles[self.TheGame.current_pile].try_collect_cards(self.TheGame.card_queue, True) > 0 :
                    self.print_all_piles()
                    self.print_game_info()
                    self.render_cards()
                    pass

                if self.b_auto_play:
                    self.TheGame.play_game_automatically(True)
                    self.render_cards()

        # if not self.TheGame.b_done and self.TheGame.deal_one_card(True):
        #     self.print_all_piles()
        #     self.print_game_info()
        #     self.render_cards()

        else:
            # no more cards
            print("[Game Over]", ", Done:", self.TheGame.b_done, ", Win:", self.TheGame.b_win, ", Hands:",
                  self.TheGame.cnt_hands)

    def collect_button_clicked(self):
        self.print_options()

        if self.b_auto_check or self.b_auto_play:
            while self.TheGame.card_piles[self.TheGame.current_pile].try_collect_cards(self.TheGame.card_queue, True) > 0 :
                self.print_all_piles()
                self.print_game_info()
                self.render_cards()
                pass

            if self.b_auto_play:
                self.TheGame.play_game_automatically(True)
                self.render_cards()

        else:
            collected = self.TheGame.card_piles[self.TheGame.current_pile].try_collect_cards(self.TheGame.card_queue, True)

            if collected > 0:
                self.print_all_piles()
                self.print_game_info()
                self.render_cards()

                if not self.TheGame.b_done :
                    collectable = self.TheGame.card_piles[self.TheGame.current_pile].try_collect_cards(self.TheGame.card_queue, False)
                    if (collectable > 0):
                        print("===", self.TheGame.current_pile, collectable)

    def undo_button_clicked(self):
        self.TheGame.pop_stack_operations()
        self.print_all_piles()
        self.print_game_info()
        self.render_cards()

    def toggle_auto_check_option(self):
        self.b_auto_check = self.b_auto_check1.get()
        self.print_options()    

    def toggle_auto_play_option(self):
        self.b_auto_play = self.b_auto_play1.get()
        self.print_options()        

    def toggle_win_game_only_option(self):
        self.b_win_game_only = self.b_win_game_only1.get()
        self.print_options()

    def toggle_peep_next_option(self):
        self.b_peep_next_in_queue = self.b_peep_next_in_queue1.get()
        self.print_options()
        self.render_peep_card_in_queue(self.b_peep_next_in_queue)

    def toggle_display_short_list_option(self):
        self.b_display_short_pile = self.b_display_short_pile1.get()
        self.print_options()
        self.render_cards()

    def toggle_display_detail_info_option(self):
        self.b_verbose = self.b_verbose1.get()
        self.print_options()

    def draw_card(self, card, x, y, image):
        if (card != None):
            self.canvas.delete(card)

        card = self.canvas.create_image(x, y, image=image)
        self.canvas.addtag_withtag('image', card)

        return card       

    def draw_label(self, label, x, y, w, h, text, background='white', text_color='#000'):
        if (label != None):
            self.canvas.delete(label)

        label_bottom = self.canvas.create_rectangle(
            x, 
            y, 
            x + w,
            y + h, 
            fill=background)

        label = self.canvas.create_text(
            x + w / 2, 
            y + h / 2, 
            text=text,
            fill=text_color)

        return label    

    def render_peep_card_in_queue(self, b_peep_next_in_queue=True):
        x1=(self.width_gap + self.card_width) * 4 + self.width_gap + self.card_width // 2
        y1=self.height_gap * 3 + self.card_height // 2
        if b_peep_next_in_queue and len(self.TheGame.card_queue.rg_cards) > 0:
            self.print_peep_next_in_queue()
            card = self.TheGame.card_queue.rg_cards[0]
            image = self.card_img[card]
            self.peep_next_label = self.draw_card(self.peep_next_label, x1, y1, image)            
        else:
            image = self.backimg
            self.peep_next_label = self.draw_card(self.peep_next_label, x1, y1, image)              

    def render_cards(self):
        for card in self.card_check_boxes:
            self.canvas.delete(card)
        self.card_check_boxes.clear()

        for pile in range(4):
            if self.b_verbose:
                self.print_pile(pile)

            cards_in_deck = len(self.TheGame.card_piles[pile].rg_cards)
            
            if (self.label_piles[pile] != None):
                self.canvas.delete(self.label_piles[pile])           
            if pile == self.TheGame.current_pile:
                self.label_piles[pile] = self.draw_label(
                    self.label_piles[pile],
                    (self.width_gap + self.card_width) * pile + self.width_gap , 
                    self.height_gap, 
                    self.card_width, 
                    self.height_gap,                    
                    str(cards_in_deck),
                    background='yellow', 
                    text_color='#F00')

            else:
                self.label_piles[pile] = self.draw_label(
                    self.label_piles[pile],
                    (self.width_gap + self.card_width) * pile + self.width_gap , 
                    self.height_gap, 
                    self.card_width, 
                    self.height_gap,                        
                    str(cards_in_deck),
                    background='white', 
                    text_color='#0F0')

            if self.b_display_short_pile and cards_in_deck > 5:
                for i in range(6):
                    xx = (self.width_gap + self.card_width) * pile + self.width_gap
                    yy = self.height_gap * (i+3)
                    
                    if i < 2:
                        card = self.TheGame.card_piles[pile].rg_cards[i]
                        x1 = xx + self.card_width // 2
                        y1 = yy + self.card_height // 2                        
                        image = self.card_img[card]
                        card_ctrl = self.draw_card(None, x1, y1, image)                             
                        self.card_check_boxes.append(card_ctrl)                                                
              
                    elif i == 2:
                        card = self.TheGame.card_piles[pile].rg_cards[i]
                        x1 = xx + self.card_width // 2
                        y1 = yy + self.card_height // 2                        
                        image = self.backimg
                        card_ctrl = self.draw_card(None, x1, y1, image)                            
                        self.card_check_boxes.append(card_ctrl)
                        pass
                    else:
                        card = self.TheGame.card_piles[pile].rg_cards[i + (cards_in_deck - 6)]
                        x1 = xx + self.card_width // 2
                        y1 = yy + self.card_height // 2                        
                        image = self.card_img[card]
                        card_ctrl = self.draw_card(None, x1, y1, image)                          
                        self.card_check_boxes.append(card_ctrl)
                  
            else:
                for i, card in enumerate(self.TheGame.card_piles[pile].rg_cards):
                    xx = (self.width_gap + self.card_width) * pile + self.width_gap
                    yy = self.height_gap * (i+3)     
                    x1 = xx + self.card_width // 2
                    y1 = yy + self.card_height // 2   
                    image = self.card_img[card]     
                    card_ctrl = self.draw_card(None, x1, y1, image)                   

                    self.card_check_boxes.append(card_ctrl)

        # draw hands count label
        self.label_hands = self.draw_label(
            self.label_hands,
            (self.width_gap + self.card_width) * 4 + self.width_gap , 
            self.height_gap, 
            self.card_width, 
            self.height_gap,                
            str(self.TheGame.cnt_hands))

        # draw card in queue label
        self.label_queue = self.draw_label(
            self.label_queue,
            (self.width_gap + self.card_width) * 4 + self.width_gap, 
            self.window_height - self.height_gap - self.height_gap - self.height_gap - self.height_gap - self.height_gap - 12, 
            self.card_width, 
            self.height_gap,                
            str(self.TheGame.card_queue.n_count))                       

        self.render_peep_card_in_queue(self.b_peep_next_in_queue)

    def help_about(self):
        pass

    def print_deck(self):
        if self.b_verbose:
            print("Deck:", [self.TheGame.cards.rg_card_face[card] for card in self.TheGame.cards.rg_cards])

    def print_game_info(self):
        if self.b_verbose:
            # display info
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
            if pile == current_pile:
                s_prompt = ">Pile"
            else:
                s_prompt = " Pile"

            if self.TheGame.card_piles[pile].n_card_count >= 6 and self.b_display_short_pile:
                print(s_prompt, pile, ":", self.TheGame.card_piles[pile].n_card_count, "[",
                      self.TheGame.cards.rg_card_face[self.TheGame.card_piles[pile].rg_cards[0]], ", ",
                      self.TheGame.cards.rg_card_face[self.TheGame.card_piles[pile].rg_cards[1]], ", ",
                      "..., ",
                      self.TheGame.cards.rg_card_face[
                          self.TheGame.card_piles[pile].rg_cards[self.TheGame.card_piles[pile].n_card_count - 3]], ", ",
                      self.TheGame.cards.rg_card_face[
                          self.TheGame.card_piles[pile].rg_cards[self.TheGame.card_piles[pile].n_card_count - 2]], ", ",
                      self.TheGame.cards.rg_card_face[
                          self.TheGame.card_piles[pile].rg_cards[self.TheGame.card_piles[pile].n_card_count - 1]], "]")
            else:
                print(s_prompt, pile, ":", self.TheGame.card_piles[pile].n_card_count,
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
        if self.b_verbose:
            print(self.TheGame.cards.rg_card_face[self.TheGame.card_queue.rg_cards[0]])

    def print_options(self):
        if self.b_verbose:
            print("Auto Check:", self.b_auto_check)
            print("Auto Run:", self.b_auto_play)
            print("Peep Next In Queue:", self.b_peep_next_in_queue)
            print("Play Win Only Hand:", self.b_win_game_only)
            print("Display Short List:", self.b_display_short_pile)
            print("Display Detail Info:", self.b_verbose)     


