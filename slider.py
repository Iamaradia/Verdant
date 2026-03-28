import pygame

class Slider:
    def __init__(self, pos, width, min_val, max_val, start_val):
        self.x, self.y = pos
        self.width = width
        self.height = 8
        self.min_val = min_val
        self.max_val = max_val
        self.value = start_val

        self.handle_radius = 12
        self.dragging = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if (mx - self.get_handle_x()) ** 2 + (my - self.y) ** 2 < self.handle_radius ** 2:
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            mx, _ = event.pos
            mx = max(self.x, min(self.x + self.width, mx))
            self.value = self.min_val + (self.max_val - self.min_val) * ((mx - self.x) / self.width)

    def get_handle_x(self):
        return self.x + (self.value - self.min_val) / (self.max_val - self.min_val) * self.width

    def draw(self, surface):
        # Draw line
        pygame.draw.rect(surface, (200, 200, 200), (self.x, self.y - self.height // 2, self.width, self.height))
        # Draw handle
        handle_x = int(self.get_handle_x())
        pygame.draw.circle(surface, (255, 100, 100), (handle_x, self.y), self.handle_radius)