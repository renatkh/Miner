import pygame
import random
import sys
import time
from collections import deque  # For pathfinding

# Initialize Pygame
pygame.init()

# Constants
GRID_SIZE = 40
CELL_SIZE = 50  # Reduced cell size to fit on screen
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
PURPLE = (160, 32, 240)
AQUA = (0, 255, 255)
ORANGE = (255, 165, 0)
DARK_GREEN = (0, 128, 0)  # For green ore

# Fonts
font = pygame.font.SysFont(None, 18)

# Clock
clock = pygame.time.Clock()


def main():
    level = 1
    player_blue_ore_inventory = 0
    player_green_ore_inventory = 0
    player_health = 5
    player_inventory = 0
    total_zombies_defeated = 0

    while True:
        # Initialize level
        run_level(level, player_inventory, player_blue_ore_inventory,
                  player_green_ore_inventory, player_health, total_zombies_defeated)
        # After level is complete
        level += 1
        player_blue_ore_inventory = 0
        player_green_ore_inventory = 0
        player_health = 5
        player_inventory = 0


def run_level(level, player_inventory, player_blue_ore_inventory, player_green_ore_inventory, player_health, total_zombies_defeated):
    # Game field
    field = [['empty' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

    # Player attributes
    player_pos = [0, 0]
    player_inventory = player_inventory
    player_blue_ore_inventory = player_blue_ore_inventory
    player_green_ore_inventory = player_green_ore_inventory
    player_health = player_health

    # Player facing direction ('up', 'down', 'left', 'right')
    player_facing = 'down'  # Default facing direction

    # Number of zombies
    NUM_ZOMBIES = 5 + (level - 1)

    # Zombie action timer
    zombie_last_move_time = time.time()  # Initialize the zombie action timer

    # Water and Lava Placement
    def place_water(x, y, max_cells):
        if field[y][x] == 'empty':
            field[y][x] = 'water'
            # Spread water to adjacent empty cells
            spread_water(x, y, max_cells)

    def spread_water(x, y, max_cells):
        queue = deque()
        queue.append((x, y))
        visited = set()
        visited.add((x, y))
        while queue and len(visited) < max_cells:
            cx, cy = queue.popleft()
            neighbors = [
                (cx+1, cy),
                (cx-1, cy),
                (cx, cy+1),
                (cx, cy-1)
            ]
            random.shuffle(neighbors)  # Randomize spread
            for nx, ny in neighbors:
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                    if (nx, ny) not in visited:
                        if field[ny][nx] == 'empty':
                            field[ny][nx] = 'water'
                            queue.append((nx, ny))
                            visited.add((nx, ny))
                        # Water and Lava Interaction
                        elif field[ny][nx] == 'lava':
                            field[ny][nx] = 'obsidian'
                            visited.add((nx, ny))  # Prevent reprocessing

    def place_lava(x, y, max_cells):
        if field[y][x] == 'empty':
            field[y][x] = 'lava'
            # Spread lava to adjacent empty cells
            spread_lava(x, y, max_cells)

    def spread_lava(x, y, max_cells):
        queue = deque()
        queue.append((x, y))
        visited = set()
        visited.add((x, y))
        while queue and len(visited) < max_cells:
            cx, cy = queue.popleft()
            neighbors = [
                (cx+1, cy),
                (cx-1, cy),
                (cx, cy+1),
                (cx, cy-1)
            ]
            random.shuffle(neighbors)  # Randomize spread
            for nx, ny in neighbors:
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                    if (nx, ny) not in visited:
                        if field[ny][nx] == 'empty':
                            field[ny][nx] = 'lava'
                            queue.append((nx, ny))
                            visited.add((nx, ny))
                        # Lava and Water Interaction
                        elif field[ny][nx] == 'water':
                            # Current lava turns to obsidian
                            field[cx][cy] = 'obsidian'
                            break  # Stop spreading this lava path

    # Place water and lava pools before filling materials
    # Place a water pool (starting point), limit the spread to 50 cells
    water_start_x = random.randint(5, 10)
    water_start_y = random.randint(5, 10)
    place_water(water_start_x, water_start_y, max_cells=50)

    # Place a lava pool (starting point), limit the spread to 30 cells
    lava_start_x = random.randint(25, 30)
    lava_start_y = random.randint(25, 30)
    place_lava(lava_start_x, lava_start_y, max_cells=30)

    # Now fill the remaining empty spaces with materials (95% fill)
    total_cells = GRID_SIZE * GRID_SIZE
    material_target = int(total_cells * 0.95)
    material_count = 0
    attempts = 0
    max_attempts = total_cells * 2  # Prevent infinite loop

    while material_count < material_target and attempts < max_attempts:
        x = random.randint(0, GRID_SIZE - 1)
        y = random.randint(0, GRID_SIZE - 1)
        if field[y][x] == 'empty' and [x, y] != player_pos and field[y][x] not in ('water', 'lava', 'obsidian'):
            field[y][x] = 'material'
            material_count += 1
        attempts += 1

    # Now place zombies in empty spaces
    def is_adjacent(pos1, pos2):
        return abs(pos1[0] - pos2[0]) <= 1 and abs(pos1[1] - pos2[1]) <= 1

    zombies = []
    zombie_positions = []
    for _ in range(NUM_ZOMBIES):
        while True:
            x = random.randint(0, GRID_SIZE - 1)
            y = random.randint(0, GRID_SIZE - 1)
            if field[y][x] == 'empty' and not is_adjacent([x, y], player_pos):
                zombies.append({'pos': [x, y], 'health': 5,
                                'shocked': False, 'shock_time': 0, 'attack_time': 0, 'starred': False})
                zombie_positions.append([x, y])
                break

    # Place 2 green ores not adjacent to zombies
    green_ore_count = 0
    attempts = 0
    max_attempts = total_cells * 2  # Prevent infinite loop
    while green_ore_count < 2 and attempts < max_attempts:
        x = random.randint(0, GRID_SIZE - 1)
        y = random.randint(0, GRID_SIZE - 1)
        if field[y][x] == 'empty':
            adjacent_to_zombie = False
            for zombie in zombies:
                zx, zy = zombie['pos']
                if abs(zx - x) <= 1 and abs(zy - y) <= 1:
                    adjacent_to_zombie = True
                    break
            if not adjacent_to_zombie:
                field[y][x] = 'green_ore'
                green_ore_count += 1
        attempts += 1

    # Randomly select one zombie to be starred (but do not show it)
    if zombies:
        starred_zombie = random.choice(zombies)
        starred_zombie['starred'] = True

    # Game over flag
    game_over = False
    level_complete = False
    game_result = None  # To store the result ("Game Over" or "You Win!")

    # Function to check if player steps on obsidian with 2 blue ores (win condition)
    def check_victory():
        if field[player_pos[1]][player_pos[0]] == 'obsidian' and player_blue_ore_inventory >= 2:
            return True
        return False

    def draw_field():
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE,
                                   CELL_SIZE, CELL_SIZE)

                cell_type = field[y][x]
                if cell_type == 'material':
                    pygame.draw.rect(SCREEN, BROWN, rect)
                elif cell_type == 'blue_ore':
                    pygame.draw.rect(SCREEN, BLUE, rect)
                elif cell_type == 'double_blue_ore':
                    pygame.draw.rect(SCREEN, BLUE, rect)
                    # Draw '2' on top
                    text_surface = font.render('2', True, BLACK)
                    text_rect = text_surface.get_rect(center=rect.center)
                    SCREEN.blit(text_surface, text_rect)
                elif cell_type == 'green_ore':
                    pygame.draw.rect(SCREEN, DARK_GREEN, rect)
                elif cell_type == 'water':
                    pygame.draw.rect(SCREEN, AQUA, rect)
                elif cell_type == 'lava':
                    pygame.draw.rect(SCREEN, ORANGE, rect)
                elif cell_type == 'obsidian':
                    pygame.draw.rect(SCREEN, PURPLE, rect)
                else:
                    pygame.draw.rect(SCREEN, WHITE, rect)
                pygame.draw.rect(SCREEN, GRAY, rect, 1)  # Grid lines

        # Draw player
        rect = pygame.Rect(player_pos[0] * CELL_SIZE,
                           player_pos[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(SCREEN, GREEN, rect)

        # Draw player facing direction (a small line indicating direction)
        center_x = player_pos[0] * CELL_SIZE + CELL_SIZE // 2
        center_y = player_pos[1] * CELL_SIZE + CELL_SIZE // 2
        if player_facing == 'up':
            pygame.draw.line(SCREEN, BLACK, (center_x, center_y),
                             (center_x, center_y - CELL_SIZE // 2), 2)
        elif player_facing == 'down':
            pygame.draw.line(SCREEN, BLACK, (center_x, center_y),
                             (center_x, center_y + CELL_SIZE // 2), 2)
        elif player_facing == 'left':
            pygame.draw.line(SCREEN, BLACK, (center_x, center_y),
                             (center_x - CELL_SIZE // 2, center_y), 2)
        elif player_facing == 'right':
            pygame.draw.line(SCREEN, BLACK, (center_x, center_y),
                             (center_x + CELL_SIZE // 2, center_y), 2)

        # Draw zombies (all look the same)
        for zombie in zombies:
            if zombie['health'] > 0:
                x, y = zombie['pos']
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE,
                                   CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(SCREEN, RED, rect)

    def move_player(dx, dy):
        nonlocal player_blue_ore_inventory, player_green_ore_inventory, player_health, game_over, game_result, level_complete, player_facing
        new_x = player_pos[0] + dx
        new_y = player_pos[1] + dy
        if (0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE):
            target_cell = field[new_y][new_x]
            # Update facing direction
            if dx == -1:
                player_facing = 'left'
            elif dx == 1:
                player_facing = 'right'
            elif dy == -1:
                player_facing = 'up'
            elif dy == 1:
                player_facing = 'down'

            # Check for zombies at the new position
            if any(zombie['pos'] == [new_x, new_y] and zombie['health'] > 0 for zombie in zombies):
                return  # Can't move into a zombie
            elif target_cell == 'material':
                return  # Can't move into a material
            elif target_cell == 'lava':
                player_health = 0  # Player dies immediately
                player_pos[0] = new_x
                player_pos[1] = new_y
                game_over = True
                game_result = "Game Over! You stepped into lava."
            elif target_cell == 'obsidian':
                player_pos[0] = new_x
                player_pos[1] = new_y
                # Check victory condition
                if player_blue_ore_inventory >= 2:
                    level_complete = True
                    game_result = "Level Complete!"
            elif target_cell == 'water':
                player_pos[0] = new_x
                player_pos[1] = new_y
                # The player can move into water
            else:
                player_pos[0] = new_x
                player_pos[1] = new_y
                # Collect blue ore if present
                if target_cell == 'blue_ore':
                    player_blue_ore_inventory += 1
                    field[new_y][new_x] = 'empty'
                elif target_cell == 'double_blue_ore':
                    player_blue_ore_inventory += 2
                    field[new_y][new_x] = 'empty'
                # Collect green ore if present
                if target_cell == 'green_ore':
                    player_green_ore_inventory += 1
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

            # Add neighboring positions (up/down/left/right) if they are walkable and not player's position
            neighbors = [
                (x+1, y),
                (x-1, y),
                (x, y+1),
                (x, y-1)
            ]
            random.shuffle(neighbors)
            for nx, ny in neighbors:
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                    # Check if position is walkable and not player's position
                    if ([nx, ny] != player_pos and
                            field[ny][nx] in ('empty', 'blue_ore', 'double_blue_ore', 'obsidian', 'water', 'green_ore')):
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
                    # Check if zombie steps into lava
                    if field[zombie['pos'][1]][zombie['pos'][0]] == 'lava':
                        zombie['health'] = 0  # Zombie dies
                    # Check if zombie steps onto green ore
                    elif field[zombie['pos'][1]][zombie['pos'][0]] == 'green_ore':
                        field[zombie['pos'][1]][zombie['pos'][0]] = 'blue_ore'
                else:
                    # Zombie is adjacent to player, may attack
                    pass
            else:
                # No path found, move randomly
                directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
                random.shuffle(directions)
                for dx, dy in directions:
                    nx = x + dx
                    ny = y + dy
                    if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                        if field[ny][nx] in ('empty', 'blue_ore', 'double_blue_ore', 'obsidian', 'water', 'green_ore') and [nx, ny] != player_pos:
                            zombie['pos'][0] = nx
                            zombie['pos'][1] = ny
                            # Check if zombie steps into lava
                            if field[ny][nx] == 'lava':
                                zombie['health'] = 0  # Zombie dies
                            # Check if zombie steps onto green ore
                            elif field[ny][nx] == 'green_ore':
                                field[ny][nx] = 'blue_ore'
                            break  # Move made
                # If no move made, zombie stays in place

    def mine_material_at(x, y):
        nonlocal player_inventory
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
        nonlocal player_inventory
        if player_inventory > 0 and field[player_pos[1]][player_pos[0]] == 'empty':
            field[player_pos[1]][player_pos[0]] = 'material'
            player_inventory -= 1

    def place_green_ore_in_front():
        nonlocal player_green_ore_inventory
        if player_green_ore_inventory > 0:
            # Determine the position in front of the player based on facing direction
            dx, dy = 0, 0
            if player_facing == 'up':
                dy = -1
            elif player_facing == 'down':
                dy = 1
            elif player_facing == 'left':
                dx = -1
            elif player_facing == 'right':
                dx = 1

            target_x = player_pos[0] + dx
            target_y = player_pos[1] + dy

            if 0 <= target_x < GRID_SIZE and 0 <= target_y < GRID_SIZE:
                if field[target_y][target_x] == 'empty':
                    field[target_y][target_x] = 'green_ore'
                    player_green_ore_inventory -= 1

    def hit_zombie(zombie):
        nonlocal total_zombies_defeated
        zombie['health'] -= 1
        zombie['shocked'] = True
        zombie['shock_time'] = time.time()
        if zombie['health'] <= 0:
            # Zombie drops blue ore at its position
            x, y = zombie['pos']
            if zombie.get('starred', False):
                field[y][x] = 'double_blue_ore'
            else:
                field[y][x] = 'blue_ore'
            total_zombies_defeated += 1

    def zombie_attack():
        nonlocal player_health, game_over, game_result
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
                if player_health <= 0:
                    game_over = True
                    game_result = "Game Over! You were killed by a zombie."

        # Update zombies' shocked status
        current_time = time.time()
        for zombie in zombies:
            if zombie['shocked'] and current_time - zombie['shock_time'] >= 0.5:
                zombie['shocked'] = False

    def show_stats():
        level_text = font.render(f'Level: {level}', True, BLACK)
        inventory_text = font.render(
            f'Inventory: {player_inventory}', True, BLACK)
        health_text = font.render(f'Health: {player_health}', True, BLACK)
        blue_ore_text = font.render(
            f'Blue Ore: {player_blue_ore_inventory}', True, BLACK)
        green_ore_text = font.render(
            f'Green Ore: {player_green_ore_inventory}', True, BLACK)
        SCREEN.blit(level_text, (10, 10))
        SCREEN.blit(inventory_text, (10, 30))
        SCREEN.blit(health_text, (10, 50))
        SCREEN.blit(blue_ore_text, (10, 70))
        SCREEN.blit(green_ore_text, (10, 90))

    # Game loop
    while not game_over and not level_complete:
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
                elif event.key == pygame.K_RETURN:  # Enter key to place green ore in front
                    place_green_ore_in_front()
                # Using 'w', 'a', 's', 'd' to mine or hit zombie
                elif event.key == pygame.K_w:
                    action_on_direction('up')
                elif event.key == pygame.K_a:
                    action_on_direction('left')
                elif event.key == pygame.K_s:
                    action_on_direction('down')
                elif event.key == pygame.K_d:
                    action_on_direction('right')

        # Zombies take action every 0.5 seconds
        if current_time - zombie_last_move_time >= 0.5:
            # Update zombies
            move_zombies()
            zombie_attack()
            # Reset the timer
            zombie_last_move_time = current_time

        # Water spreading logic
        water_spread_positions = []
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if field[y][x] == 'water':
                    neighbors = [
                        (x+1, y),
                        (x-1, y),
                        (x, y+1),
                        (x, y-1)
                    ]
                    for nx, ny in neighbors:
                        if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                            if field[ny][nx] == 'empty':
                                field[ny][nx] = 'water'
                                water_spread_positions.append((nx, ny))
                            elif field[ny][nx] == 'lava':
                                field[ny][nx] = 'obsidian'

        pygame.display.flip()
        clock.tick(60)  # 60 FPS for smoother player movement

    # Level Complete or Game Over
    SCREEN.fill(WHITE)
    end_text = font.render(game_result, True, BLACK)
    text_rect = end_text.get_rect(center=(SCREEN_SIZE // 2, SCREEN_SIZE // 2))
    SCREEN.blit(end_text, text_rect)
    pygame.display.flip()
    time.sleep(2)
    if game_over:
        pygame.quit()
        sys.exit()
    else:
        return


if __name__ == "__main__":
    main()
