import pygame
import sys

class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        self.clock = pygame.time.Clock()
        self.running = True

    def run(self):
        self.handle_events()
        self.update()
        self.draw()
        self.clock.tick(60)

    def update(self):
        pass

    def draw(self):
        self.screen.fill((0, 0, 0))
        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

    def quit(self):
        self.running = False
        pygame.quit()
        sys.exit()