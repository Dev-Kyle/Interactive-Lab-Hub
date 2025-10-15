import pygame
import random
import board
import busio
import adafruit_mpr121

i2c = busio.I2C(board.SCL, board.SDA)
mpr121 = adafruit_mpr121.MPR121(i2c)
JUMP_PIN = 0
DUCK_PIN = 1

# 2. Pygame Setup
pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pi Dino Game (Keyboard Test)")

# Colors and Fonts
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
font = pygame.font.Font(None, 36)
game_over_font = pygame.font.Font(None, 72)

# Game Variables
clock = pygame.time.Clock()
FPS = 60
GROUND_LEVEL = SCREEN_HEIGHT - 50

# 3. Player Class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.normal_height = 50
        self.duck_height = 25
        self.image = pygame.Surface([40, self.normal_height])
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = GROUND_LEVEL
        self.rect.left = 50

        self.velocity_y = 0
        self.gravity = 1
        self.is_jumping = False
        self.is_ducking = False

    def update(self):
        # Apply gravity
        if self.is_jumping:
            self.velocity_y += self.gravity
            self.rect.y += self.velocity_y

        # Check if landed
        if self.rect.bottom >= GROUND_LEVEL:
            self.rect.bottom = GROUND_LEVEL
            self.is_jumping = False
            self.velocity_y = 0

    def jump(self):
        if not self.is_jumping and not self.is_ducking:
            self.is_jumping = True
            self.velocity_y = -20

    def duck(self, is_pressed):
        if self.is_jumping: return

        if is_pressed and not self.is_ducking:
            self.is_ducking = True
            self.image = pygame.Surface([40, self.duck_height])
            self.image.fill(BLACK)
            self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
        elif not is_pressed and self.is_ducking:
            self.is_ducking = False
            self.image = pygame.Surface([40, self.normal_height])
            self.image.fill(BLACK)
            self.rect = self.image.get_rect(midbottom=self.rect.midbottom)

# 4. Obstacle Class
class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Randomly choose obstacle type
        if random.choice([True, False]):
            height = 50 # A cactus to jump over
        else:
            height = 40 # A bird to duck under

        self.image = pygame.Surface([20, height])
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = GROUND_LEVEL if height == 50 else GROUND_LEVEL - 30
        self.rect.left = SCREEN_WIDTH

    def update(self):
        self.rect.x -= 8 # Move left
        if self.rect.right < 0:
            self.kill()

# 5. Game Loop
def game_loop():
    player = Player()
    obstacles = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group(player)

    running = True
    game_over = False
    score = 0
    obstacle_timer = pygame.USEREVENT + 1
    pygame.time.set_timer(obstacle_timer, 1500)

    while running:
        # --- Event Handling ---
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
        pygame.draw.line(screen, BLACK, (0, GROUND_LEVEL), (SCREEN_WIDTH, GROUND_LEVEL), 2)
        all_sprites.draw(screen)

        score_text = font.render(f"Score: {score // 10}", True, BLACK)
        screen.blit(score_text, (10, 10))

        if game_over:
            over_text = game_over_font.render("GAME OVER", True, BLACK)
            text_rect = over_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
            screen.blit(over_text, text_rect)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    game_loop()
