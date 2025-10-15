# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import digitalio
import board
<<<<<<< HEAD
from PIL import Image
=======
from PIL import Image, ImageDraw, ImageFont # Use Pillow for image manipulation
>>>>>>> a2716e4 (geogame)
import pygame
import random
import busio
import sys
import time
<<<<<<< HEAD
import os
=======
>>>>>>> a2716e4 (geogame)

# --- Attempt to import all hardware libraries ---
try:
    import qwiic_joystick
    joystick_connected = True
except (ImportError, ModuleNotFoundError):
    joystick_connected = False

try:
    from adafruit_seesaw.seesaw import Seesaw
    from adafruit_seesaw.rotaryio import IncrementalEncoder
    encoder_connected = True
except (ImportError, ModuleNotFoundError):
    encoder_connected = False

<<<<<<< HEAD
import adafruit_rgb_display.st7789 as st7789
=======
# --- MODIFIED: Import new display driver ---
from adafruit_ssd1305 import SSD1305_SPI
>>>>>>> a2716e4 (geogame)

# --- Hardware Setup ---
i2c = busio.I2C(board.SCL, board.SDA)

# Joystick Setup
if joystick_connected:
    myJoystick = qwiic_joystick.QwiicJoystick(i2c)
    if not myJoystick.connected:
        print("Joystick not connected, falling back to keyboard.", file=sys.stderr)
        joystick_connected = False
    else:
        myJoystick.begin()
        print(f"Joystick Initialized. Firmware: {myJoystick.version}")

# Rotary Encoder Setup
if encoder_connected:
    try:
        seesaw = Seesaw(i2c, addr=0x36)
        seesaw.pin_mode(24, seesaw.INPUT_PULLUP)
        encoder = IncrementalEncoder(seesaw)
        last_encoder_pos = encoder.position
    except ValueError:
        print("Rotary Encoder not found. Use L/R Arrow Keys in menu.", file=sys.stderr)
        encoder_connected = False

<<<<<<< HEAD
# Display Setup
cs_pin = digitalio.DigitalInOut(board.D5)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D24)
BAUDRATE = 24000000
spi = board.SPI()
disp = st7789.ST7789(
    spi, cs=cs_pin, dc=dc_pin, rst=reset_pin, baudrate=BAUDRATE,
    width=135, height=240, x_offset=53, y_offset=40,
)
disp.rotation = 90
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

# --- Global Pygame & Game Setup ---
SCREEN_WIDTH, SCREEN_HEIGHT = 240, 135
pygame.init()
screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
WHITE, BLACK, GREEN = (255, 255, 255), (0, 0, 0), (0, 255, 0)
font = pygame.font.Font(None, 24)
title_font = pygame.font.Font(None, 40)
clock = pygame.time.Clock()
FPS = 30

# --- Load Player Image (Robustly) ---
script_dir = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(script_dir, "lunavator.png")
try:
    player_image_original = pygame.image.load(image_path).convert_alpha()
    use_player_image = True
except pygame.error as e:
    print(f"Could not load lunavator.png from '{image_path}': {e}", file=sys.stderr)
    print("Using black squares for player. The image file might be corrupt.", file=sys.stderr)
    use_player_image = False

# ##########################################################################
# DINO GAME CODE
# ##########################################################################

DINO_GROUND_LEVEL = SCREEN_HEIGHT - 25
=======
# --- MODIFIED: Display Setup for Waveshare 128x32 OLED ---
spi = board.SPI()
cs_pin = digitalio.DigitalInOut(board.D17)
dc_pin = digitalio.DigitalInOut(board.D24)
reset_pin = digitalio.DigitalInOut(board.D25)
disp = SSD1305_SPI(128, 32, spi, dc_pin, reset_pin, cs_pin)

# Clear display.
disp.fill(0)
disp.show()

# --- MODIFIED: Global Pygame & Game Setup for new resolution ---
SCREEN_WIDTH, SCREEN_HEIGHT = 128, 32
pygame.init()
screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
WHITE, BLACK, GREEN = (255, 255, 255), (0, 0, 0), (0, 255, 0)
# Use smaller fonts for the tiny screen
font = pygame.font.Font(None, 12)
title_font = pygame.font.Font(None, 16)
clock = pygame.time.Clock()
FPS = 30

