# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import digitalio
import board
from PIL import Image
import pygame
import random
import busio
import adafruit_mpr121
import adafruit_rgb_display.st7789 as st7789

# --- Controller Hardware Setup ---
i2c = busio.I2C(board.SCL, board.SDA)
mpr121 = adafruit_mpr121.MPR121(i2c)
JUMP_PIN = 0
DUCK_PIN = 1

# --- Display Hardware Setup ---
cs_pin = digitalio.DigitalInOut(board.D5)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D24)
BAUDRATE = 24000000
spi = board.SPI()

disp = st7789.ST7789(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
    width=135,
    height=240,
    x_offset=53,
    y_offset=40,
)

# Set display rotation to landscape and turn on backlight
disp.rotation = 90
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

# --- Pygame Setup ---
# *** THIS IS THE FIX ***
# Directly use the display's width and height after the rotation has been set.
# The library automatically swaps them for us.
SCREEN_WIDTH = disp.width
SCREEN_HEIGHT = disp.height

pygame.init()
# This screen surface is created in memory and will be sent to the display
screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

# Colors and Fonts (adjusted for smaller screen)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
font = pygame.font.Font(None, 24)
game_over_font = pygame.font.Font(None, 40)

# Game Variables
clock = pygame.time.Clock()
FPS = 30
GROUND_LEVEL = SCREEN_HEIGHT - 25

# --- Player Class (adjusted for smaller screen) ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.normal_height = 25
        self.duck_height = 12
        self.image = pygame.Surface([20, self.normal_height])
        self.image.fill(BLACK)
        self.rect = self.image.get_rect(bottomleft=(20, GROUND_LEVEL))
        self.velocity_y = 0
        self.gravity = 0.8
        self.is_jumping = False
        self.is_ducking = False

    def update(self):
        if self.is_jumping:
            self.velocity_y += self.gravity
            self.rect.y += self.velocity_y
        if self.rect.bottom >= GROUND_LEVEL:
            self.rect.bottom = GROUND_LEVEL
            self.is_jumping = False
            self.velocity_y = 0

    def jump(self):
        if not self.is_jumping and not self.is_ducking:
            self.is_jumping = True
            self.velocity_y = -10

    def duck(self, is_pressed):
        if self.is_jumping: return
        if is_pressed and not self.is_ducking:
            self.is_ducking = True
            self.image = pygame.Surface([20, self.duck_height])
            self.image.fill(BLACK)
            self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
        elif not is_pressed and self.is_ducking:
            self.is_ducking = False
            self.image = pygame.Surface([20, self.normal_height])
            self.image.fill(BLACK)
            self.rect = self.image.get_rect(midbottom=self.rect.midbottom)

# --- Obstacle Class (adjusted for smaller screen) ---
class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        if random.choice([True, False]): # Cactus
            self.image = pygame.Surface([10, 25])
            self.rect = self.image.get_rect(bottomleft=(SCREEN_WIDTH, GROUND_LEVEL))
        else: # Bird
            self.image = pygame.Surface([15, 15])
            self.rect = self.image.get_rect(bottomleft=(SCREEN_WIDTH, GROUND_LEVEL - 20))
        self.image.fill(BLACK)

    def update(self):
        self.rect.x -= 5
        if self.rect.right < 0:
            self.kill()

# --- Game Loop Function ---
def game_loop():
    player = Player()
    obstacles = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group(player)
    running = True
    game_over = False
    score = 0
    obstacle_timer = pygame.USEREVENT + 1
    pygame.time.set_timer(obstacle_timer, 2000)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if not game_over and event.type == obstacle_timer:
                new_obstacle = Obstacle()
                obstacles.add(new_obstacle)
                all_sprites.add(new_obstacle)

        if not game_over:
            if mpr121[JUMP_PIN].value:
                player.jump()
            player.duck(mpr121[DUCK_PIN].value)
            all_sprites.update()
            score += 1
            if pygame.sprite.spritecollide(player, obstacles, False):
                game_over = True

        screen.fill(WHITE)
        pygame.draw.line(screen, BLACK, (0, GROUND_LEVEL), (SCREEN_WIDTH, GROUND_LEVEL), 1)
        all_sprites.draw(screen)
        score_text = font.render(f"Score: {score // 10}", True, BLACK)
        screen.blit(score_text, (5, 5))

        if game_over:
            over_text = game_over_font.render("GAME OVER", True, BLACK)
            text_rect = over_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
            screen.blit(over_text, text_rect)

        pixel_data = pygame.image.tostring(screen, "RGB")
        image = Image.frombytes("RGB", screen.get_size(), pixel_data)
        disp.image(image)

        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    game_loop()


