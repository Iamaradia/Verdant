import pygame
import sys
from session import Session
from tree import Tree  # Make sure your Tree class has an 'alive' property
from button import Button

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0
        self.font = pygame.font.SysFont(None, 36)
        self.timer_font = pygame.font.SysFont(None, 48)

        self.curr_session = None
        self.curr_duration = 10  # seconds

        # Tree skins
        self.tree_skins = [
            pygame.image.load("oak.png").convert_alpha(),
            pygame.image.load("spruce.png").convert_alpha(),
            pygame.image.load("crimson_spruce.png").convert_alpha(),
            pygame.image.load("cherry_oak.png").convert_alpha(),
        ]
        self.tree_index = 0
        self.tree_image = self.tree_skins[self.tree_index]

        # Dictionary to store completed trees
        self.completed_trees = {}

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
        self.curr_session = Session(self.curr_duration)
        self.curr_session.tree = Tree(self.curr_duration)
        self.curr_session.tree.alive = True

    def stop_session(self):
        if self.curr_session and self.curr_session.tree:
            self.curr_session.tree.alive = False
            tree_id = len(self.completed_trees) + 1
            self.completed_trees[tree_id] = self.curr_session.tree
        self.curr_session = None

    def change_skin(self):
        self.tree_index = (self.tree_index + 1) % len(self.tree_skins)
        self.tree_image = self.tree_skins[self.tree_index]

    # --- Game logic ---
    def update(self):
        if self.curr_session:
            self.curr_session.update(self.dt)
            if self.curr_session.is_finished():
                tree_id = len(self.completed_trees) + 1
                self.completed_trees[tree_id] = self.curr_session.tree
                self.curr_session = None
                print(self.completed_trees)

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

        # Draw completed trees info
        self.display_completed_trees()

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

    def display_completed_trees(self):
        y_offset = 10
        for tree_id, tree in self.completed_trees.items():
            status = "Alive" if getattr(tree, 'alive', False) else "Dead"
            text = self.font.render(f"Tree {tree_id}: {status}", True, (255, 255, 0))
            self.screen.blit(text, (10, y_offset))
            y_offset += 30

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