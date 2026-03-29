import pygame
import sys
from session import Session
from tree import Tree
from button import Button
from user_handler import User

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# XP and balance rewards
XP_ALIVE  = 50
XP_DEAD   = 10
BAL_ALIVE = 20
BAL_DEAD  = 5

class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
        self.timer_font = pygame.font.SysFont(None, 48)

        # Load or create the user
        self.user = User.get("User")

        self.curr_session = None
        self.curr_duration = 10

        # Note input state — "start", "end", or None
        self.typing_note  = None
        self.start_note   = ""
        self.end_note     = ""

        # Tracks whether the pending tree was alive or dead (used after end note)
        self.pending_alive = False

        # Tree skins
        self.tree_skins = [
            pygame.image.load("assets/trees/oak.png").convert_alpha(),
            pygame.image.load("assets/trees/spruce.png").convert_alpha(),
            pygame.image.load("assets/trees/crimson_spruce.png").convert_alpha(),
            pygame.image.load("assets/trees/cherry_oak.png").convert_alpha(),
        ]
        self.tree_index = 0
        self.tree_image = self.tree_skins[self.tree_index]

        # Skin names match the image files so we can save the correct type
        self.tree_skin_names = ["oak.png", "spruce.png", "crimson_spruce.png", "cherry_oak.png"]

        # Buttons
        self.session_button = Button(
            (SCREEN_WIDTH // 2 - 84, SCREEN_HEIGHT // 2 + 64),
            (200, 50),
            text="Start Session",
            bg_color=(5, 31, 32),
            font_size=20,
            on_click=self.start_new_session
        )

        self.stop_button = Button(
            (SCREEN_WIDTH // 2 - 84, SCREEN_HEIGHT // 2 + 130),
            (200, 50),
            text="Stop Session",
            bg_color=(150, 0, 0),
            font_size=20,
            on_click=self.stop_session
        )

        self.skin_button = Button(
            (SCREEN_WIDTH // 2 - 84, SCREEN_HEIGHT // 2 + 195),
            (200, 50),
            text="Change Skin",
            bg_color=(5, 31, 32),
            font_size=20,
            on_click=self.change_skin
        )

    # --- Main loop ---
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.dt = self.clock.tick(60) / 1000

    # --- Button actions ---
    def start_new_session(self):
        # Don't start if a session is already running or waiting for a note
        if self.curr_session or self.typing_note:
            return
        # Ask for a start note before beginning the session
        self.typing_note = "start"
        self.start_note  = ""

    def stop_session(self):
        # Don't stop if nothing is running or we're already waiting for a note
        if not self.curr_session or self.typing_note:
            return
        # Mark the tree as dead and ask for an end note
        self.curr_session.tree.alive = False
        self.pending_alive = False
        self.typing_note   = "end"
        self.end_note      = ""

    def change_skin(self):
        self.tree_index = (self.tree_index + 1) % len(self.tree_skins)
        self.tree_image = self.tree_skins[self.tree_index]

    # --- Called after the end note is submitted to save and clean up ---
    def _finish_session(self):
        if self.curr_session and self.curr_session.tree:
            self._save_tree(self.curr_session.tree, alive=self.pending_alive)
        self.curr_session = None
        self.typing_note  = None

    # --- Saves a completed or stopped tree to the user's data ---
    def _save_tree(self, tree, alive):
        skin_name = self.tree_skin_names[self.tree_index]

        # Prefix the filename with dead_ if the tree didn't survive
        if not alive:
            skin_name = "dead_" + skin_name

        # Give XP and balance based on whether the tree survived
        if alive:
            self.user.update_xp(XP_ALIVE)
            self.user.update_balance(BAL_ALIVE)
        else:
            self.user.update_xp(XP_DEAD)
            self.user.update_balance(BAL_DEAD)

        # Save the tree using the notes collected from the text boxes
        self.user.add_tree(
            tree=skin_name,
            elapsed=round(tree.elapsed, 2),
            duration=tree.duration,
            alive=alive,
            upvotes=getattr(tree, "upvotes", 0),
            downvotes=getattr(tree, "downvotes", 0),
            start_note=self.start_note,
            end_note=self.end_note
        )

        print(f"Tree saved — type: {skin_name}, alive: {alive}, XP: {self.user.xp}, balance: {self.user.balance}")

    # --- Game logic ---
    def update(self):
        if self.curr_session and not self.typing_note:
            self.curr_session.update(self.dt)

            # Session finished naturally — ask for an end note then save as alive
            if self.curr_session.is_finished():
                self.pending_alive = True
                self.typing_note   = "end"
                self.end_note      = ""

    def draw(self):
        self.screen.fill((1, 50, 32))

        # Draw tree
        if self.curr_session:
            progress = self.curr_session.tree.elapsed / self.curr_session.tree.duration
            scale = 0.5 + 0.5 * progress
            tree_scaled = pygame.transform.smoothscale(
                self.tree_image,
                (int(self.tree_image.get_width() * scale),
                 int(self.tree_image.get_height() * scale))
            )
            tree_rect = tree_scaled.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(tree_scaled, tree_rect)
        else:
            tree_rect = self.tree_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(self.tree_image, tree_rect)

        # Draw timer
        if self.curr_session:
            self.display_timer_text()

        # Draw user stats in the top right
        self.display_user_stats()

        # Draw buttons
        self.session_button.draw(self.screen)
        self.stop_button.draw(self.screen)
        self.skin_button.draw(self.screen)

        # Draw note input box on top of everything if active
        if self.typing_note:
            self.draw_note_input()

        pygame.display.flip()

    def display_timer_text(self):
        if not self.curr_session or not self.curr_session.tree:
            return
        time_left = max(0, self.curr_session.tree.duration - self.curr_session.tree.elapsed)
        minutes = int(time_left // 60)
        seconds = int(time_left % 60)
        timer_text = self.timer_font.render(f"{minutes:02d}:{seconds:02d}", True, (255, 255, 255))
        self.screen.blit(timer_text, (SCREEN_WIDTH // 2 - 32, 50))

    # Displays XP, balance, and tree counts in the top left
    def display_user_stats(self):
        stats = [
            f"XP: {self.user.xp}",
            f"Balance: ${self.user.balance}",
            f"Trees: {self.user.total_trees} ({self.user.alive_trees} alive / {self.user.dead_trees} dead)"
        ]
        for i, line in enumerate(stats):
            text = self.font.render(line, True, (200, 255, 200))
            self.screen.blit(text, (10, 10 + i * 30))

    # Draws the note input overlay with a text box
    def draw_note_input(self):
        # Dark overlay behind the box
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 160), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen.blit(overlay, (0, 0))

        # Box background
        box_x = SCREEN_WIDTH // 2 - 200
        box_y = SCREEN_HEIGHT // 2 - 80
        box_w = 400
        box_h = 160
        pygame.draw.rect(self.screen, (5, 31, 32),  (box_x, box_y, box_w, box_h), border_radius=12)
        pygame.draw.rect(self.screen, (50, 50, 65), (box_x, box_y, box_w, box_h), 1, border_radius=12)

        # Prompt label
        label = "Start note:" if self.typing_note == "start" else "End note:"
        prompt = self.font.render(label, True, (255, 255, 255))
        self.screen.blit(prompt, (box_x + 20, box_y + 18))

        # Text input area
        input_rect = (box_x + 20, box_y + 58, box_w - 40, 40)
        pygame.draw.rect(self.screen, (15, 50, 40), input_rect, border_radius=6)
        pygame.draw.rect(self.screen, (80, 200, 120), input_rect, 1, border_radius=6)

        # Current typed text with blinking cursor
        current = self.start_note if self.typing_note == "start" else self.end_note
        typed = self.font.render(current + "|", True, (80, 200, 120))
        self.screen.blit(typed, (box_x + 28, box_y + 66))

        # Hint at the bottom
        hint = self.small_font.render("Press Enter to confirm", True, (130, 130, 155))
        self.screen.blit(hint, (box_x + 20, box_y + 125))

    # --- Event handling ---
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()

            # Handle typing into the note box
            elif event.type == pygame.KEYDOWN and self.typing_note:
                if event.key == pygame.K_RETURN:
                    if self.typing_note == "start":
                        # Start note done — now actually start the session
                        self.curr_session = Session(self.curr_duration)
                        self.curr_session.tree = Tree(self.curr_duration)
                        self.curr_session.tree.alive = True
                        self.typing_note = None
                    elif self.typing_note == "end":
                        # End note done — save and clean up
                        self._finish_session()

                elif event.key == pygame.K_BACKSPACE:
                    # Delete the last character
                    if self.typing_note == "start":
                        self.start_note = self.start_note[:-1]
                    else:
                        self.end_note = self.end_note[:-1]

                else:
                    # Append the typed character
                    if self.typing_note == "start":
                        self.start_note += event.unicode
                    else:
                        self.end_note += event.unicode

            # Only handle button clicks when no note box is open
            elif event.type == pygame.MOUSEBUTTONDOWN and not self.typing_note:
                if self.session_button.rect.collidepoint(event.pos):
                    self.session_button.trigger()
                elif self.stop_button.rect.collidepoint(event.pos):
                    self.stop_button.trigger()
                elif self.skin_button.rect.collidepoint(event.pos):
                    self.skin_button.trigger()

    def quit(self):
        self.running = False
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    app = App()
    app.run()