# --- NEW: Function to update the monochrome display ---
def update_display(pygame_surface):
    """Converts a Pygame surface to a 1-bit PIL Image and displays it."""
    # Convert pygame surface to a PIL image
    pil_string_image = pygame.image.tostring(pygame_surface, "RGB")
    pil_image = Image.frombytes("RGB", pygame_surface.get_size(), pil_string_image)

    # Convert the PIL image to black and white
    mono_image = pil_image.convert("1")

    # Display the monochrome image
    disp.image(mono_image)
    disp.show()


# ##########################################################################
# DINO GAME CODE (Rescaled for 128x32)
# ##########################################################################

DINO_GROUND_LEVEL = SCREEN_HEIGHT - 5
>>>>>>> a2716e4 (geogame)

class DinoPlayer(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
<<<<<<< HEAD
        self.normal_height = 25
        self.duck_height = 12
        
        if use_player_image:
            self.image_normal = pygame.transform.scale(player_image_original, (20, self.normal_height))
            self.image_duck = pygame.transform.scale(player_image_original, (20, self.duck_height))
            self.image = self.image_normal
        else:
            self.image = pygame.Surface([20, self.normal_height])
            self.image.fill(BLACK)

        self.rect = self.image.get_rect(bottomleft=(20, DINO_GROUND_LEVEL))
        self.velocity_y = 0
        self.gravity = 0.8
=======
        self.normal_height = 10
        self.duck_height = 5
        self.sprite_width = 8

        self.image = pygame.transform.scale(player_sprite_raw, (self.sprite_width, self.normal_height))
        self.rect = self.image.get_rect(bottomleft=(10, DINO_GROUND_LEVEL))
        
        self.velocity_y = 0
        self.gravity = 0.4  # Scaled down gravity
        self.jump_strength = -5 # Scaled down jump
>>>>>>> a2716e4 (geogame)
        self.is_jumping = False
        self.is_ducking = False

    def update(self):
        if self.is_jumping:
            self.velocity_y += self.gravity
            self.rect.y += self.velocity_y
        if self.rect.bottom >= DINO_GROUND_LEVEL:
            self.rect.bottom = DINO_GROUND_LEVEL
            self.is_jumping = False
            self.velocity_y = 0

    def jump(self):
        if not self.is_jumping and not self.is_ducking:
            self.is_jumping = True
<<<<<<< HEAD
            self.velocity_y = -10
=======
            self.velocity_y = self.jump_strength
>>>>>>> a2716e4 (geogame)

    def duck(self, is_pressed):
        if self.is_jumping: return
        
<<<<<<< HEAD
        # *** BUG FIX: Save midbottom to prevent horizontal skipping ***
        current_midbottom = self.rect.midbottom
        
        if is_pressed and not self.is_ducking:
            self.is_ducking = True
            if use_player_image:
                self.image = self.image_duck
            else:
                self.image = pygame.Surface([20, self.duck_height])
                self.image.fill(BLACK)
            self.rect = self.image.get_rect(midbottom=current_midbottom)

        elif not is_pressed and self.is_ducking:
            self.is_ducking = False
            if use_player_image:
                self.image = self.image_normal
            else:
                self.image = pygame.Surface([20, self.normal_height])
                self.image.fill(BLACK)
            self.rect = self.image.get_rect(midbottom=current_midbottom)
=======
        current_bottom = self.rect.bottom
        if is_pressed and not self.is_ducking:
            self.is_ducking = True
            self.image = pygame.transform.scale(player_sprite_raw, (self.sprite_width, self.duck_height))
            self.rect = self.image.get_rect(bottomleft=(10, current_bottom))

        elif not is_pressed and self.is_ducking:
            self.is_ducking = False
            self.image = pygame.transform.scale(player_sprite_raw, (self.sprite_width, self.normal_height))
            self.rect = self.image.get_rect(bottomleft=(10, current_bottom))
>>>>>>> a2716e4 (geogame)

class DinoObstacle(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
<<<<<<< HEAD
        if random.choice([True, False]):
            self.image = pygame.Surface([10, 25])
            self.rect = self.image.get_rect(bottomleft=(SCREEN_WIDTH, DINO_GROUND_LEVEL))
        else:
            self.image = pygame.Surface([15, 15])
            self.rect = self.image.get_rect(bottomleft=(SCREEN_WIDTH, DINO_GROUND_LEVEL - 20))
=======
        # Scaled down obstacles
        if random.choice([True, False]):
            self.image = pygame.Surface([5, 10])
            self.rect = self.image.get_rect(bottomleft=(SCREEN_WIDTH, DINO_GROUND_LEVEL))
        else:
            self.image = pygame.Surface([8, 8])
            self.rect = self.image.get_rect(bottomleft=(SCREEN_WIDTH, DINO_GROUND_LEVEL - 8))
>>>>>>> a2716e4 (geogame)
        self.image.fill(BLACK)
        self.speed = speed

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()

def dino_game_loop():
    player = DinoPlayer()
    obstacles = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group(player)
    game_over = False
<<<<<<< HEAD
    score, game_speed = 0, 5
    obstacle_timer = pygame.USEREVENT + 1
    pygame.time.set_timer(obstacle_timer, 2000)

    while True:
        if encoder_connected and not seesaw.digital_read(24):
            time.sleep(0.1) # Debounce
            return "MENU"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            if not game_over and event.type == obstacle_timer:
                new_obstacle = DinoObstacle(game_speed)
                obstacles.add(new_obstacle)
                all_sprites.add(new_obstacle)

        if game_over:
            if (joystick_connected and myJoystick.button == 0):
                return "MENU" 
        else:
            if joystick_connected:
                y = myJoystick.vertical
                # *** CONTROLS FLIPPED ***
                if y < 300: player.jump()   # Down on stick to jump
                player.duck(y > 700)        # Up on stick to duck
=======
    score, game_speed = 0, 4
    obstacle_timer = pygame.USEREVENT + 1
    pygame.time.set_timer(obstacle_timer, 2500)

    while True:
        if encoder_connected and not seesaw.digital_read(24):
            time.sleep(0.1); return "MENU"

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT"
            if not game_over and event.type == obstacle_timer:
                obstacles.add(DinoObstacle(game_speed))
                all_sprites.add(obstacles)

        if game_over:
            if joystick_connected and myJoystick.button == 0: return "MENU"
        else:
            if joystick_connected:
                y = myJoystick.vertical
                if y > 700: player.jump()
                player.duck(y < 300)
>>>>>>> a2716e4 (geogame)
            else:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_UP]: player.jump()
                player.duck(keys[pygame.K_DOWN])

            all_sprites.update()
            score += 1
<<<<<<< HEAD
            if pygame.sprite.spritecollide(player, obstacles, False):
                game_over = True
            if score % 200 == 0:
                game_speed = min(12, game_speed + 1)
=======
            if pygame.sprite.spritecollide(player, obstacles, False): game_over = True
            if score % 200 == 0: game_speed = min(8, game_speed + 1)
>>>>>>> a2716e4 (geogame)

        screen.fill(WHITE)
        pygame.draw.line(screen, BLACK, (0, DINO_GROUND_LEVEL), (SCREEN_WIDTH, DINO_GROUND_LEVEL), 1)
        all_sprites.draw(screen)
<<<<<<< HEAD
        score_text = font.render(f"Score: {score // 10}", True, BLACK)
=======
        score_text = font.render(f"{score // 10}", True, BLACK)
>>>>>>> a2716e4 (geogame)
        screen.blit(score_text, (5, 5))

        if game_over:
            msg = title_font.render("GAME OVER", True, BLACK)
            screen.blit(msg, msg.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)))

