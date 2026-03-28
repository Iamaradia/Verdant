import pygame
import subprocess
import sys
from app import App

pygame.init()

WIDTH, HEIGHT = 450, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Verdant")

# Colors
BG = (1, 50, 32)
BOX_BG = (5, 31, 32)
BOX_LINE  = (50, 50, 65)
BOX_HOVER = (45, 45, 60)
WHITE     = (255, 255, 255)
MUTED     = (130, 130, 155)
GREEN     = (80, 200, 120)
GOLD      = (255, 200, 50)
BLUE      = (80, 140, 220)

# Fonts
font_title    = pygame.font.SysFont("Arial", 38, bold=True)
font_subtitle = pygame.font.SysFont("Arial", 15)
font_btn      = pygame.font.SysFont("Arial", 20, bold=True)
font_desc     = pygame.font.SysFont("Arial", 14)


# Draws a rectangle with rounded corners and an optional border
def draw_rounded_rect(surface, color, rect, radius=14, border_color=None, border_width=1):
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border_color:
        pygame.draw.rect(surface, border_color, rect, border_width, border_radius=radius)


# Each button links to a separate file
BUTTONS = [
    {
        "label": "Grower",
        "desc": "Start or continue a focus session",
        "color": GREEN,
        "file": "app.py"
    },
    {
        "label": "Leaderboard",
        "desc": "See who has the most XP",
        "color": GOLD,
        "file": "leaderboard.py"
    },
    {
        "label": "Garden",
        "desc": "View all your planted trees",
        "color": BLUE,
        "file": "garden.py"
    },
]

# Box layout constants
BOX_H   = 90
BOX_W   = WIDTH - 64
START_Y = 220
PADDING = 18


# Returns the index of whichever button the mouse is hovering over, or -1 if none
def get_hovered(mouse_pos):
    for i in range(len(BUTTONS)):
        x = 32
        y = START_Y + i * (BOX_H + PADDING)
        if x <= mouse_pos[0] <= x + BOX_W and y <= mouse_pos[1] <= y + BOX_H:
            return i
    return -1


# Opens the selected page as a separate Python process
def open_page(filename):
    subprocess.Popen([sys.executable, filename])


def draw():
    screen.fill(BG)

    # Title
    title = font_title.render("Verdant", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

    # Subtitle
    sub = font_subtitle.render("Grow trees. Earn XP. Stay focused.", True, MUTED)
    screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 130))

    # Divider line between header and buttons
    pygame.draw.line(screen, BOX_LINE, (32, 180), (WIDTH - 32, 180), 1)

    mouse_pos = pygame.mouse.get_pos()
    hovered   = get_hovered(mouse_pos)

    for i, btn in enumerate(BUTTONS):
        x = 32
        y = START_Y + i * (BOX_H + PADDING)

        # Highlight the box if hovered
        bg = BOX_HOVER if hovered == i else BOX_BG
        draw_rounded_rect(screen, bg, (x, y, BOX_W, BOX_H), radius=14, border_color=BOX_LINE)

        # Colored accent bar on the left side of the box
        pygame.draw.rect(screen, btn["color"], (x, y + 18, 4, BOX_H - 36), border_radius=2)

        # Button label and description
        label = font_btn.render(btn["label"], True, WHITE)
        desc  = font_desc.render(btn["desc"], True, MUTED)
        screen.blit(label, (x + 24, y + 22))
        screen.blit(desc,  (x + 24, y + 52))

        # Arrow on the right in the button's accent color
        arrow = font_btn.render("→", True, btn["color"])
        screen.blit(arrow, (x + BOX_W - arrow.get_width() - 20, y + BOX_H // 2 - arrow.get_height() // 2))

    pygame.display.flip()


# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Open the page when a button is clicked
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            hovered = get_hovered(pygame.mouse.get_pos())
            if hovered != -1:
                open_page(BUTTONS[hovered]["file"])

    draw()

pygame.quit()