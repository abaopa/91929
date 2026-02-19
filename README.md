# 91929 Card Game

A mathematical logic solitaire game built with Python. The project features a shared logic core with two distinct graphical implementations: a Desktop version using Tkinter and a Mobile version using Flet (Flutter).

## Game Rules

### 1. The Deck
- **Cards Used:** 40 cards (Ace through 10 of all four suits).
- **Excluded:** Jacks, Queens, and Kings are removed.
- **Rank Values:** Ace = 1, 2-10 = face value.

### 2. Gameplay
- **Setup:** Cards are dealt from a **Queue** into 4 **Piles** on the table.
- **Dealing:** Cards are dealt one-by-one in a circular sequence (Pile 1 → 2 → 3 → 4 → 1...).
- **Collection (The "9" Rule):** You can remove (collect) exactly **three** cards from a single pile if their ranks sum to a number ending in **9** (9, 19, or 29). Collected cards return to the back of the Queue.
- **Valid Combinations:**
    - **Rule 1:** First two cards + Last card of the pile.
    - **Rule 2:** First card + Last two cards of the pile.
    - **Rule 3:** Last three cards of the pile.

### 3. Constraints & Objectives

#### The Last Pile Rule (Deadlock Prevention)
To ensure the game can always continue dealing, you are prohibited from clearing a pile if it is the only non-empty pile remaining, **unless** doing so immediately results in a win. This prevents a state where cards remain in the queue but no piles exist to receive them.

**The restriction is lifted in two cases:**
1.  **Queue is Empty:** Clearing the board is allowed because no more cards need to be dealt (leads to **Win Condition A**).
2.  **Next Card is a "3" AND Hands >= 40:** Clearing the board is allowed if it leads to a win where the "3" effectively becomes the single-card remainder for **Win Condition B**.

#### Winning Conditions
The game logic verifies victory via two distinct conditions. **Important: No win can be declared until the full deck has been dealt at least once (Hands Count >= 40).**

- **Win Condition A (Clean Sweep):**
    - The table is completely empty.
    - All 40 cards have returned to the Queue.
    - At least 40 hands have been dealt.

- **Win Condition B (The "3" Remainder):**
    - 39 cards are in the Queue.
    - Exactly one card with rank **"3"** remains on the table.
    - At least 40 hands have been dealt.

#### Losing Condition
- The game is declared lost only when the **Card Queue is empty** and no more valid combinations can be made with the cards remaining on the table.
- If the Queue is not empty but you have no moves, the game simply continues dealing until a move becomes available or the conditions for a win/loss are met.

---

## Desktop vs. Mobile Implementation

While the core logic resides in `src/game_info.py`, the two versions offer different features:

| Feature | Desktop (`src/game_ui.py`) | Mobile (`src/mobile_main.py`) |
| :--- | :--- | :--- |
| **Framework** | **Tkinter** | **Flet** (Flutter-based) |
| **Controls** | Mouse + **Keyboard Shortcuts** (Q-R, 1-3, Enter) | **Touch-optimized** buttons |
| **Short Pile** | Shows top 2 and bottom 3 (if > 5 cards) | Shows top 3 and bottom 11 (if > 15 cards) |
| **Auto Play** | Variable Delay (0-5s) via **Spinbox** | Asynchronous loop with fixed transition |
| **Assistant** | **Detailed Dialog** with visual stack previews | **Pile Highlights** (Light Blue) + Status Text |
| **Debug Mode** | Persistent column showing undealt cards | Toggleable view showing undealt stack |
| **Smart Undo** | "Rewind" pops history until a move exists | "REWIND" button performs the same search |

## Technical Notes
- **Core Logic:** Managed by `GameInfo` which handles dealing, stack-based undo operations, and win/loss validation.
- **Animations:** 
    - Desktop uses `root.after` recursion to move images via coordinate calculation.
    - Mobile uses Flet's `animate_position` and `animate_opacity` for smooth Flutter-native transitions.