<<<<<<< HEAD
        disp.image(Image.frombytes("RGB", screen.get_size(), pygame.image.tobytes(screen, "RGB")))
        clock.tick(FPS)

# ##########################################################################
# MAZE GAME CODE
# ##########################################################################

MAZE_COLS, MAZE_ROWS = 15, 8
CELL_SIZE = min(SCREEN_WIDTH // MAZE_COLS, SCREEN_HEIGHT // MAZE_ROWS)
MAZE_OFFSET_X = (SCREEN_WIDTH - MAZE_COLS * CELL_SIZE) // 2
MAZE_OFFSET_Y = (SCREEN_HEIGHT - MAZE_ROWS * CELL_SIZE) // 2
=======
        update_display(screen) # Use the new display function
        clock.tick(FPS)

# ##########################################################################
# MAZE GAME CODE (Rescaled for 128x32)
# ##########################################################################

# --- MODIFIED: Maze dimensions for new screen size ---
CELL_SIZE = 4
MAZE_COLS = SCREEN_WIDTH // CELL_SIZE
MAZE_ROWS = SCREEN_HEIGHT // CELL_SIZE
MAZE_OFFSET_X, MAZE_OFFSET_Y = 0, 0 # No offset needed if it fills screen
>>>>>>> a2716e4 (geogame)

class MazePlayer(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
<<<<<<< HEAD
        player_size = CELL_SIZE - 4
        
        if use_player_image:
            self.image = pygame.transform.scale(player_image_original, (player_size, player_size))
        else:
            self.image = pygame.Surface([player_size, player_size])
            self.image.fill(BLACK)
        
        self.x, self.y = 0, 0
        self.rect = self.image.get_rect(topleft=(MAZE_OFFSET_X + 2, MAZE_OFFSET_Y + 2))
=======
        player_size = CELL_SIZE - 1 # Player is almost as big as a cell
        self.image = pygame.transform.scale(player_sprite_raw, (player_size, player_size))
        self.x, self.y = 0, 0
        self.rect = self.image.get_rect(topleft=(MAZE_OFFSET_X, MAZE_OFFSET_Y))
>>>>>>> a2716e4 (geogame)

    def move(self, dx, dy, walls):
        new_x, new_y = self.x + dx, self.y + dy
        if 0 <= new_x < MAZE_COLS and 0 <= new_y < MAZE_ROWS:
<<<<<<< HEAD
            if dx == -1 and not walls[self.y][self.x][0]: self._update_pos(new_x, new_y)
            if dx == 1 and not walls[self.y][self.x][1]: self._update_pos(new_x, new_y)
            if dy == -1 and not walls[self.y][self.x][2]: self._update_pos(new_x, new_y)
            if dy == 1 and not walls[self.y][self.x][3]: self._update_pos(new_x, new_y)

    def _update_pos(self, new_x, new_y):
        self.x, self.y = new_x, new_y
        self.rect.x = MAZE_OFFSET_X + self.x * CELL_SIZE + 2
        self.rect.y = MAZE_OFFSET_Y + self.y * CELL_SIZE + 2


def generate_maze():
    walls = [[[True, True, True, True] for _ in range(MAZE_COLS)] for _ in range(MAZE_ROWS)] # L,R,U,D
    stack = [(0, 0)]
    visited = {(0, 0)}
    while stack:
        x, y = stack[-1]
        neighbors = []
        if x > 0 and (x-1, y) not in visited: neighbors.append((x-1, y, 0, 1)) 
        if x < MAZE_COLS-1 and (x+1, y) not in visited: neighbors.append((x+1, y, 1, 0))
        if y > 0 and (x, y-1) not in visited: neighbors.append((x, y-1, 2, 3))
        if y < MAZE_ROWS-1 and (x, y+1) not in visited: neighbors.append((x, y+1, 3, 2))
        
        if neighbors:
            nx, ny, wall_to_remove, opposite_wall = random.choice(neighbors)
            walls[y][x][wall_to_remove] = False
            walls[ny][nx][opposite_wall] = False
            visited.add((nx, ny))
            stack.append((nx, ny))
        else:
            stack.pop()
=======
            current_cell_walls = walls[self.y][self.x]
            if dx == -1 and not current_cell_walls[0]: self._update_pos(new_x, new_y)
            elif dx == 1 and not current_cell_walls[1]: self._update_pos(new_x, new_y)
            elif dy == -1 and not current_cell_walls[2]: self._update_pos(new_x, new_y)
            elif dy == 1 and not current_cell_walls[3]: self._update_pos(new_x, new_y)

    def _update_pos(self, new_x, new_y):
        self.x, self.y = new_x, new_y
        self.rect.x = MAZE_OFFSET_X + self.x * CELL_SIZE
        self.rect.y = MAZE_OFFSET_Y + self.y * CELL_SIZE

def generate_maze():
    walls = [[[True, True, True, True] for _ in range(MAZE_COLS)] for _ in range(MAZE_ROWS)] # L,R,U,D
    stack, visited = [(0, 0)], {(0, 0)}
    while stack:
        x, y = stack[-1]
        neighbors = []
        if x > 0 and (x-1, y) not in visited: neighbors.append((x-1, y, 0, 1))
        if x < MAZE_COLS-1 and (x+1, y) not in visited: neighbors.append((x+1, y, 1, 0))
        if y > 0 and (x, y-1) not in visited: neighbors.append((x, y-1, 2, 3))
        if y < MAZE_ROWS-1 and (x, y+1) not in visited: neighbors.append((x, y+1, 3, 2))
        if neighbors:
            nx, ny, wall, opp_wall = random.choice(neighbors)
            walls[y][x][wall] = False
            walls[ny][nx][opp_wall] = False
            visited.add((nx, ny)); stack.append((nx, ny))
        else: stack.pop()
>>>>>>> a2716e4 (geogame)
    return walls

def maze_game_loop():
    player = MazePlayer()
    all_sprites = pygame.sprite.Group(player)
    walls = generate_maze()
    goal_rect = pygame.Rect(MAZE_OFFSET_X + (MAZE_COLS-1)*CELL_SIZE, MAZE_OFFSET_Y + (MAZE_ROWS-1)*CELL_SIZE, CELL_SIZE, CELL_SIZE)
<<<<<<< HEAD
    last_move_time = 0
    move_cooldown = 200

    while True:
        if encoder_connected and not seesaw.digital_read(24):
            time.sleep(0.1) # Debounce
            return "MENU"
=======
    last_move_time, move_cooldown = 0, 200

    while True:
        if encoder_connected and not seesaw.digital_read(24):
            time.sleep(0.1); return "MENU"
>>>>>>> a2716e4 (geogame)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT"

        current_time = pygame.time.get_ticks()
        if current_time - last_move_time > move_cooldown:
            dx, dy = 0, 0
            if joystick_connected:
                x, y = myJoystick.horizontal, myJoystick.vertical
<<<<<<< HEAD
                if x < 300: dx = -1
                elif x > 700: dx = 1
                # *** CONTROLS FLIPPED ***
                elif y > 700: dy = 1 # Up on stick -> move player up
                elif y < 300: dy = -1  # Down on stick -> move player down
            else:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT]: dx = -1
                elif keys[pygame.K_RIGHT]: dx = 1
                elif keys[pygame.K_UP]: dy = -1
                elif keys[pygame.K_DOWN]: dy = 1
            
            if dx != 0 or dy != 0:
                player.move(dx, dy, walls)
                last_move_time = current_time

        screen.fill(WHITE)
=======
                if x < 300: dx = -1; elif x > 700: dx = 1
                elif y < 300: dy = -1; elif y > 700: dy = 1
            else:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT]: dx = -1; elif keys[pygame.K_RIGHT]: dx = 1
                elif keys[pygame.K_UP]: dy = -1; elif keys[pygame.K_DOWN]: dy = 1
            if dx != 0 or dy != 0:
                player.move(dx, dy, walls); last_move_time = current_time

        screen.fill(WHITE)
        pygame.draw.rect(screen, GREEN, goal_rect)
