import asyncio
import os
import re
import sys
import threading
from typing import Optional, List, Tuple

import flet as ft
from game_info import GameInfo

# Performance & Path Setup
BASE_DIR: str = os.getcwd()


def get_card_image_path(card_idx: int) -> str:
    """Returns the relative path to a card image asset."""
    return f"images/{card_idx + 1}.gif"


def get_back_image_path() -> str:
    """Returns the relative path to the card back image."""
    return "images/b.gif"


class MobileGameAdapter:
    """Adapter class to connect the GameInfo logic with the Flet mobile UI."""

    def __init__(self, page: ft.Page) -> None:
        self.page: ft.Page = page
        self.b_auto_play: bool = False
        self._b_win_game_only: bool = False
        self._b_peep: bool = False
        self._b_assistant: bool = False
        self._b_tactile: bool = True
        self.render_count: int = 0
        self.best_move: Tuple[Optional[int], int] = (None, 0)

        # Permanent UI References
        self.pile_stacks: List[ft.Stack] = []
        self.pile_headers: List[ft.Text] = []
        self.pile_containers: List[ft.Container] = [] # The label containers
        self.column_containers: List[ft.Container] = [] # The whole column containers

        self.queue_text: Optional[ft.Text] = None
        self.hands_text: Optional[ft.Text] = None
        self.status_text: Optional[ft.Text] = None
        self.info_text: Optional[ft.Text] = None
        self.peep_card_img: Optional[ft.Image] = None
        self.debug_queue_stack: Optional[ft.Stack] = None
        
        self.deal_control: Optional[ft.Control] = None
        self.queue_control: Optional[ft.Control] = None

        # Switches
        self.auto_switch: Optional[ft.Switch] = None
        self.winnable_switch: Optional[ft.Switch] = None
        self.peep_switch: Optional[ft.Switch] = None
        self.assistant_switch: Optional[ft.Switch] = None
        self.debug_switch: Optional[ft.Switch] = None
        self.tactile_switch: Optional[ft.Switch] = None
        self.priority_dropdown: Optional[ft.Dropdown] = None

        self.undealt_stack: ft.Stack = ft.Stack(height=45, width=1000) # Width will be dynamic
        self.undealt_queue_col: Optional[ft.Column] = None

        self.animation_overlay: ft.Stack = ft.Stack(expand=True)

        self.selected_indices: List[int] = []
        self.selected_pile: int = -1

        self.hidden_pile: int = -1
        self.hidden_indices: List[int] = []

        self.debug_col: Optional[ft.Column] = None
        self.TheGame: GameInfo = GameInfo(self, None)

    # Logic Shims
    @property
    def b_win_game_only(self) -> bool:
        return self._b_win_game_only

    @property
    def b_verbose(self) -> bool:
        return False

    @property
    def b_tactile_mode(self):
        class Shim:
            def __init__(self, val): self.val = val
            def get(self): return self.val
        return Shim(self._b_tactile)

    # Stubs for desktop compatibility
    def print_deck(self) -> None:
        print("Deck:", [self.TheGame.cards.rg_card_face[card]
              for card in self.TheGame.cards.rg_cards])

    def print_piles(self, cp: int) -> None: pass
    def print_queue(self) -> None: pass
    def print_all_piles(self) -> None: pass
    def print_game_info(self) -> None: pass
    def render_peep_card_in_queue(self, b: bool = True) -> None: pass
    def print_peep_next_in_queue(self) -> None: pass

    def log(self, msg: str) -> None:
        print(f"[LOG] {msg}")

    async def animate_collection(self, pile_idx: int, card_values: List[int], card_indices: List[int]) -> None:
        """Animates cards flying from a pile to the DEAL control."""
        # 1. Establish hiding state
        self.selected_indices = []
        self.selected_pile = -1
        self.hidden_pile = pile_idx
        self.hidden_indices = card_indices
        
        # Force a render to make the real cards disappear from the pile
        await self.render_cards()

        p_obj = self.TheGame.card_piles[pile_idx]
        n = p_obj.n_card_count
        
        # Manual coordinates (centered content assumed)
        base_x = 10 + pile_idx * 76 + 2
        base_y = 62
        dest_x = 329
        dest_y = 210
        
        anim_cards = []
        for i, idx in enumerate(card_indices):
            if n <= self.TheGame.SHORT_PILE_MAX_DISPLAY:
                display_idx = idx
            else:
                if idx < self.TheGame.SHORT_PILE_TOP_COUNT:
                    display_idx = idx
                elif idx >= n - self.TheGame.SHORT_PILE_BOTTOM_COUNT:
                    display_idx = idx - (n - self.TheGame.SHORT_PILE_MAX_DISPLAY)
                else:
                    display_idx = self.TheGame.SHORT_PILE_TOP_COUNT
            
            s_y = base_y + display_idx * 30
                
            # Start at EXACT pile position
            card_img = ft.Image(
                src=get_card_image_path(card_values[i]),
                width=71, height=96,
                left=base_x,
                top=s_y,
                opacity=1,
            )
            anim_cards.append(card_img)
            self.animation_overlay.controls.append(card_img)
            
        self.animation_overlay.update()
        
        # 2. Pop Animation (Jump up-right)
        await asyncio.sleep(0.1)
        for card in anim_cards:
            card.animate_position = ft.Animation(250, ft.AnimationCurve.EASE_OUT)
            card.left += 12
            card.top -= 12
        self.animation_overlay.update()
        
        # 3. Pause while cards are in the "popped" position
        await asyncio.sleep(0.4)
        
        # 4. Trigger movement to DEAL control
        for card in anim_cards:
            card.animate_position = ft.Animation(800, ft.AnimationCurve.EASE_IN_OUT)
            card.animate_opacity = ft.Animation(800, ft.AnimationCurve.EASE_IN_OUT)
            card.left = dest_x
            card.top = dest_y
            card.opacity = 0
            
        self.animation_overlay.update()
        await asyncio.sleep(0.9)
        
        # 5. Cleanup
        self.animation_overlay.controls.clear()
        self.animation_overlay.update()
        self.hidden_pile = -1
        self.hidden_indices = []

    async def animate_deal(self, pile_idx: int, card_value: int) -> None:
        """Animates a card flying from the DEAL control to a pile."""
        start_x = 329
        start_y = 210
        
        dest_x = 10 + pile_idx * 76 + 2
        p_obj = self.TheGame.card_piles[pile_idx]
        n = p_obj.n_card_count
        display_idx = min(n, self.TheGame.SHORT_PILE_MAX_DISPLAY - 1)
        dest_y = 62 + display_idx * 30
        
        # 1. Create card at DEAL position, fully visible
        card_img = ft.Image(
            src=get_card_image_path(card_value),
            width=71, height=96,
            left=start_x,
            top=start_y,
            opacity=1,
        )
        
        self.animation_overlay.controls.append(card_img)
        self.animation_overlay.update()
        
        # 2. Anchor wait
        await asyncio.sleep(0.2)
        
        # 3. Trigger movement
        card_img.animate_position = ft.Animation(600, ft.AnimationCurve.EASE_IN_OUT)
        card_img.left = dest_x
        card_img.top = dest_y
        self.animation_overlay.update()
        
        # 4. Finishing wait
        await asyncio.sleep(0.7)
        self.animation_overlay.controls.remove(card_img)
        self.animation_overlay.update()

    async def render_cards(self) -> None:
        """Renders the current game state to the Flet UI components."""
        if not self.page:
            return
        self.render_count += 1
        try:
            for i in range(4):
                p_obj = self.TheGame.card_piles[i]
                stack = self.pile_stacks[i]
                header = self.pile_headers[i]
                label_container = self.pile_containers[i]

                # 1. Update Header Text
                header.value = f"{p_obj.n_card_count}"

                # 2. Update Card Stack with 'Short Pile' logic
                new_controls: List[ft.Control] = []
                if p_obj.n_card_count == 0:
                    new_controls.append(
                        ft.Container(
                            width=71, height=96,
                            border=ft.Border.all(1, ft.Colors.GREY_400),
                            border_radius=5,
                            top=10,
                        )
                    )
                else:
                    if p_obj.n_card_count <= self.TheGame.SHORT_PILE_MAX_DISPLAY:
                        for idx, val in enumerate(p_obj.rg_cards):
                            # Skip if card is currently being animated
                            if i == self.hidden_pile and idx in self.hidden_indices:
                                continue
                            x_off, y_off = (10, -10) if i == self.selected_pile and idx in self.selected_indices else (0, 0)
                            new_controls.append(
                                ft.Image(
                                    src=get_card_image_path(val),
                                    width=71, height=96,
                                    fit="contain", top=10 + idx * 30 + y_off,
                                    left=x_off
                                )
                            )
                    else:
                        # Top cards (e.g., 2)
                        for idx in range(self.TheGame.SHORT_PILE_TOP_COUNT):
                            # Skip if hidden
                            if i == self.hidden_pile and idx in self.hidden_indices:
                                continue
                            val = p_obj.rg_cards[idx]
                            x_off, y_off = (10, -10) if i == self.selected_pile and idx in self.selected_indices else (0, 0)
                            new_controls.append(ft.Image(src=get_card_image_path(val), width=71, height=96, fit="contain", top=10 + idx * 30 + y_off, left=x_off))
                        
                        # Gap indicator (at index SHORT_PILE_TOP_COUNT)
                        new_controls.append(ft.Image(src=get_back_image_path(), width=71, height=96, fit="contain", top=10 + self.TheGame.SHORT_PILE_TOP_COUNT * 30))
                        
                        # Bottom cards (e.g., 3)
                        for b_idx in range(self.TheGame.SHORT_PILE_BOTTOM_COUNT):
                            visual_idx = self.TheGame.SHORT_PILE_TOP_COUNT + 1 + b_idx
                            actual_idx = p_obj.n_card_count - self.TheGame.SHORT_PILE_BOTTOM_COUNT + b_idx
                            # Skip if hidden
                            if i == self.hidden_pile and actual_idx in self.hidden_indices:
                                continue
                            val = p_obj.rg_cards[actual_idx]
                            x_off, y_off = (10, -10) if i == self.selected_pile and actual_idx in self.selected_indices else (0, 0)
                            new_controls.append(ft.Image(src=get_card_image_path(val), width=71, height=96, fit="contain", top=10 + visual_idx * 30 + y_off, left=x_off))
                
                stack.controls = new_controls

                # 3. Dynamic Styling (Colors & Highlights)
                # Reset defaults
                label_container.bgcolor = ft.Colors.WHITE
                header.color = "#00FF00" # Green for non-current

                # Check for last pile status with refined rule
                non_empty_piles = [p for p in self.TheGame.card_piles if not p.b_pile_empty]
                
                next_card_is_3 = False
                if self.TheGame.card_queue.n_count > 0:
                    if (int(self.TheGame.card_queue.rg_cards[0] / 4) + 1) == 3:
                        next_card_is_3 = True
                
                # Enforce Hands >= 40 rule for victory clearance
                is_last_pile = len(non_empty_piles) == 1 and \
                               (self.TheGame.cnt_hands < 40 or (self.TheGame.card_queue.n_count > 0 and not next_card_is_3))

                has_move = self.TheGame.card_piles[i].try_collect_cards(
                    self.TheGame.card_queue, False, self.TheGame.rule_priority, is_last_pile
                ) > 0

                if i == self.TheGame.current_pile:
                    label_container.bgcolor = ft.Colors.YELLOW
                    header.color = ft.Colors.RED # High contrast for current
                
                # Apply Light Blue highlight if collectable (overrides White, keeps Yellow)
                if has_move and i != self.TheGame.current_pile:
                    label_container.bgcolor = "#ADD8E6"
                    header.color = ft.Colors.BLUE

            # Update Labels
            if self.queue_text:
                self.queue_text.value = f"{self.TheGame.card_queue.n_count}"
            if self.hands_text:
                self.hands_text.value = f"{self.TheGame.cnt_hands}"

            # Update Peep Card
            if self.peep_card_img:
                if (self._b_peep or self.TheGame.b_win) and self.TheGame.card_queue.n_count > 0:
                    next_card = self.TheGame.card_queue.rg_cards[0]
                    self.peep_card_img.src = get_card_image_path(next_card)
                    self.peep_card_img.visible = True
                else:
                    self.peep_card_img.visible = False

            # Debug: Update Undealt Cards Stack (Top 6, Bottom 6)
            if self.debug_queue_stack:
                total_undealt = len(self.TheGame.card_queue.rg_cards)
                debug_controls = []
                if total_undealt > 0:
                    if total_undealt <= 12:
                        indices = [(j, True) for j in range(total_undealt)]
                    else:
                        indices = [(j, True) for j in range(6)]
                        indices.append((6, False)) 
                        indices.extend([(j, True) for j in range(total_undealt - 6, total_undealt)])

                    for idx, (deck_idx, reveal) in enumerate(indices):
                        card_val = self.TheGame.card_queue.rg_cards[deck_idx]
                        img_path = get_card_image_path(card_val) if reveal else get_back_image_path()
                        debug_controls.append(ft.Image(src=img_path, width=71, height=96, fit="contain", top=idx * 30))
                self.debug_queue_stack.controls = debug_controls

            # Update Horizontal Undealt Queue at the bottom (Overlapping Stack)
            n_undealt = len(self.TheGame.card_queue.rg_cards)
            self.undealt_stack.controls = [
                ft.Image(src=get_card_image_path(val), width=30, height=40, fit="contain", left=idx * 8)
                for idx, val in enumerate(self.TheGame.card_queue.rg_cards)
            ]
            # Ensure the stack has enough width to be scrollable
            self.undealt_stack.width = (n_undealt * 8) + 30 if n_undealt > 0 else 10

            self.page.update()
        except Exception as e:
            self.log(f"Render Error: {e}")

    async def toggle_auto_play(self, e: ft.ControlEvent) -> None:
        self.b_auto_play = e.control.value
        if self.b_auto_play:
            asyncio.create_task(self.run_loop())

    async def toggle_winnable(self, e: ft.ControlEvent) -> None:
        self._b_win_game_only = e.control.value
        
    async def toggle_peep(self, e: ft.ControlEvent) -> None:
        self._b_peep = e.control.value
        await self.render_cards()

    async def toggle_assistant(self, e: ft.ControlEvent) -> None:
        self._b_assistant = e.control.value

    async def handle_priority_change(self, e: ft.ControlEvent) -> None:
        if e.data == "123":
            self.TheGame.rule_priority = [4, 2, 1]
        else:
            self.TheGame.rule_priority = [1, 2, 4]
        self.log(f"Priority changed to: {self.TheGame.rule_priority}")

    async def toggle_debug(self, e: ft.ControlEvent) -> None:
        if self.undealt_queue_col:
            self.undealt_queue_col.visible = e.control.value
            self.page.update()

    async def toggle_tactile(self, e: ft.ControlEvent) -> None:
        self._b_tactile = e.control.value
        self.selected_indices = []
        self.selected_pile = -1
        await self.render_cards()

    async def run_loop(self) -> None:
        while self.b_auto_play and not self.TheGame.b_done:
            moved = False
            non_empty_piles = [p for p in self.TheGame.card_piles if not p.b_pile_empty]
            
            next_card_is_3 = False
            if self.TheGame.card_queue.n_count > 0:
                if (int(self.TheGame.card_queue.rg_cards[0] / 4) + 1) == 3:
                    next_card_is_3 = True
            
            # Enforce Hands >= 40 rule for victory clearance
            is_last_pile = len(non_empty_piles) == 1 and \
                           (self.TheGame.cnt_hands < 40 or (self.TheGame.card_queue.n_count > 0 and not next_card_is_3))

            for i in range(4):
                collectable = self.TheGame.card_piles[i].try_collect_cards(
                        self.TheGame.card_queue, False, self.TheGame.rule_priority, is_last_pile
                    )
                if collectable > 0:
                    # Determine rule
                    rule_id = 0
                    for r in self.TheGame.rule_priority:
                        if collectable & r:
                            rule_id = r
                            break
                    
                    # Determine card indices and values for animation
                    p_obj = self.TheGame.card_piles[i]
                    n = p_obj.n_card_count
                    indices = []
                    if rule_id == 4: indices = [0, 1, n - 1]
                    elif rule_id == 2: indices = [0, n - 2, n - 1]
                    elif rule_id == 1: indices = [n - 3, n - 2, n - 1]
                    
                    if indices:
                        # Demonstate the "pop" visually first if in tactile mode
                        if self._b_tactile:
                            self.selected_pile = i
                            self.selected_indices = indices
                            await self.render_cards()
                            await asyncio.sleep(0.3) # Demo pause to see the pop

                        card_values = [p_obj.rg_cards[idx] for idx in indices]
                        await self.animate_collection(i, card_values, indices)

                    self.TheGame.card_piles[i].collect_rule(rule_id, self.TheGame.card_queue)
                    moved = True
                    await self.render_cards()
                    # await asyncio.sleep(0.2) # Removed extra sleep as animation takes time
                    break
            if moved: continue
            if self.TheGame.card_queue.n_count > 0:
                # Predict next pile for animation
                next_p = (self.TheGame.current_pile + 1) % 4
                checked = 0
                while self.TheGame.card_piles[next_p].b_pile_empty and checked < 4:
                    next_p = (next_p + 1) % 4
                    checked += 1
                
                if checked == 4:
                    self.b_auto_play = False
                    break
                
                # Animate before dealing
                await self.animate_deal(next_p, self.TheGame.card_queue.rg_cards[0])

                if self.TheGame.deal_one_card(True):
                    await self.render_cards()
                    # await asyncio.sleep(0.2)
                else: self.b_auto_play = False
            else: self.b_auto_play = False
            self.TheGame.check_win_status()
            if self.TheGame.b_done:
                await self.render_cards()
                await self.show_game_over()
                break
        self.b_auto_play = False
        if self.auto_switch:
            self.auto_switch.value = False
            self.auto_switch.update()

    async def undo_clicked(self, e: ft.ControlEvent) -> None:
        self.TheGame.pop_stack_operations()
        if self.status_text: self.status_text.value = ""
        await self.render_cards()

    async def rewind_clicked(self, e: ft.ControlEvent) -> None:
        if self.b_auto_play: return
        rewound = 0
        while len(self.TheGame.rg_stack_operation) > 0:
            has_move = False
            non_empty_piles = [p for p in self.TheGame.card_piles if not p.b_pile_empty]
            
            next_card_is_3 = False
            if self.TheGame.card_queue.n_count > 0:
                if (int(self.TheGame.card_queue.rg_cards[0] / 4) + 1) == 3:
                    next_card_is_3 = True
            
            # Enforce Hands >= 40 rule for victory clearance
            is_last_pile = len(non_empty_piles) == 1 and \
                           (self.TheGame.cnt_hands < 40 or (self.TheGame.card_queue.n_count > 0 and not next_card_is_3))

            for i in range(4):
                if self.TheGame.card_piles[i].try_collect_cards(self.TheGame.card_queue, False, self.TheGame.rule_priority, is_last_pile) > 0:
                    has_move = True
                    break
            if has_move: break
            self.TheGame.pop_stack_operations()
            rewound += 1
        if self.status_text:
            self.status_text.value = f"Rewound {rewound} steps" if rewound > 0 else "Moves available"
            self.status_text.color = ft.Colors.WHITE
        await self.render_cards()

    async def pile_clicked(self, idx: int, local_y: Optional[float] = None) -> None:
        """Handles manual collection click on a pile."""
        if self.b_auto_play: return
        
        if self._b_tactile and local_y is not None:
            await self.handle_tactile_click(idx, local_y)
            return

        # Challenge Rule: ONLY allowed at the current dealing pile
        if idx != self.TheGame.current_pile:
            if self.status_text:
                self.status_text.value = f"Wait! Click P{self.TheGame.current_pile + 1} or Deal."
                self.status_text.color = ft.Colors.RED_400
            self.page.update()
            return

        # Check if collection is actually possible
        non_empty_piles = [p for p in self.TheGame.card_piles if not p.b_pile_empty]
        
        next_card_is_3 = False
        if self.TheGame.card_queue.n_count > 0:
            if (int(self.TheGame.card_queue.rg_cards[0] / 4) + 1) == 3:
                next_card_is_3 = True
        
        # Enforce Hands >= 40 rule for victory clearance
        is_last_pile = len(non_empty_piles) == 1 and \
                       (self.TheGame.cnt_hands < 40 or (self.TheGame.card_queue.n_count > 0 and not next_card_is_3))

        collectable = self.TheGame.card_piles[idx].try_collect_cards(self.TheGame.card_queue, False, self.TheGame.rule_priority, is_last_pile)
        if collectable > 0:
            await self.show_collection_dialog(collectable, idx)
        else:
            if self.status_text:
                self.status_text.value = f"No moves available for P{idx + 1}"
                self.status_text.color = ft.Colors.RED_400
            self.page.update()

    async def handle_tactile_click(self, pile_idx: int, local_y: float) -> None:
        """Handles selecting individual cards for the 3-card collection set."""
        # Challenge Rule: ONLY allowed at the current dealing pile
        if pile_idx != self.TheGame.current_pile:
            return

        if self.selected_pile != pile_idx:
            self.selected_indices = []
            self.selected_pile = pile_idx

        # Adjust for header height: P# label (size 9 + spacing 2) + header (30 + spacing 2) ~= 43. Adjusted to 45 for mobile padding.
        y_cards = local_y - 45
        if y_cards < 0: return # Clicked on header area

        visual_idx = int(y_cards / 30)
        pile_len = len(self.TheGame.card_piles[pile_idx].rg_cards)
        
        if pile_len > self.TheGame.SHORT_PILE_MAX_DISPLAY:
            if visual_idx < self.TheGame.SHORT_PILE_TOP_COUNT:
                actual_card_idx = visual_idx
            elif visual_idx == self.TheGame.SHORT_PILE_TOP_COUNT:
                # Clicked on the Gap indicator
                return 
            else:
                # Bottom part
                if visual_idx >= self.TheGame.SHORT_PILE_MAX_DISPLAY: visual_idx = self.TheGame.SHORT_PILE_MAX_DISPLAY - 1
                actual_card_idx = visual_idx - (self.TheGame.SHORT_PILE_TOP_COUNT + 1) + (pile_len - self.TheGame.SHORT_PILE_BOTTOM_COUNT)
        else:
            actual_card_idx = visual_idx
        
        if actual_card_idx >= pile_len: actual_card_idx = pile_len - 1
        if actual_card_idx < 0: return

        if actual_card_idx in self.selected_indices:
            self.selected_indices.remove(actual_card_idx)
        else:
            self.selected_indices.append(actual_card_idx)
            if len(self.selected_indices) > 3:
                self.selected_indices.pop(0)

        if len(self.selected_indices) == 3:
            await self.validate_tactile_collection(pile_idx)
        
        await self.render_cards()

    async def validate_tactile_collection(self, pile_idx: int) -> None:
        """Checks if the 3 selected cards match a legal Rule."""
        pile = self.TheGame.card_piles[pile_idx]
        pile_len = len(pile.rg_cards)
        sel = sorted(self.selected_indices)
        
        matched_rule = None
        if sel == [0, 1, pile_len-1]: matched_rule = 4
        elif sel == [0, pile_len-2, pile_len-1]: matched_rule = 2
        elif sel == [pile_len-3, pile_len-2, pile_len-1]: matched_rule = 1
        
        if matched_rule:
            # Perform animation for tactile collection
            c_vals = [pile.rg_cards[i] for i in sel]
            await self.animate_collection(pile_idx, c_vals, sel)
            
            # Apply logic
            pile.collect_rule(matched_rule, self.TheGame.card_queue)
            self.selected_indices = []
            self.selected_pile = -1
            await self.render_cards()
            await self.check_end()
        else:
            self.selected_indices = []

    async def collect_clicked(self, e: ft.ControlEvent) -> None:
        """Handler for the dedicated COLLECT button."""
        if self.b_auto_play: return
        if self.TheGame.current_pile < 0:
            if self.status_text:
                self.status_text.value = "Deal a card first!"
                self.status_text.color = ft.Colors.ORANGE_400
            self.page.update()
            return
        await self.pile_clicked(self.TheGame.current_pile)

    async def execute_choice(self, rid, indices, l, pile_idx):
        try:
            print(f"DEBUG: execute_choice start - Rule: {l}, Pile: {pile_idx}")
            
            # Save state at the very start, before any UI/Logic changes
            self.TheGame.push_stack_operations()

            # Dismiss the dialog
            self.page.pop_dialog()
            self.page.update()
            
            p_obj = self.TheGame.card_piles[pile_idx]
            # Perform animation
            c_vals = [p_obj.rg_cards[i] for i in indices]
            await self.animate_collection(pile_idx, c_vals, indices)
            
            # Apply logic
            success = self.TheGame.card_piles[pile_idx].collect_rule(rid, self.TheGame.card_queue)
            
            if success:
                print(f"DEBUG: Collection successful for {l}")
                if self.status_text:
                    self.status_text.value = f"Collected {l} from P{pile_idx + 1}"
                    self.status_text.color = ft.Colors.GREEN_400
            else:
                print(f"DEBUG: Collection logic returned False for {l}")
                
            await self.render_cards()
            await self.check_end()
        except Exception as ex:
            print(f"ERROR in execute_choice: {ex}")

    async def show_collection_dialog(self, mask: int, pile_idx: int) -> None:
        """Shows an AlertDialog for choosing between multiple collection rules."""
        try:
            p_obj = self.TheGame.card_piles[pile_idx]
            n = p_obj.n_card_count
            print(f"DEBUG: show_collection_dialog for P{pile_idx}, mask: {mask}, count: {n}")

            recommended_rule = 0
            for r in self.TheGame.rule_priority:
                if mask & r:
                    recommended_rule = r
                    break

            rules_meta = [(4, "Rule 1", [0, 1, n - 1]), (2, "Rule 2", [0, n - 2, n - 1]), (1, "Rule 3", [n - 3, n - 2, n - 1])]

            options = []
            for r_id, label, idxs in rules_meta:
                if mask & r_id:
                    print(f"DEBUG: Adding option {label} for P{pile_idx}")
                    is_rec = (r_id == recommended_rule)
                    card_values = [p_obj.rg_cards[i] for i in idxs]

                    preview_stack = ft.Stack(height=150, width=71)
                    # Logic to insert gap indicator if indices are not consecutive
                    display_elements = []
                    for j in range(len(idxs)):
                        display_elements.append(("card", card_values[j]))
                        if j < len(idxs) - 1 and idxs[j+1] > idxs[j] + 1:
                            display_elements.append(("gap", None))
                    
                    for idx, (el_type, val) in enumerate(display_elements):
                        img_path = get_card_image_path(val) if el_type == "card" else get_back_image_path()
                        preview_stack.controls.append(ft.Image(src=img_path, width=71, height=96, top=idx*15))                    
                    # Direct async handler
                    async def on_select_click(e, rid=r_id, ind=idxs, lab=label, p_id=pile_idx):
                        print(f"DEBUG: UI Clicked {lab} for P{p_id}")
                        await self.execute_choice(rid, ind, lab, p_id)

                    options.append(
                        ft.Container(
                            content=ft.Column([
                                ft.Text(label + ("\n(Best)" if is_rec else ""), size=9, weight="bold", text_align="center"),
                                preview_stack,
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                            padding=5,
                            bgcolor=ft.Colors.WHITE10,
                            border=ft.Border.all(1, ft.Colors.GREEN if is_rec else ft.Colors.WHITE24),
                            border_radius=8,
                            on_click=on_select_click
                        )
                    )

            def close_dlg(e):
                self.page.pop_dialog()
                self.page.update()

            print("DEBUG: Creating AlertDialog object")
            dlg = ft.AlertDialog(
                title=ft.Text(f"P{pile_idx + 1} Options", size=10, weight="bold"),
                content=ft.Row(options, spacing=3, tight=True, vertical_alignment="start"),
                actions=[ft.TextButton("Cancel", on_click=close_dlg)],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            
            print("DEBUG: Calling self.page.show_dialog(dlg)")
            self.page.show_dialog(dlg)
            self.page.update()
            print("DEBUG: show_dialog called and page updated")
        except Exception as ex:
            print(f"ERROR in show_collection_dialog: {ex}")

    async def deal_clicked(self, e: ft.ControlEvent) -> None:
        if self.b_auto_play: return

        # Un-pop any cards before dealing
        self.selected_indices = []
        self.selected_pile = -1

        if self._b_assistant:
            piles_with_moves = []
            non_empty_piles = [p for p in self.TheGame.card_piles if not p.b_pile_empty]
            
            next_card_is_3 = False
            if self.TheGame.card_queue.n_count > 0:
                if (int(self.TheGame.card_queue.rg_cards[0] / 4) + 1) == 3:
                    next_card_is_3 = True
            
            # Enforce Hands >= 40 rule for victory clearance
            is_last_pile = len(non_empty_piles) == 1 and \
                           (self.TheGame.cnt_hands < 40 or (self.TheGame.card_queue.n_count > 0 and not next_card_is_3))

            for i in range(4):
                if self.TheGame.card_piles[i].try_collect_cards(self.TheGame.card_queue, False, self.TheGame.rule_priority, is_last_pile) > 0:
                    piles_with_moves.append(str(i + 1))
            if piles_with_moves:
                if self.status_text:
                    self.status_text.value = f"Collect moves in Pile {', '.join(piles_with_moves)}!"
                    self.status_text.color = ft.Colors.RED_400
                self.page.update()
                return
        
        if not self.TheGame.b_done and self.TheGame.card_queue.n_count > 0:
            # Predict the next pile
            next_pile_idx = (self.TheGame.current_pile + 1) % 4
            checked = 0
            while self.TheGame.card_piles[next_pile_idx].b_pile_empty and checked < 4:
                next_pile_idx = (next_pile_idx + 1) % 4
                checked += 1
            
            if checked == 4:
                await self.check_end()
                return
            
            # Get the card value that will be dealt
            card_val = self.TheGame.card_queue.rg_cards[0]
            
            # ANIMATE
            await self.animate_deal(next_pile_idx, card_val)
            
            if self.TheGame.deal_one_card(True):
                if self.status_text: self.status_text.value = ""
                await self.render_cards()
                await self.check_end()

    async def check_end(self) -> None:
        self.TheGame.check_win_status()
        if self.TheGame.b_done: await self.show_game_over()

    async def show_game_over(self) -> None:
        if self.status_text:
            self.status_text.value = "VICTORY!" if self.TheGame.b_win else "GAME OVER"
            self.status_text.color = ft.Colors.GREEN if self.TheGame.b_win else ft.Colors.RED
        self.TheGame.b_done = True
        self.page.update()

    async def restart_clicked(self, e: ft.ControlEvent) -> None:
        self.b_auto_play = False
        if self.status_text: self.status_text.value = "Starting New Game..."
        self.page.update()
        await asyncio.to_thread(lambda: self.TheGame.start_game(True))
        if self.status_text: self.status_text.value = ""
        await self.render_cards()

    async def replay_clicked(self, e: ft.ControlEvent) -> None:
        self.b_auto_play = False
        if self.status_text: self.status_text.value = "Replaying..."
        self.page.update()
        self.TheGame.start_game(False)
        if self.status_text: self.status_text.value = ""
        await self.render_cards()

    async def on_load_btn(self, e: ft.ControlEvent) -> None:
        save_file_path = os.path.join(BASE_DIR, "saved_game.json")
        try:
            self.TheGame.load_game_state(save_file_path)
            if self.status_text:
                self.status_text.value = "Game loaded successfully!"
                self.status_text.color = ft.Colors.GREEN_400
        except FileNotFoundError:
            if self.status_text:
                self.status_text.value = "No saved game found."
                self.status_text.color = ft.Colors.RED_400
        except Exception as ex:
            if self.status_text:
                self.status_text.value = f"Error loading game: {ex}"
                self.status_text.color = ft.Colors.RED_400
        finally:
            await self.render_cards()
            self.page.update()

    async def on_save_btn(self, e: ft.ControlEvent) -> None:
        save_file_path = os.path.join(BASE_DIR, "saved_game.json")
        try:
            self.TheGame.save_game_state(save_file_path)
            if self.status_text:
                self.status_text.value = "Game saved successfully!"
                self.status_text.color = ft.Colors.GREEN_400
        except Exception as ex:
            if self.status_text:
                self.status_text.value = f"Error saving game: {ex}"
                self.status_text.color = ft.Colors.RED_400
        finally:
            self.page.update()


async def main(page: ft.Page) -> None:
    page.title = "91929"
    
    # Desktop window size settings (will be ignored by mobile browser)
    page.window.width = 441
    page.window.maximized = False
    page.window.resizable = True
    
    # Force update and wait
    page.update()
    await asyncio.sleep(0.2)

    # If the offset is different, we adjust one more time
    if page.width != 425:
        diff = 425 - page.width
        page.window.width += diff
        page.update()
        await asyncio.sleep(0.1)

    print(f"DEBUG: Final Page Width (Usable): {page.width}")
    print(f"DEBUG: Final Window Width (Outer): {page.window.width}")
    
    page.bgcolor = "#336699"
    page.padding = 10
    ad = MobileGameAdapter(page)
    
    def label_container(content, width=75):
        return ft.Container(content=content, alignment=ft.Alignment(0, 0), width=width, height=30, bgcolor="white", border=ft.Border.all(1, "black"))

    # UI Components
    ad.hands_text = ft.Text("0", size=16, weight="bold", color="black", text_align=ft.TextAlign.CENTER)
    ad.queue_text = ft.Text("40", size=16, weight="bold", color="black", text_align=ft.TextAlign.CENTER)
    ad.status_text = ft.Text("", size=14, weight="bold", color="white")
    ad.peep_card_img = ft.Image(src="images/b.gif", width=60, height=82, fit="contain")

    # Piles Layout - Optimized for Side-by-Side with Info
    piles_row = ft.Row(spacing=4, alignment=ft.MainAxisAlignment.START)
    for i in range(4):
        stack = ft.Stack(height=280, width=72) # Increased to 280 for 30px gap
        header = ft.Text("0", size=15, weight="bold")
        l_cont = label_container(header, width=65)
        ad.pile_stacks.append(stack)
        ad.pile_headers.append(header)
        ad.pile_containers.append(l_cont)
        
        def make_on_tap_down(idx):
            async def on_tap_down(e: ft.TapEvent):
                y = e.local_position.y if e.local_position else 0
                await ad.pile_clicked(idx, y)
            return on_tap_down

        piles_row.controls.append(
            ft.GestureDetector(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text(f"P{i+1}", size=8, weight="bold", color="white"),
                        l_cont,
                        stack
                    ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ),
                on_tap_down=make_on_tap_down(i)
            )
        )

    # Info Column (Vertical, to be placed on the right of piles)
    ad.queue_control = label_container(ad.queue_text, 55)
    ad.deal_control = ft.Container(ft.Image(src="images/b.gif", width=42, height=60), on_click=ad.deal_clicked, border=ft.Border.all(1, "white"), border_radius=3)

    info_column = ft.Column([
        ft.Column([ft.Text("HANDS", size=9, color="white"), label_container(ad.hands_text, 55)], horizontal_alignment="center", spacing=1),
        ft.Column([ft.Text("NEXT", size=9, color="white"), ft.Container(ad.peep_card_img, height=60, width=42)], horizontal_alignment="center", spacing=1),
        ft.Column([ft.Text("QUEUE", size=9, color="white"), ad.queue_control], horizontal_alignment="center", spacing=1),
        ft.Column([ft.Text("DEAL", size=9, color="white"), ad.deal_control], horizontal_alignment="center", spacing=1),
    ], spacing=10, horizontal_alignment="center", width=60)

    # Action Buttons Grid - Optimized to 3x2
    def action_button(text, icon, on_click, color="white"):
        return ft.ElevatedButton(
            content=ft.Row([ft.Icon(icon, size=16), ft.Text(text, size=12)], alignment="center", spacing=5),
            on_click=on_click,
            bgcolor=color,
            color="black",
            style=ft.ButtonStyle(padding=5, shape=ft.RoundedRectangleBorder(radius=5)),
            expand=True
        )

    actions_grid = ft.Column([
        ft.Row([
            action_button("New", ft.Icons.ADD, ad.restart_clicked, "white"),
            action_button("Undo", ft.Icons.UNDO, ad.undo_clicked, "white"),
            action_button("Load", ft.Icons.FOLDER_OPEN, ad.on_load_btn, "white"),
        ], spacing=5),
        ft.Row([
            action_button("Replay", ft.Icons.REFRESH, ad.replay_clicked, "white"),
            action_button("Rewind", ft.Icons.REPLAY, ad.rewind_clicked, "white"),
            action_button("Save", ft.Icons.SAVE, ad.on_save_btn, "white"),
        ], spacing=5),
    ], spacing=10)

    ad.debug_queue_stack = ft.Stack(height=300, width=60)
    debug_col = ft.Column([ft.Text("UNDEALT", size=9, weight="bold", color="white"), ft.Container(content=ad.debug_queue_stack, padding=ft.Padding.only(top=20))], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER, visible=False)
    ad.debug_col = debug_col

    ad.auto_switch = ft.Switch(label="Auto", on_change=ad.toggle_auto_play, label_position=ft.LabelPosition.RIGHT)
    ad.peep_switch = ft.Switch(label="Peep", on_change=ad.toggle_peep, label_position=ft.LabelPosition.RIGHT)
    ad.tactile_switch = ft.Switch(label="Tactile", value=True, on_change=ad.toggle_tactile, label_position=ft.LabelPosition.RIGHT)
    ad.winnable_switch = ft.Switch(label="Win Only", on_change=ad.toggle_winnable, label_position=ft.LabelPosition.RIGHT)
    ad.assistant_switch = ft.Switch(label="Assistant", on_change=ad.toggle_assistant, label_position=ft.LabelPosition.RIGHT)
    ad.debug_switch = ft.Switch(label="Debug", on_change=ad.toggle_debug, label_position=ft.LabelPosition.RIGHT)
    
    options_grid = ft.Column([
        ft.Row([ft.Container(content=s, theme_mode=ft.ThemeMode.DARK) for s in [ad.auto_switch, ad.peep_switch, ad.winnable_switch]], alignment="center", spacing=5),
        ft.Row([ft.Container(content=s, theme_mode=ft.ThemeMode.DARK) for s in [ad.assistant_switch, ad.tactile_switch, ad.debug_switch]], alignment="center", spacing=5),
    ], spacing=5)

    # Horizontal Undealt Queue (Overlapping) - Controlled by Debug
    ad.undealt_queue_col = ft.Container(
        content=ft.Column([
            ft.Text("UNDEALT QUEUE", size=9, weight="bold", color="white60"),
            ft.Row([ad.undealt_stack], scroll=ft.ScrollMode.AUTO, height=45)
        ], spacing=2),
        width=370,
        visible=False
    )

    page.add(
        ft.Stack([
            ft.Column([
                # Main Play Area: Piles and Info side-by-side
                ft.Container(
                    content=ft.Row([
                        piles_row,
                        info_column
                    ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment="start", spacing=10),
                    padding=ft.padding.only(top=10, bottom=10),
                    alignment=ft.Alignment(0, 0)
                ),
                
                # Bottom Controls Area
                ft.Container(
                    content=ft.Column([
                        actions_grid,
                        options_grid,
                        ft.Container(content=ad.status_text, alignment=ft.Alignment(0, 0), height=30),
                        ad.undealt_queue_col
                    ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=15,
                    bgcolor="#224466",
                    border_radius=ft.border_radius.only(top_left=25, top_right=25),
                    alignment=ft.Alignment(0, 0)
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
            ad.animation_overlay
        ], expand=True)
    )
    
    ad.TheGame.play_real_init(True)
    await ad.render_cards()

if __name__ == "__main__":
    if getattr(sys, 'frozen', False):
        assets_path = "assets"
    else:
        assets_path = "../assets"
    ft.app(target=main, assets_dir=assets_path)
