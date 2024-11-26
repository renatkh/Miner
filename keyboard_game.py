import pygame  
import random  
import sys  
import math  
from itertools import product  
  
# Initialize Pygame  
pygame.init()  
  
# Set up display  
WIDTH, HEIGHT = 800, 600  
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))  
pygame.display.set_caption("Mob Defeat Game")  
  
# Fonts  
FONT = pygame.font.SysFont('Arial', 24)  
FONT_SMALL = pygame.font.SysFont('Arial', 20)  
  
# Colors  
BACKGROUND_COLOR = (30, 30, 30)  # Dark gray  
TEXT_COLOR = (255, 255, 255)     # White  
HEART_COLOR = (255, 0, 0)        # Red  
SUPER_MOB_COLOR = (255, 215, 0)  # Gold color for super charged mob  
  
# Game settings  
MOB_SIZE = 60  # Width and height of mob square  
STARTING_HEARTS = 5  
NEW_MOB_INTERVAL = 3000   # New mob every 3 seconds (milliseconds)  
MOB_TIME_LIMIT = 5000     # 5 seconds to defeat a mob (milliseconds)  
POINTS_PER_MOB = 5  
POINTS_PER_SUPER_MOB = 10  
COMBO_THRESHOLD = 10      # Increase difficulty after 10 consecutive hits  
  
# Super Charged Mob settings  
SUPER_MOB_MIN_INTERVAL = 10000  # At least 10 seconds between super mobs (milliseconds)  
LAST_SUPER_MOB_TIME = -SUPER_MOB_MIN_INTERVAL  # Initialize to allow the first mob to appear  
SUPER_MOB_PROBABILITY = 0.2     # 20% chance to spawn a super mob when eligible  
  
# Difficulty levels  
DIFFICULTY_LEVELS = [  
    list("ASDFGHJKLQWERTYUIOPZXCVBNM"),                                           # Level 1: Letters  
    list("ASDFGHJKLQWERTYUIOPZXCVBNM") + list("1234567890"),                      # Level 2: Letters + Numbers  
    list("ASDFGHJKLQWERTYUIOPZXCVBNM") + list("1234567890!@#$%^&*()"),            # Level 3: Letters + Numbers + Symbols  
    [''.join(p) for p in product("ASDFGHJKLQWERTYUIOPZXCVBNM", repeat=2)],        # Level 4: 2-letter combinations  
    [''.join(p) for p in product("ASDFGHJKLQWERTYUIOPZXCVBNM1234567890", repeat=3)], # Level 5: 3-character combinations  
]  
  
# List of two-letter words for super mobs  
TWO_LETTER_WORDS = ['OF', 'TO', 'IN', 'IT', 'IS', 'BE', 'AS', 'AT', 'SO', 'WE',  
                    'HE', 'BY', 'OR', 'ON', 'DO', 'IF', 'ME', 'UP', 'MY', 'GO',  
                    'NO', 'US', 'AM']  
  
# Player class  
class Player:  
    def __init__(self):  
        self.points = 0  
        self.hearts = STARTING_HEARTS  
        self.combo = 0  
        self.difficulty_level = 0  
  