>>>>>>> a2716e4 (geogame)
        for r in range(MAZE_ROWS):
            for c in range(MAZE_COLS):
                x, y = MAZE_OFFSET_X + c * CELL_SIZE, MAZE_OFFSET_Y + r * CELL_SIZE
                if walls[r][c][0]: pygame.draw.line(screen, BLACK, (x, y), (x, y + CELL_SIZE))
                if walls[r][c][1]: pygame.draw.line(screen, BLACK, (x + CELL_SIZE, y), (x + CELL_SIZE, y + CELL_SIZE))
                if walls[r][c][2]: pygame.draw.line(screen, BLACK, (x, y), (x + CELL_SIZE, y))
                if walls[r][c][3]: pygame.draw.line(screen, BLACK, (x, y + CELL_SIZE), (x + CELL_SIZE, y + CELL_SIZE))
<<<<<<< HEAD
        
        pygame.draw.rect(screen, GREEN, goal_rect)
=======
>>>>>>> a2716e4 (geogame)
        all_sprites.draw(screen)

        if player.x == MAZE_COLS-1 and player.y == MAZE_ROWS-1:
            win_text = title_font.render("YOU WIN!", True, BLACK)
            screen.blit(win_text, win_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)))
<<<<<<< HEAD
            disp.image(Image.frombytes("RGB", screen.get_size(), pygame.image.tobytes(screen, "RGB")))
            time.sleep(2)
            return "MENU"

        disp.image(Image.frombytes("RGB", screen.get_size(), pygame.image.tobytes(screen, "RGB")))
