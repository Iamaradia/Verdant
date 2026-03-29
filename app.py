
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
        self.timer_font = pygame.font.SysFont(None, 48)

        # Load or create the user
        self.user = User.get("User")

        self.curr_session = None
        self.curr_duration = 10

        # Tree skins
        self.tree_skins = [
            pygame.image.load("assets/trees/oak.png").convert_alpha(),
            pygame.image.load("assets/trees/spruce.png").convert_alpha(),
            pygame.image.load("assets/trees/crimson_spruce.png").convert_alpha(),
            pygame.image.load("assets/trees/cherry_oak.png").convert_alpha(),
        ]
        self.tree_index = 0
        self.tree_image = self.tree_skins[self.tree_index]

        # Skin names match the image files so we can save the type
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
        # Don't start a new session if one is already running
        if self.curr_session:
            return
        self.curr_session = Session(self.curr_duration)
        self.curr_session.tree = Tree(self.curr_duration)
        self.curr_session.tree.alive = True

    def stop_session(self):
        # Stop the session early and save it as a dead tree
        if self.curr_session and self.curr_session.tree:
            self.curr_session.tree.alive = False
            self._save_tree(self.curr_session.tree, alive=False)
        self.curr_session = None

    def change_skin(self):
        self.tree_index = (self.tree_index + 1) % len(self.tree_skins)
        self.tree_image = self.tree_skins[self.tree_index]

    # --- Saves a completed or stopped tree to the user's data ---
    def _save_tree(self, tree, alive):
        skin_name = self.tree_skin_names[self.tree_index]

        # Give XP and balance based on whether the tree survived
        if alive:
            self.user.update_xp(XP_ALIVE)
            self.user.update_balance(BAL_ALIVE)
        else:
            self.user.update_xp(XP_DEAD)
            self.user.update_balance(BAL_DEAD)

        # Save the tree to the user's JSON
        self.user.add_tree(
            tree=skin_name,
            elapsed=round(tree.elapsed, 2),
            duration=tree.duration,
            alive=alive,
            upvotes=getattr(tree, "upvotes", 0),
            downvotes=getattr(tree, "downvotes", 0),
            start_note=getattr(tree, "start_note", ""),
            end_note=getattr(tree, "end_note", "")
        )

        print(f"Tree saved — alive: {alive}, XP: {self.user.xp}, balance: {self.user.balance}")

    # --- Game logic ---
    def update(self):
        if self.curr_session:
            self.curr_session.update(self.dt)

            # Session finished naturally — tree is alive
            if self.curr_session.is_finished():
                self._save_tree(self.curr_session.tree, alive=True)
                self.curr_session = None

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

        pygame.display.flip()

    def display_timer_text(self):
        if not self.curr_session or not self.curr_session.tree:
            return
        time_left = max(0, self.curr_session.tree.duration - self.curr_session.tree.elapsed)
        minutes = int(time_left // 60)
        seconds = int(time_left % 60)
        timer_text = self.timer_font.render(f"{minutes:02d}:{seconds:02d}", True, (255, 255, 255))
        self.screen.blit(timer_text, (SCREEN_WIDTH // 2 - 32, 50))

    # Displays XP, balance, and tree counts in the corner
    def display_user_stats(self):
        stats = [
            f"XP: {self.user.xp}",
            f"Balance: ${self.user.balance}",
            f"Trees: {self.user.total_trees} ({self.user.alive_trees} alive / {self.user.dead_trees} dead)"
        ]
        for i, line in enumerate(stats):
            text = self.font.render(line, True, (200, 255, 200))
            self.screen.blit(text, (10, 10 + i * 30))

    # --- Event handling ---
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
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