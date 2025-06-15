from pathlib import Path
import pygame
import random
import os
import sys

pygame.init()
WIDTH, HEIGHT = 1000, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hwatu mini game")

CARD_WIDTH, CARD_HEIGHT = 101, 166
ASSETS_PATH = "assets"
LAYER_OFFSET = 6
SLOT_LIMIT = 7
NUM_LAYERS = 10
GRID_COLS, GRID_ROWS = 6, 4

TOTAL_WIDTH = CARD_WIDTH * GRID_COLS + LAYER_OFFSET * (NUM_LAYERS - 1)
TOTAL_HEIGHT = CARD_HEIGHT * GRID_ROWS + LAYER_OFFSET * (NUM_LAYERS - 1)
GRID_START_X = (WIDTH - TOTAL_WIDTH) // 2
GRID_START_Y = (HEIGHT - 230 - TOTAL_HEIGHT) // 2

font = pygame.font.SysFont("arial", 48)
undo_stack = []
game_won = False

tile_images = []
assets_path = Path(ASSETS_PATH)
if assets_path.exists():
    for file in os.listdir(ASSETS_PATH):
        if file.endswith(".jpg"):
            img = pygame.image.load(os.path.join(ASSETS_PATH, file)).convert_alpha()
            img = pygame.transform.scale(img, (CARD_WIDTH, CARD_HEIGHT))
            tile_images.append((file, img))
if not tile_images:
    print("No pics，put in assets/")
    pygame.quit()
    sys.exit()

TILE_STACK = []
slot = []

def create_stack():
    TILE_STACK.clear()
    all_cards = []

    chosen = random.sample(tile_images, 16)
    for name, img in chosen:
        for _ in range(9):
            all_cards.append({'name': name, 'img': img})

    assert len(all_cards) == 144

    positions = []
    for layer in range(NUM_LAYERS):
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                x = GRID_START_X + col * (CARD_WIDTH + 10) + layer * LAYER_OFFSET
                y = GRID_START_Y + row * (CARD_HEIGHT + 10) + layer * LAYER_OFFSET
                positions.append((x, y, layer))

    positions = sorted(positions, key=lambda p: p[2])
    random.shuffle(all_cards)

    for pos, card in zip(positions, all_cards):
        TILE_STACK.append({
            'name': card['name'],
            'img': card['img'],
            'pos': pos
        })

def is_uncovered(tile):
    x1, y1, z1 = tile['pos']
    for other in TILE_STACK:
        if other == tile:
            continue
        x2, y2, z2 = other['pos']
        if z2 > z1:
            cx, cy = x1 + CARD_WIDTH // 2, y1 + CARD_HEIGHT // 2
            if x2 <= cx <= x2 + CARD_WIDTH and y2 <= cy <= y2 + CARD_HEIGHT:
                return False
    return True

def draw():
    screen.fill((240, 230, 200))

    # 分层绘制卡牌
    for layer in range(NUM_LAYERS):
        for tile in [t for t in TILE_STACK if t['pos'][2] == layer]:
            x, y, _ = tile['pos']
            screen.blit(tile['img'], (x, y))
            pygame.draw.rect(screen, (0, 0, 0), (x, y, CARD_WIDTH, CARD_HEIGHT), 2)

    # 绘制卡槽
    pygame.draw.rect(screen, (200, 200, 200), (50, HEIGHT - 190, 900, 170), border_radius=8)
    for i, t in enumerate(slot):
        px = 60 + i * (CARD_WIDTH + 10)
        py = HEIGHT - 180
        screen.blit(t['img'], (px, py))
        pygame.draw.rect(screen, (0, 0, 0), (px, py, CARD_WIDTH, CARD_HEIGHT), 2)

    # 撤销按钮
    pygame.draw.rect(screen, (100, 100, 100), (850, HEIGHT - 50, 100, 40), border_radius=6)
    undo_text = pygame.font.SysFont("arial", 20).render("Back", True, (255, 255, 255))
    screen.blit(undo_text, (880, HEIGHT - 45))

    if game_won:
        msg = font.render("Congratulations!", True, (0, 100, 0))
        screen.blit(msg, ((WIDTH - msg.get_width()) // 2, HEIGHT // 2 - 30))

    pygame.display.flip()

def handle_click(pos):
    global game_won, slot

    if game_won:
        return

    # 撤销按钮
    if 850 <= pos[0] <= 950 and HEIGHT - 50 <= pos[1] <= HEIGHT - 10:
        if undo_stack:
            stack_data, slot_data = undo_stack.pop()

            # 恢复 TILE_STACK
            TILE_STACK.clear()
            for item in stack_data:
                for name, img in tile_images:
                    if name == item['name']:
                        TILE_STACK.append({'name': name, 'img': img, 'pos': item['pos']})
                        break

            # 恢复 slot
            slot.clear()
            for item in slot_data:
                for name, img in tile_images:
                    if name == item['name']:
                        slot.append({'name': name, 'img': img})
                        break
        return

    for tile in reversed(TILE_STACK):
        x, y, _ = tile['pos']
        rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        if rect.collidepoint(pos) and is_uncovered(tile):
            if len(slot) >= SLOT_LIMIT:
                print("game over")
                return

            backup_stack = [{'name': t['name'], 'pos': t['pos']} for t in TILE_STACK]
            backup_slot = [{'name': t['name']} for t in slot]
            undo_stack.append((backup_stack, backup_slot))

            TILE_STACK.remove(tile)
            slot.append(tile)

            count = {}
            for t in slot:
                count[t['name']] = count.get(t['name'], 0) + 1
            for name, c in count.items():
                if c >= 3:
                    slot = [t for t in slot if t['name'] != name]
                    print(f"clean: {name}")

            if not TILE_STACK:
                game_won = True
            return

create_stack()
clock = pygame.time.Clock()
running = True
while running:
    draw()
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        elif e.type == pygame.MOUSEBUTTONDOWN:
            handle_click(e.pos)
    clock.tick(30)

pygame.quit()