=======
            update_display(screen); time.sleep(2); return "MENU"

        update_display(screen) # Use the new display function
>>>>>>> a2716e4 (geogame)
        clock.tick(FPS)

# ##########################################################################
# MENU AND MAIN APP LOOP
# ##########################################################################

def menu_loop():
    global last_encoder_pos
<<<<<<< HEAD
    games = ["DINO_GAME", "MAZE_GAME"]
=======
    games = ["DINO GAME", "MAZE GAME"]
>>>>>>> a2716e4 (geogame)
    selected_game_idx = 0

    while True:
        for event in pygame.event.get():
<<<<<<< HEAD
            if event.type == pygame.QUIT:
                return "QUIT"
            if not joystick_connected and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT: selected_game_idx = (selected_game_idx - 1) % len(games)
                if event.key == pygame.K_RIGHT: selected_game_idx = (selected_game_idx + 1) % len(games)
                if event.key == pygame.K_RETURN: return games[selected_game_idx]
        
        if encoder_connected:
            pos = encoder.position
            if pos > last_encoder_pos:
                selected_game_idx = (selected_game_idx + 1) % len(games)
            elif pos < last_encoder_pos:
                selected_game_idx = (selected_game_idx - 1) % len(games)
            last_encoder_pos = pos

        if joystick_connected and myJoystick.button == 0:
            time.sleep(0.2) # Debounce
            return games[selected_game_idx]

        screen.fill(WHITE)
        title_text = title_font.render("Pi Game Console", True, BLACK)
        screen.blit(title_text, title_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/3)))

        for i, game in enumerate(games):
            color = BLACK if i == selected_game_idx else (180, 180, 180)
            game_text = font.render(game.replace("_", " "), True, color)
            screen.blit(game_text, game_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 20 + i*30)))

        disp.image(Image.frombytes("RGB", screen.get_size(), pygame.image.tobytes(screen, "RGB")))
