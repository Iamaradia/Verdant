import pygame
import sys

from session import Session
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
        self.font = pygame.font.SysFont(None, 48)

        self.curr_session = None
        self.curr_duration = 1500

        def on_session_button_click():
            self.start_new_session(duration=self.curr_duration)

        self.session_button = Button(
            (SCREEN_WIDTH // 2 - 84, SCREEN_HEIGHT // 2),
            (200, 50),
            text="Start Session",
            bg_color="green",
            font_size=20,
            on_click=on_session_button_click
        )

        self.tree_image = pygame.image.load("tree.png")

    def run(self):
        self.handle_events()
        self.update()
        self.draw()
        self.dt = self.clock.tick(60) / 1000

    def update(self):
        if self.curr_session:
            self.curr_session.update(self.dt)

    def draw(self):
        self.screen.fill((0, 100, 0))

        if self.curr_session:
            self.display_timer_text()

        self.session_button.draw(self.screen)
        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.session_button.rect.collidepoint(event.pos):
                    self.session_button.trigger()

    def quit(self):
        self.running = False
        pygame.quit()
        sys.exit()

    def display_timer_text(self):
        time_left = self.curr_session.tree.duration - self.curr_session.tree.elapsed
        minutes = int(time_left // 60)
        seconds = int(time_left % 60)

        timer_text = self.font.render(f"{minutes}:{seconds}", True, (255, 255, 255))
        self.screen.blit(timer_text, (SCREEN_WIDTH // 2 - 32, SCREEN_HEIGHT - 100))

    def start_new_session(self, duration):
        if self.curr_session:
            self.curr_session = None

        self.curr_session = Session(duration)



