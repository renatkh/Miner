import pygame
import random
import sys
import time
from collections import deque  # For pathfinding

# Initialize Pygame
pygame.init()

# Constants
GRID_SIZE = 40
CELL_SIZE = 50
SCREEN_SIZE = GRID_SIZE * CELL_SIZE
SCREEN = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
pygame.display.set_caption("Simple Game")

# Colors
WHITE = (255, 255, 255)
GRAY = (160, 160, 160)
GREEN = (0, 255, 0)
BROWN = (156, 93, 82)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)

# Game field
field = [['empty' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

# Place materials randomly
for _ in range(int(GRID_SIZE * GRID_SIZE * 0.95)):  # 95% of the field
    x = random.randint(0, GRID_SIZE - 1)
    y = random.randint(0, GRID_SIZE - 1)
    field[y][x] = 'material'

# Player attributes
player_pos = [0, 0]
player_inventory = 0
player_blue_ore_inventory = 0
player_health = 5

# Zombies attributes
zombies = [
    {'pos': [GRID_SIZE - 1, GRID_SIZE - 1], 'health': 5,
        'shocked': False, 'shock_time': 0, 'attack_time': 0},
    {'pos': [GRID_SIZE - 1, 0], 'health': 5,
        'shocked': False, 'shock_time': 0, 'attack_time': 0}
]

# Game over flag
game_over = False
# To store the result ("Game Over" or "You Defeated the Zombies!")
game_result = None

# Fonts
font = pygame.font.SysFont(None, 24)

# Clock
clock = pygame.time.Clock()

# Zombie action timer
zombie_last_move_time = time.time()  # Initialize the zombie action timer


def draw_field():
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE,
                               CELL_SIZE, CELL_SIZE)
            if field[y][x] == 'material':
                pygame.draw.rect(SCREEN, BROWN, rect)
            elif field[y][x] == 'blue_ore':
                pygame.draw.rect(SCREEN, BLUE, rect)
            else:
                pygame.draw.rect(SCREEN, WHITE, rect)
            pygame.draw.rect(SCREEN, GRAY, rect, 1)  # Grid lines

    # Draw player
    rect = pygame.Rect(player_pos[0] * CELL_SIZE,
                       player_pos[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(SCREEN, GREEN, rect)

    # Draw zombies
    for zombie in zombies:
        if zombie['health'] > 0:
            x, y = zombie['pos']
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE,
                               CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(SCREEN, RED, rect)


def move_player(dx, dy):
    global player_blue_ore_inventory
    new_x = player_pos[0] + dx
    new_y = player_pos[1] + dy
    if (0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE) and \
            (field[new_y][new_x] == 'empty' or field[new_y][new_x] == 'blue_ore'):
        # Check for zombies at the new position
        if not any(zombie['pos'] == [new_x, new_y] and zombie['health'] > 0 for zombie in zombies):
            player_pos[0] = new_x
            player_pos[1] = new_y
            # Collect blue ore if present
            if field[new_y][new_x] == 'blue_ore':
                player_blue_ore_inventory += 1
                field[new_y][new_x] = 'empty'


def find_path(start, goal, field):
    visited = set()
    queue = deque()
    queue.append((start, []))  # (current_position, path)

    while queue:
        current_pos, path = queue.popleft()
        if current_pos == goal:
            return path  # Return the path to the goal

        x, y = current_pos
        if current_pos in visited:
            continue
        visited.add(current_pos)

        # Add neighboring positions (up/down/left/right) if they are empty and not player's position
        neighbors = [
            (x+1, y),
            (x-1, y),
            (x, y+1),
            (x, y-1)
        ]
        for nx, ny in neighbors:
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                # Check if position is empty and not player's position
                if [nx, ny] != player_pos and field[ny][nx] == 'empty':
                    if (nx, ny) not in visited:
                        queue.append(((nx, ny), path + [(nx, ny)]))
    # No path found
    return None


def move_zombies():
    for zombie in zombies:
        if zombie['health'] <= 0:
            continue
        if zombie['shocked']:
            continue

        x, y = zombie['pos']
        path = find_path((x, y), (player_pos[0], player_pos[1]), field)
        if path and len(path) > 0:
            next_pos = path[0]
            # Ensure zombie doesn't move onto player
            if next_pos != (player_pos[0], player_pos[1]):
                zombie['pos'][0], zombie['pos'][1] = next_pos
            else:
                # Zombie is adjacent to player, may attack
                pass
        else:
            # No path found, move randomly
            # up, down, left, right
            directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
            random.shuffle(directions)
            for dx, dy in directions:
                nx = x + dx
                ny = y + dy
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                    if field[ny][nx] == 'empty' and [nx, ny] != player_pos:
                        zombie['pos'][0] = nx
                        zombie['pos'][1] = ny
                        break  # Move made
            # If no move made, zombie stays in place


def mine_material_at(x, y):
    global player_inventory
    if field[y][x] == 'material':
        field[y][x] = 'empty'
        player_inventory += 1


def action_on_direction(direction):
    dx, dy = 0, 0
    if direction == 'up':
        dy = -1
    elif direction == 'down':
        dy = 1
    elif direction == 'left':
        dx = -1
    elif direction == 'right':
        dx = 1
    else:
        return

    target_x = player_pos[0] + dx
    target_y = player_pos[1] + dy
    if 0 <= target_x < GRID_SIZE and 0 <= target_y < GRID_SIZE:
        # First, check for zombie at target location
        for zombie in zombies:
            if zombie['health'] > 0 and zombie['pos'] == [target_x, target_y]:
                # Hit the zombie
                hit_zombie(zombie)
                return
        # If no zombie, try to mine material
        if field[target_y][target_x] == 'material':
            mine_material_at(target_x, target_y)


def place_material():
    global player_inventory
    if player_inventory > 0 and field[player_pos[1]][player_pos[0]] == 'empty':
        field[player_pos[1]][player_pos[0]] = 'material'
        player_inventory -= 1


def hit_zombie(zombie):
    zombie['health'] -= 1
    zombie['shocked'] = True
    zombie['shock_time'] = time.time()
    if zombie['health'] <= 0:
        # Zombie drops blue ore at its position
        x, y = zombie['pos']
        field[y][x] = 'blue_ore'


def zombie_attack():
    global player_health
    current_time = time.time()
    for zombie in zombies:
        if zombie['health'] <= 0:
            continue
        if zombie['shocked']:
            continue
        if current_time - zombie['attack_time'] < 0.5:
            continue  # Zombie is in attack cooldown
        x, y = zombie['pos']
        if abs(player_pos[0] - x) <= 1 and abs(player_pos[1] - y) <= 1:
            player_health -= 1
            zombie['attack_time'] = current_time


def show_stats():
    inventory_text = font.render(f'Inventory: {player_inventory}', True, BLACK)
    health_text = font.render(f'Health: {player_health}', True, BLACK)
    blue_ore_text = font.render(
        f'Blue Ore: {player_blue_ore_inventory}', True, BLACK)
    SCREEN.blit(inventory_text, (10, 10))
    SCREEN.blit(health_text, (10, 30))
    SCREEN.blit(blue_ore_text, (10, 50))


def check_game_over():
    if player_health <= 0:
        return "loss"
    elif all(zombie['health'] <= 0 for zombie in zombies):
        return "win"
    else:
        return None


# Game loop
while not game_over:
    SCREEN.fill(WHITE)
    draw_field()
    show_stats()

    current_time = time.time()

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Player input handling for moving one square per key press
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                move_player(-1, 0)
            elif event.key == pygame.K_RIGHT:
                move_player(1, 0)
            elif event.key == pygame.K_UP:
                move_player(0, -1)
            elif event.key == pygame.K_DOWN:
                move_player(0, 1)
            elif event.key == pygame.K_p:
                place_material()
            # Using 'w', 'a', 's', 'd' to mine or hit zombie
            elif event.key == pygame.K_w:
                action_on_direction('up')
            elif event.key == pygame.K_a:
                action_on_direction('left')
            elif event.key == pygame.K_s:
                action_on_direction('down')
            elif event.key == pygame.K_d:
                action_on_direction('right')

    # Update zombies' shocked status
    for zombie in zombies:
        if zombie['shocked'] and current_time - zombie['shock_time'] >= 0.5:
            zombie['shocked'] = False

    # Zombies take action every 0.5 seconds
    if current_time - zombie_last_move_time >= 0.5:
        # Update zombies
        move_zombies()
        zombie_attack()
        # Reset the timer
        zombie_last_move_time = current_time

    # Check game over condition
    result = check_game_over()
    if result == "loss":
        game_over = True
        game_result = "Game Over"
    elif result == "win":
        game_over = True
        game_result = "You Defeated the Zombies!"

    pygame.display.flip()
    clock.tick(60)  # Increased to 60 FPS for smoother player movement

# Game Over or Victory Screen
SCREEN.fill(WHITE)
end_text = font.render(game_result, True, BLACK)
text_rect = end_text.get_rect(center=(SCREEN_SIZE // 2, SCREEN_SIZE // 2))
SCREEN.blit(end_text, text_rect)
pygame.display.flip()
time.sleep(2)
pygame.quit()