# Mob class  
class Mob:  
    def __init__(self, x, y, key, spawn_time, time_limit, super_mob=False):  
        self.x = x  
        self.y = y  
        self.key = key  
        self.spawn_time = spawn_time  
        self.time_limit = time_limit  
        self.defeated = False  
        self.super_mob = super_mob  
        self.angle = 0  # For animation  
        self.rect = pygame.Rect(self.x, self.y, MOB_SIZE, MOB_SIZE)  
        if self.super_mob:  
            self.color = SUPER_MOB_COLOR  # Gold color for super charged mob  
        else:  
            self.color = [random.randint(50, 255) for _ in range(3)]  
  
    def update(self, current_time):  
        # Update the angle for animation  
        self.angle = (self.angle + 5) % 360  
        # Check if mob's time has expired  
        elapsed_time = current_time - self.spawn_time  
        if elapsed_time >= self.time_limit:  
            return False  # Mob's time expired  
        return True  
  
    def draw(self, surface, current_time):  
        if not self.defeated:  
            # Draw the mob  
            pygame.draw.rect(surface, self.color, self.rect)  
  
            # Draw swirling lines around super mobs  
            if self.super_mob:  
                self.draw_swirl(surface)  
  
            # Render the key above the mob  
            key_text = FONT.render(self.key, True, TEXT_COLOR)  
            key_text_rect = key_text.get_rect(center=(self.x + MOB_SIZE / 2, self.y - 30))  
            surface.blit(key_text, key_text_rect)  
            # Render the timer below the mob  
            elapsed_time = current_time - self.spawn_time  
            time_remaining = max(0, (self.time_limit - elapsed_time) // 1000 + 1)  
            timer_text = FONT_SMALL.render(f"{time_remaining}", True, HEART_COLOR)  
            timer_text_rect = timer_text.get_rect(center=(self.x + MOB_SIZE / 2, self.y + MOB_SIZE + 15))  
            surface.blit(timer_text, timer_text_rect)  
  
    def draw_swirl(self, surface):  
        # Draw white swirling lines around the mob  
        center_x = self.x + MOB_SIZE / 2  
        center_y = self.y + MOB_SIZE / 2  
        num_lines = 12  # Number of lines in the swirl  
        radius = MOB_SIZE  # Radius of the swirl  
  
        for i in range(num_lines):  
            angle_deg = self.angle + (360 / num_lines) * i  
            angle_rad = math.radians(angle_deg)  
            end_x = center_x + radius * math.cos(angle_rad)  
            end_y = center_y + radius * math.sin(angle_rad)  
            pygame.draw.line(surface, TEXT_COLOR, (center_x, center_y), (end_x, end_y), 2)  
  
def create_mob(difficulty_level, spawn_time, current_time):  
    global LAST_SUPER_MOB_TIME  
    x = random.randint(50, WIDTH - MOB_SIZE - 50)  
    y = random.randint(100, HEIGHT - MOB_SIZE - 100)  
  
    # Check if we can spawn a super charged mob  
    time_since_last_super = current_time - LAST_SUPER_MOB_TIME  
    if time_since_last_super >= SUPER_MOB_MIN_INTERVAL and random.random() < SUPER_MOB_PROBABILITY:  
        # Create a super charged mob  
        key = random.choice(TWO_LETTER_WORDS)  
        mob = Mob(x, y, key, spawn_time, MOB_TIME_LIMIT, super_mob=True)  
        LAST_SUPER_MOB_TIME = current_time  
    else:  
        # Create a regular mob  
        key_list = DIFFICULTY_LEVELS[min(difficulty_level, len(DIFFICULTY_LEVELS)-1)]  
        key = random.choice(key_list)  
        mob = Mob(x, y, key, spawn_time, MOB_TIME_LIMIT)  
    return mob  
  
def draw_hearts(surface, hearts):  
    # Simple representation of hearts as text  
    heart_text = FONT.render(f"Hearts: {hearts}", True, HEART_COLOR)  
    heart_rect = heart_text.get_rect(topright=(WIDTH - 20, 20))  
    surface.blit(heart_text, heart_rect)  
  
def draw_points(surface, points):  
    points_text = FONT.render(f"Points: {points}", True, TEXT_COLOR)  
    points_rect = points_text.get_rect(topleft=(20, 20))  
    surface.blit(points_text, points_rect)  
  
def main():  
    clock = pygame.time.Clock()  
    player = Player()  
    mobs = []  
    last_mob_spawn_time = pygame.time.get_ticks()  
    running = True  
  
    while running:  
        current_time = pygame.time.get_ticks()  
        WINDOW.fill(BACKGROUND_COLOR)  
  
        for event in pygame.event.get():  
            if event.type == pygame.QUIT:  
                running = False  
  
            if event.type == pygame.KEYDOWN:  
                key_pressed = pygame.key.name(event.key).upper()  
                mob_defeated = False  
                # Collect the keys pressed (for multi-character keys)  
                if len(key_pressed) == 1:  
                    for mob in mobs:  
                        if not mob.defeated and mob.key.startswith(key_pressed):  
                            if len(mob.key) > 1:  
                                # Wait for the next key  
                                mob.key = mob.key[1:]  
                            else:  
                                # Last character matched  
                                mob.defeated = True  
                                mob_defeated = True  
                                if mob.super_mob:  
                                    player.points += POINTS_PER_SUPER_MOB  
                                else:  
                                    player.points += POINTS_PER_MOB  
                                player.combo += 1  
                                if player.combo % COMBO_THRESHOLD == 0:  
                                    player.difficulty_level += 1  # Increase difficulty  
                                break  # Defeat only one mob per key press  
  
                if not mob_defeated:  
                    player.combo = 0  # Reset combo if wrong key  
  
        # Spawn new mobs every 3 seconds  
        if current_time - last_mob_spawn_time >= NEW_MOB_INTERVAL:  
            new_mob = create_mob(player.difficulty_level, current_time, current_time)  
            mobs.append(new_mob)  
            last_mob_spawn_time = current_time  
  
        # Update and draw mobs  
        mobs_to_remove = []  
        for mob in mobs:  
            if not mob.defeated:  
                if not mob.update(current_time):  
                    # Mob's time expired  
                    mob.defeated = True  
                    player.hearts -= 1  
                    player.combo = 0  # Reset combo  
                    if player.hearts <= 0:  
                        running = False  # Game over  
                        break  
                else:  
                    mob.draw(WINDOW, current_time)  
            else:  
                mobs_to_remove.append(mob)  # Remove defeated mobs  
  
        # Remove defeated mobs from the list  
        for mob in mobs_to_remove:  
            mobs.remove(mob)  
  
        # Draw points and hearts  
        draw_points(WINDOW, player.points)  
        draw_hearts(WINDOW, player.hearts)  
  
        pygame.display.flip()  
        clock.tick(60)  # Limit to 60 FPS  
  
    # Game Over Screen  
    WINDOW.fill(BACKGROUND_COLOR)  
    game_over_text = FONT.render("Game Over!", True, TEXT_COLOR)  
    final_score_text = FONT.render(f"Final Score: {player.points}", True, TEXT_COLOR)  
    game_over_rect = game_over_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 30))  
    final_score_rect = final_score_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 10))  
    WINDOW.blit(game_over_text, game_over_rect)  
    WINDOW.blit(final_score_text, final_score_rect)  
    pygame.display.flip()  
    pygame.time.wait(5000)  # Display for 5 seconds before closing  
  
    pygame.quit()  
    sys.exit()  
  
if __name__ == '__main__':  
    main()  