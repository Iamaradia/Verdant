import pygame
import os
import json
import random
import math

# ============================================================
#  CONFIGURATION
# ============================================================
TILE_WIDTH       = 64      # pixels wide per tile (must be even)
TILE_HEIGHT      = 64      # pixels tall per tile (must be even)
STEP_X           = 64      # horizontal distance between tile origins
STEP_Y           = 30      # vertical distance between tile origins — lower = closer together
WINDOW_WIDTH     = 800
WINDOW_HEIGHT    = 600
FPS              = 60
BACKGROUND_COLOR = (30, 30, 30)
ZOOM_STEP        = 0.1
ZOOM_MIN         = 0.2
ZOOM_MAX         = 4.0
TREE_ASSETS_DIR  = "assets/trees"
USER_DATA_PATH   = "user_data.json"
TREE_DENSITY     = 0.15
GRID_EDGE_BUFFER = 2
MIN_TREE_SPACING = 2
# ============================================================


def load_tiles():
    ray = pygame.image.load("assets/grass_tile.png")
    ray.set_colorkey(ray.get_at((0, 0)))
    ray = pygame.transform.scale(ray, (TILE_WIDTH, TILE_HEIGHT))
    return ray


def load_user_data():
    with open(USER_DATA_PATH, "r") as f:
        return json.load(f)


def load_tree_images():
    data = load_user_data()
    images = {}
    for user in data["users"].values():
        for tree in user["trees"].values():
            filename = tree["type"]
            if filename not in images:
                path = os.path.join(TREE_ASSETS_DIR, filename)
                img = pygame.image.load(path).convert_alpha()
                images[filename] = img
    return images


def compute_grid_extent(num_trees: int, density: float = TREE_DENSITY) -> int:
    spacing_footprint = (MIN_TREE_SPACING + 1) ** 2
    adjusted_density  = density / spacing_footprint
    min_tiles = num_trees / adjusted_density
    extent = math.ceil((math.sqrt(min_tiles) - 1) / 2)
    extent += GRID_EDGE_BUFFER
    return max(extent, 5)


def grid_to_screen(gx, gy):
    sx = (gx - gy) * (STEP_X / 2)
    sy = (gx + gy) * (STEP_Y / 2)
    return sx, sy


def build_tree_list(tree_images: dict, grid_extent: int) -> list:
    data = load_user_data()
    trees = []
    occupied = set()
    placed   = []

    min_x = -grid_extent + GRID_EDGE_BUFFER
    max_x =  grid_extent - GRID_EDGE_BUFFER
    min_y = -grid_extent + GRID_EDGE_BUFFER
    max_y =  grid_extent - GRID_EDGE_BUFFER

    all_entries = [
        (tree_id, tree)
        for user in data["users"].values()
        for tree_id, tree in user["trees"].items()
    ]

    for tree_id, tree in all_entries:
        placed_ok = False
        for _ in range(1000):
            gx = random.randint(min_x, max_x)
            gy = random.randint(min_y, max_y)
            if (gx, gy) in occupied:
                continue
            too_close = any(
                abs(gx - px) < MIN_TREE_SPACING and abs(gy - py) < MIN_TREE_SPACING
                for px, py in placed
            )
            if too_close:
                continue
            occupied.add((gx, gy))
            placed.append((gx, gy))
            trees.append({
                "id":     tree_id,
                "image":  tree_images[tree["type"]],
                "grid_x": gx,
                "grid_y": gy,
                "alive":  tree["alive"],
                "data":   tree,
            })
            placed_ok = True
            break

        if not placed_ok:
            print(f"Warning: could not place tree {tree_id} with spacing, placing freely.")
            while True:
                gx = random.randint(min_x, max_x)
                gy = random.randint(min_y, max_y)
                if (gx, gy) not in occupied:
                    occupied.add((gx, gy))
                    placed.append((gx, gy))
                    trees.append({
                        "id":     tree_id,
                        "image":  tree_images[tree["type"]],
                        "grid_x": gx,
                        "grid_y": gy,
                        "alive":  tree["alive"],
                        "data":   tree,
                    })
                    break

    return trees


