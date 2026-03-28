import pygame
import sys

from session import Session
from button import Button
from slider import Slider

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0
        self.font = pygame.font.SysFont(None, 48)

        self.curr_session = None
        self.curr_duration = 10

        def on_session_button_click():
            self.start_new_session(duration=self.curr_duration)

        self.session_button = Button(
            (SCREEN_WIDTH // 2 - 84, SCREEN_HEIGHT // 2 + 64),
            (200, 50),
            text="Start Session",
            bg_color=(5, 31, 32),
            font_size=20,
            on_click=on_session_button_click
        )

        self.tree_skins = [
            pygame.image.load("tree.png").convert_alpha(),
            pygame.image.load("tree2.png").convert_alpha(),
        ]
        self.tree_index = 0
        self.tree_image = self.tree_skins[self.tree_index]

        def on_change_skin():
            self.tree_index = (self.tree_index + 1) % len(self.tree_skins)
            self.tree_image = self.tree_skins[self.tree_index]

        self.skin_button = Button(
            (SCREEN_WIDTH // 2 - 84, SCREEN_HEIGHT // 2 + 130),  # below session button
            (200, 50),
            text="Change Skin",
            bg_color=(5, 31, 32),
            font_size=20,
            on_click=on_change_skin
        )

        self.trees = []
        self.tree_image = pygame.image.load("tree.png")

        def on_stop_button_click():
            if self.curr_session:
                self.curr_session = None  # stop current session

        self.stop_button = Button(
            (SCREEN_WIDTH // 2 - 84, SCREEN_HEIGHT // 2 + 195),  # below skin button
            (200, 50),
            text="Stop Session",
            bg_color=(150, 0, 0),
            font_size=20,
            on_click=on_stop_button_click
        )


    def run(self):
        self.handle_events()
        self.update()
        self.draw()
        self.dt = self.clock.tick(60) / 1000

    def update(self):
        if self.curr_session:
            self.curr_session.update(self.dt)

    def draw(self):
        # Fill background
        self.screen.fill( (1, 50, 32))

        # Draw tree
        if self.curr_session:
            # Optional: scale tree based on progress
            progress = self.curr_session.tree.elapsed / self.curr_session.tree.duration
            scale = 0.5 + 0.5 * progress  # grows from 50% to 100%
            tree_scaled = pygame.transform.smoothscale(
                self.tree_image,
                (int(self.tree_image.get_width() * scale),
                 int(self.tree_image.get_height() * scale))
            )
            # Center tree on screen
            tree_rect = tree_scaled.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(tree_scaled, tree_rect)

            if self.curr_session.is_finished():
                self.trees.append(self.curr_session.tree)
                self.curr_session = None
        else:
            # Default tree if no session running
            tree_rect = self.tree_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(self.tree_image, tree_rect)

        # Draw timer
        if self.curr_session:
            self.display_timer_text()

        # Draw button
        self.session_button.draw(self.screen)
        self.skin_button.draw(self.screen)
        self.stop_button.draw(self.screen)

        # Update display
        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.session_button.rect.collidepoint(event.pos):
                    self.session_button.trigger()
                elif self.skin_button.rect.collidepoint(event.pos):
                    self.skin_button.trigger()
                elif self.stop_button.rect.collidepoint(event.pos):
                    self.stop_button.trigger()

    def quit(self):
        self.running = False
        pygame.quit()
        sys.exit()

    def display_timer_text(self):
        time_left = self.curr_session.tree.duration - self.curr_session.tree.elapsed
        minutes = int(time_left // 60)
        seconds = int(time_left % 60)

        # Pad zeros for display (e.g., 05:03)
        timer_text = self.font.render(f"{minutes:02d}:{seconds:02d}", True, (255, 255, 255))
        self.screen.blit(timer_text, (SCREEN_WIDTH // 2 - 32, SCREEN_HEIGHT - 100))

    def start_new_session(self, duration):
        if self.curr_session:
            self.curr_session = None

        self.curr_session = Session(duration)



