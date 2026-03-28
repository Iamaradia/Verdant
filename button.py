import pygame

class Button:
    def __init__(self, pos, size, bg_color="white", text="Button", font_size=30, on_click=None):
        self.surface = pygame.Surface(size)
        self.surface.fill(bg_color)
        self.rect = self.surface.get_rect(topleft=pos)

        self.font = pygame.font.SysFont('Arial', font_size)
        self.text_surface = self.font.render(text, True, (0, 0, 0))
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

        self.on_click = on_click

    def trigger(self):
        if self.on_click:
            self.on_click()

    def draw(self, surface):
        surface.blit(self.surface, self.rect)
        surface.blit(self.text_surface, self.text_rect)