class GardenTile(pygame.sprite.Sprite):
    def __init__(self, image, x, y, grid_x, grid_y):
        super().__init__()
        self.image = image
        self.rect  = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.grid_x = grid_x
        self.grid_y = grid_y


class Camera:
    def __init__(self, start_x, start_y):
        self.offset      = [start_x, start_y]
        self.zoom        = 1.0
        self.dragging    = False
        self.drag_start  = (0, 0)
        self.offset_start = [0, 0]

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.dragging     = True
                self.drag_start   = event.pos
                self.offset_start = list(self.offset)
            elif event.button == 4:
                self._zoom_toward(event.pos,  ZOOM_STEP)
            elif event.button == 5:
                self._zoom_toward(event.pos, -ZOOM_STEP)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            dx = event.pos[0] - self.drag_start[0]
            dy = event.pos[1] - self.drag_start[1]
            self.offset[0] = self.offset_start[0] + dx
            self.offset[1] = self.offset_start[1] + dy

    def _zoom_toward(self, mouse_pos, step):
        old_zoom   = self.zoom
        self.zoom  = max(ZOOM_MIN, min(ZOOM_MAX, self.zoom + step))
        scale      = self.zoom / old_zoom
        self.offset[0] = mouse_pos[0] + (self.offset[0] - mouse_pos[0]) * scale
        self.offset[1] = mouse_pos[1] + (self.offset[1] - mouse_pos[1]) * scale