=======
            if event.type == pygame.QUIT: return "QUIT"
            if not joystick_connected and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT: selected_game_idx = (selected_game_idx - 1) % len(games)
                if event.key == pygame.K_RIGHT: selected_game_idx = (selected_game_idx + 1) % len(games)
                if event.key == pygame.K_RETURN: return games[selected_game_idx].replace(" ", "_")
        
        if encoder_connected:
            pos = encoder.position
            if pos > last_encoder_pos: selected_game_idx = (selected_game_idx + 1) % len(games)
            elif pos < last_encoder_pos: selected_game_idx = (selected_game_idx - 1) % len(games)
            last_encoder_pos = pos

        if joystick_connected and myJoystick.button == 0:
            time.sleep(0.2); return games[selected_game_idx].replace(" ", "_")

        screen.fill(WHITE)
        title_text = title_font.render("Pi Game Console", True, BLACK)
        screen.blit(title_text, title_text.get_rect(center=(SCREEN_WIDTH/2, 8)))

        for i, game in enumerate(games):
            color = BLACK if i == selected_game_idx else (180, 180, 180)
            game_text = font.render(game, True, color)
            screen.blit(game_text, game_text.get_rect(center=(SCREEN_WIDTH/2, 24)))

        # Simple indicator for selected game
        if selected_game_idx == 0: pygame.draw.line(screen, BLACK, (25, 30), (55, 30), 1)
        else: pygame.draw.line(screen, BLACK, (70, 30), (105, 30), 1)

        update_display(screen) # Use the new display function
>>>>>>> a2716e4 (geogame)
        clock.tick(FPS)

if __name__ == "__main__":
    game_state = "MENU"
    while game_state != "QUIT":
<<<<<<< HEAD
        if game_state == "MENU":
            game_state = menu_loop()
        elif game_state == "DINO_GAME":
            game_state = dino_game_loop()
        elif game_state == "MAZE_GAME":
            game_state = maze_game_loop()
    pygame.quit()
    sys.exit()


=======
        if game_state == "MENU": game_state = menu_loop()
        elif game_state == "DINO_GAME": game_state = dino_game_loop()
        elif game_state == "MAZE_GAME": game_state = maze_game_loop()
    pygame.quit()
    sys.exit()
>>>>>>> a2716e4 (geogame)
