import pygame

class Tree:
    def __init__(self):
        self.time_planted = 0
        self.elapsed_time = 0

        self.start_note = ""
        self.end_note = ""

        self.sprite = pygame.Surface((100, 100))
        self.sprite.fill((255, 255, 255))
        self.rect = self.sprite.get_rect()

    def update(self, dt):
        self.elapsed_time += dt

    def draw(self, surface):
        surface.blit(self.sprite, self.rect)