class TreeInfoBox:
    def __init__(self):
        pygame.font.init()
        self.font_title  = pygame.font.SysFont("segoeui", 14, bold=True)
        self.font_label  = pygame.font.SysFont("segoeui", 11, bold=True)
        self.font_body   = pygame.font.SysFont("segoeui", 12)

        self.visible      = False
        self.tree         = None
        self.anchor_x     = 0
        self.anchor_y     = 0

        self.padding      = 12
        self.box_width    = 230
        self.line_gap     = 3
        self.bg_color     = (18, 18, 18)
        self.border_color = (70, 70, 70)
        self.text_color   = (220, 220, 220)
        self.muted_color  = (130, 130, 130)
        self.alive_color  = (90, 195, 90)
        self.dead_color   = (195, 75, 75)
        self.div_color    = (50, 50, 50)

    def show(self, tree, anchor_x, anchor_y):
        self.visible  = True
        self.tree     = tree
        self.anchor_x = anchor_x
        self.anchor_y = anchor_y

    def hide(self):
        self.visible = False
        self.tree    = None

    def _lines(self):
        d      = self.tree["data"]
        alive  = self.tree["alive"]
        status = "Alive" if alive else "Dead"
        s_col  = self.alive_color if alive else self.dead_color
        pct    = int(d["elapsed"] / d["duration"] * 100) if d["duration"] else 0
        prog   = f'{d["elapsed"]} / {d["duration"]} min  ({pct}%)'

        return [
            ("title",  f'Tree  #{self.tree["id"]}',          self.text_color),
            ("body",   d["type"].replace(".png", ""),         self.muted_color),
            ("div",    None,                                  None),
            ("label",  "STATUS",                              self.muted_color),
            ("body",   status,                                s_col),
            ("label",  "PROGRESS",                            self.muted_color),
            ("body",   prog,                                  self.text_color),
            ("label",  "VOTES",                               self.muted_color),
            ("body",   f'Up: {d["upvotes"]}   Down: {d["downvotes"]}', self.text_color),
            ("div",    None,                                  None),
            ("label",  "START NOTE",                          self.muted_color),
            ("body",   d["start_note"],                       self.text_color),
            ("label",  "END NOTE",                            self.muted_color),
            ("body",   d["end_note"],                         self.text_color),
        ]

    def draw(self, screen):
        if not self.visible or self.tree is None:
            return

        lines      = self._lines()
        lh_title   = self.font_title.get_height()
        lh_label   = self.font_label.get_height()
        lh_body    = self.font_body.get_height()
        div_h      = 10
        p          = self.padding

        # Measure height
        total_h = p * 2
        for kind, text, _ in lines:
            if kind == "div":
                total_h += div_h
            elif kind == "title":
                total_h += lh_title + self.line_gap + 2
            elif kind == "label":
                total_h += lh_label + self.line_gap
            else:
                total_h += lh_body + self.line_gap + 4

        sw, sh = screen.get_size()
        bw, bh = self.box_width, total_h

        # Pin box to right of tree, nudge onto screen
        bx = self.anchor_x + 12
        by = self.anchor_y - bh // 2
        if bx + bw > sw - 4: bx = self.anchor_x - bw - 12
        if by < 4:            by = 4
        if by + bh > sh - 4:  by = sh - bh - 4

        # Background + border
        rect = pygame.Rect(bx, by, bw, bh)
        pygame.draw.rect(screen, self.bg_color,    rect, border_radius=7)
        pygame.draw.rect(screen, self.border_color, rect, width=1, border_radius=7)

        cy = by + p
        for kind, text, color in lines:
            if kind == "div":
                pygame.draw.line(
                    screen, self.div_color,
                    (bx + p, cy + div_h // 2),
                    (bx + bw - p, cy + div_h // 2)
                )
                cy += div_h
            elif kind == "title":
                surf = self.font_title.render(text, True, color)
                screen.blit(surf, (bx + p, cy))
                cy += lh_title + self.line_gap + 2
            elif kind == "label":
                surf = self.font_label.render(text, True, color)
                screen.blit(surf, (bx + p, cy))
                cy += lh_label + self.line_gap
            else:
                surf = self.font_body.render(text, True, color)
                screen.blit(surf, (bx + p, cy))
                cy += lh_body + self.line_gap + 4


class Garden:
    def __init__(self, tree_images, grid_extent):
        self.tile_width   = TILE_WIDTH
        self.tile_height  = TILE_HEIGHT
        self.grid_extent  = grid_extent
        self.grass_tile   = load_tiles()
        self.grass_tiles_group = pygame.sprite.Group()
        self.palettes     = ["grass", "dirt"]
        self._scaled_tile_cache = {}
        self._scaled_tree_cache = {}
        self.create_tiles()
        self.tree_images  = tree_images
        self.trees        = build_tree_list(tree_images, grid_extent)
        self.info_box     = TreeInfoBox()
        self.selected_tree = None   # tree dict currently clicked

    def create_tiles(self):
        self.grass_tiles_group.empty()
        ext = self.grid_extent
        for x in range(-ext, ext + 1):
            for y in range(-ext, ext + 1):
                tile_x = (x - y) * (STEP_X / 2)
                tile_y = (x + y) * (STEP_Y / 2)
                self.grass_tiles_group.add(
                    GardenTile(self.grass_tile, tile_x, tile_y, x, y)
                )

    def _get_scaled_tile(self, zoom):
        key = round(zoom, 2)
        if key not in self._scaled_tile_cache:
            w = max(1, int(TILE_WIDTH  * zoom))
            h = max(1, int(TILE_HEIGHT * zoom))
            self._scaled_tile_cache[key] = pygame.transform.scale(self.grass_tile, (w, h))
        return self._scaled_tile_cache[key]

    def _get_scaled_tree(self, image, tree_id, zoom):
        key = (tree_id, round(zoom, 2))
        if key not in self._scaled_tree_cache:
            ow, oh = image.get_size()
            w = max(1, int(ow * zoom))
            h = max(1, int(oh * zoom))
            self._scaled_tree_cache[key] = pygame.transform.scale(image, (w, h))
        return self._scaled_tree_cache[key]

    def handle_click(self, mouse_pos, camera):
        """Called on MOUSEBUTTONUP to select/deselect a tree."""
        zoom       = camera.zoom
        scaled_tile = self._get_scaled_tile(zoom)
        tile_w     = scaled_tile.get_width()
        tile_h     = scaled_tile.get_height()

        clicked = None
        for tree in sorted(self.trees, key=lambda t: t["grid_x"] + t["grid_y"]):
            sx, sy  = grid_to_screen(tree["grid_x"], tree["grid_y"])
            img     = self._get_scaled_tree(tree["image"], tree["id"], zoom)
            tw, th  = img.get_size()
            draw_x  = sx * zoom + camera.offset[0] + (tile_w / 2) - (tw / 2)
            draw_y  = sy * zoom + camera.offset[1] + (tile_h / 2) - th
            if pygame.Rect(draw_x, draw_y, tw, th).collidepoint(mouse_pos):
                clicked = tree

        if clicked and clicked is not self.selected_tree:
            self.selected_tree = clicked
        else:
            self.selected_tree = None   # click same tree or empty space = deselect

    def draw(self, screen, camera):
        zoom = camera.zoom
        scaled_tile = self._get_scaled_tile(zoom)
        tile_w = scaled_tile.get_width()
        tile_h = scaled_tile.get_height()
        mouse_pos = pygame.mouse.get_pos()

        # Tiles
        for tile in self.grass_tiles_group:
            x = tile.rect.x * zoom + camera.offset[0]
            y = tile.rect.y * zoom + camera.offset[1]
            screen.blit(scaled_tile, (x, y))

        # Resolve draw positions first so we can find the topmost hovered tree
        draw_data = []
        for tree in sorted(self.trees, key=lambda t: t["grid_x"] + t["grid_y"]):
            sx, sy = grid_to_screen(tree["grid_x"], tree["grid_y"])
            base = self._get_scaled_tree(tree["image"], tree["id"], zoom)
            tw, th = base.get_size()
            draw_x = sx * zoom + camera.offset[0] + (tile_w / 2) - (tw / 2)
            draw_y = sy * zoom + camera.offset[1] + (tile_h / 2) - th
            draw_data.append((tree, base, draw_x, draw_y, tw, th))

        # Topmost hovered = last in depth-sorted list whose rect contains the mouse
        hovered_id = None
        for tree, base, draw_x, draw_y, tw, th in draw_data:
            if pygame.Rect(draw_x, draw_y, tw, th).collidepoint(mouse_pos):
                hovered_id = tree["id"]  # keep overwriting — last one wins

        info_target = None

        for tree, base, draw_x, draw_y, tw, th in draw_data:
            is_hovered = (tree["id"] == hovered_id)
            is_selected = self.selected_tree and self.selected_tree["id"] == tree["id"]

            img = base.copy()

            if is_selected:
                lighten = pygame.Surface((tw, th))  # no SRCALPHA — RGB only
                lighten.fill((60, 60, 60))
                img.blit(lighten, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
            elif is_hovered:
                img.set_alpha(160)

            screen.blit(img, (draw_x, draw_y))

            if is_selected:
                info_target = (tree, int(draw_x + tw), int(draw_y + th // 2))

        if info_target:
            self.info_box.show(*info_target)
        else:
            self.info_box.hide()

        self.info_box.draw(screen)

    def update(self):
        pass

    def reset_tiles(self):
        self.create_tiles()


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Isometric Garden")
    clock  = pygame.time.Clock()

    data        = load_user_data()
    num_trees   = sum(len(u["trees"]) for u in data["users"].values())
    grid_extent = compute_grid_extent(num_trees, TREE_DENSITY)

    tree_images = load_tree_images()
    garden      = Garden(tree_images, grid_extent)
    camera      = Camera(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)

    running     = True
    mouse_moved = False  # detect drag vs click

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            camera.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_moved = False
            if event.type == pygame.MOUSEMOTION and camera.dragging:
                mouse_moved = True
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if not mouse_moved:
                    garden.handle_click(event.pos, camera)

        screen.fill(BACKGROUND_COLOR)
        garden.draw(screen, camera)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()