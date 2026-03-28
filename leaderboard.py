import pygame
from user_handler import *

pygame.init()

# Gives the size
WIDTH, HEIGHT = 450, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Leaderboard")

# Gets the colours
BG = (1, 50, 32)
BOX_BG = (5, 31, 32)
BOX_LINE = (50, 50, 65)
GOLD = (255, 200, 50)
SILVER = (180, 180, 200)
BRONZE = (190, 120, 60)
WHITE = (255, 255, 255)
MUTED = (130, 130, 155)

# Gets the fonts for each
font_title = pygame.font.SysFont("Arial", 32, bold=True)
font_rank = pygame.font.SysFont("Arial", 20, bold=True)
font_name = pygame.font.SysFont("Arial", 20, bold=True)
font_stat = pygame.font.SysFont("Arial", 15)

MEDAL_COLORS = [GOLD, SILVER, BRONZE]


# Loads all users and sorts them by XP highest to lowest
def get_leaderboard():
    data = load_data()
    users = [
        User._from_data(user_id, user)
        for user_id, user in data["users"].items()
    ]
    return sorted(users, key=lambda u: u.xp, reverse=True)


# Draws a rectangle with rounded corners, with an optional border
def draw_rounded_rect(surface, color, rect, radius=12, border_color=None, border_width=1):
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border_color:
        pygame.draw.rect(surface, border_color, rect, border_width, border_radius=radius)


def draw_leaderboard():
    screen.fill(BG)

    # Draw the title centered at the top
    title = font_title.render("Leaderboard", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 24))

    leaderboard = get_leaderboard()

    # Box dimensions and spacing
    BOX_H = 72
    BOX_W = WIDTH - 48
    START_Y = 90
    PADDING = 12

    for i, user in enumerate(leaderboard):
        # Position of each box
        x = 24
        y = START_Y + i * (BOX_H + PADDING)

        # Draw the background box
        draw_rounded_rect(screen, BOX_BG, (x, y, BOX_W, BOX_H), radius=12, border_color=BOX_LINE)

        # Gold, silver, bronze for top 3, gray for the rest
        rank_color = MEDAL_COLORS[i] if i < 3 else MUTED

        # Rank number on the left
        rank_text = font_rank.render(f"#{i + 1}", True, rank_color)
        screen.blit(rank_text, (x + 16, y + BOX_H // 2 - rank_text.get_height() // 2))

        # Username
        name_text = font_name.render(user.name, True, WHITE)
        screen.blit(name_text, (x + 64, y + 14))

        # XP, balance, and tree count below the name
        stat_text = font_stat.render(
            f"{user.xp} XP  •  ${user.balance} balance  •  {user.total_trees} trees",
            True, MUTED
        )
        screen.blit(stat_text, (x + 64, y + 38))

        # XP value on the far right
        xp_label = font_rank.render(str(user.xp), True, rank_color)
        screen.blit(xp_label, (x + BOX_W - xp_label.get_width() - 16, y + BOX_H // 2 - xp_label.get_height() // 2))

    # Push everything to the screen
    pygame.display.flip()


# Main loop — redraws the leaderboard every frame until the window is closed
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    draw_leaderboard()

pygame.quit()
