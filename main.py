import pygame
import sys
import math
import random

# Initialize Pygame
pygame.init()
clock = pygame.time.Clock()

# Screen dimensions
screen_info = pygame.display.Info()
WIDTH = screen_info.current_w
HEIGHT = screen_info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.flip()
pygame.display.set_caption('Player Mover with Enemy')

# Load images
player_image = pygame.image.load('assets/player.png')
player_image = pygame.transform.scale(player_image, (50, 50))  # Scale player image to match enemy size
enemy_image = pygame.image.load('assets/red_skull.png')
enemy_image = pygame.transform.scale(enemy_image, (50, 50))  # Scale enemy image to match player size
house_image = pygame.image.load('assets/house.png')
house_image = pygame.transform.scale(house_image, (50, 50))  # Scale house image to match enemy size
projectile_image = pygame.image.load('assets/t-rex-skull.png')
projectile_image = pygame.transform.scale(projectile_image, (50, 50))  # Scale projectile image to match player size
background_image = pygame.image.load('assets/Screenshot.png')
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))  # Stretch to fit screen

# Constants
PLAYER_SPEED = 5
ENEMY_SPEED = PLAYER_SPEED * 0.5
PROJECTILE_SPEED = 8
ENEMY_RADIUS = enemy_image.get_width() // 2  # Use half the width as the radius for collision detection
HOUSE_SPAWN_DISTANCE = 200  # Distance from player where the house spawns enemies

# Classes
class Entity(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.x = x
        self.y = y
    
    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Player(Entity):
    def __init__(self, image, x, y):
        super().__init__(image, x, y)
    
    def update(self, keys):
        dx, dy = 0, 0
        if keys[pygame.K_w]:  # Move up
            dy = -PLAYER_SPEED
        elif keys[pygame.K_s]:  # Move down
            dy = PLAYER_SPEED
        if keys[pygame.K_a]:  # Move left
            dx = -PLAYER_SPEED
        elif keys[pygame.K_d]:  # Move right
            dx = PLAYER_SPEED
        
        # Move player
        self.rect.x += dx
        self.rect.y += dy

        self.x += dx
        self.y += dy

        # Keep player within window boundaries
        self.rect.x = max(0, min(self.rect.x, WIDTH - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, HEIGHT - self.rect.height))

        self.x = max(0, min(self.rect.x, WIDTH - self.rect.width))
        self.y = max(0, min(self.rect.y, HEIGHT - self.rect.height))

class Enemy(Entity):
    def __init__(self, image, x, y):
        super().__init__(image, x, y)
    
    def update(self, player_x, player_y):
        dx = player_x - self.x
        dy = player_y - self.y
        dist = math.hypot(dx, dy)
        if dist != 0:
            dx /= dist
            dy /= dist
        self.x += dx * ENEMY_SPEED
        self.y += dy * ENEMY_SPEED
        self.rect.center = (self.x, self.y)

class House(Entity):
    def __init__(self, image, x, y):
        super().__init__(image, x, y)
    
    def spawn_enemy(self, player, enemies):
        while True:
            if player.x - self.x < 0:
                x = random.randint(0, self.x+20)
            else:
                x = random.randint(self.x, player.x+20)
            
            if player.y - self.y < 0:
                y = random.randint(0, self.y+20)
            else:
                y = random.randint(self.y, player.y+20)

            if math.hypot(x - player.x, y - player.y) > 200:  # Adjust the distance threshold as needed
                new_enemy = Enemy(enemy_image, x, y)

                return new_enemy  # Exit the loop and return the created enemy

class Projectile(Entity):
    def __init__(self, image, x, y, target_x, target_y):
        super().__init__(image, x, y)
        self.target_x = target_x
        self.target_y = target_y
    
    def update(self, enemies):
        if enemies:
            nearest_enemy = min(enemies, key=lambda enemy: math.hypot(self.x - enemy.x, self.y - enemy.y))
            dx = nearest_enemy.x - self.x
            dy = nearest_enemy.y - self.y
            dist = math.hypot(dx, dy)
            if dist != 0:
                dx /= dist
                dy /= dist
            self.x += dx * PROJECTILE_SPEED
            self.y += dy * PROJECTILE_SPEED
            self.rect.center = (self.x, self.y)

# Initialize game objects
player = Player(player_image, WIDTH // 2, HEIGHT // 2)
house = House(house_image, random.randint(player.x + HOUSE_SPAWN_DISTANCE, WIDTH - house_image.get_width()),
              random.randint(0, HEIGHT - house_image.get_height()))
enemies = []
enemies = [house.spawn_enemy(player, enemies)]  # List to store enemy instances
projectiles = []  # List to store projectile instances
enemies_killed = 0  # Counter for enemies killed

# Game state
game_over = False
retry_game = False

# Main game loop
while True:
    screen.blit(background_image, (0, 0))  # Draw the background

    keys = pygame.key.get_pressed()
    player.update(keys)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and not retry_game:
            projectiles.append(Projectile(projectile_image,
                                          player.x + player.rect.width // 2,
                                          player.y + player.rect.height // 2,
                                          player.x + player.rect.width // 2,
                                          player.y + player.rect.height // 2))

    new_projectiles = []
    for projectile in projectiles:
        projectile.update(enemies)  # Pass enemies list to update method
        hit = False
        for enemy in enemies[:]:  # Iterate over a copy of the list
            if projectile.rect.colliderect(enemy.rect):
                enemies.remove(enemy)  # Remove enemy instance
                enemies.extend([house.spawn_enemy(player, enemies) for _ in range(2)])  # Spawn 2 new enemies
                enemies_killed += 1
                hit = True
        if not hit:
            new_projectiles.append(projectile)
        projectile.draw(screen)  # Draw the projectile after updating

    projectiles = new_projectiles

    for enemy in enemies[:]:  # Iterate over a copy of the list
        enemy.update(player.x + player.rect.width // 2, player.y + player.rect.height // 2)
        if enemy.rect.colliderect(player.rect):
            game_over = True
            retry_game = True

    player.draw(screen)
    house.draw(screen)
    for enemy in enemies:
        enemy.draw(screen)

    if game_over:
        font = pygame.font.Font(None, 36)
        text = font.render(f"Game Over - Enemies Killed: {enemies_killed}", True, (255, 255, 255))
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(text, text_rect)

        retry_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50)
        pygame.draw.rect(screen, (0, 255, 0), retry_button)
        retry_text = font.render("Retry", True, (0, 0, 0))
        retry_text_rect = retry_text.get_rect(center=retry_button.center)
        screen.blit(retry_text, retry_text_rect)

        quit_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 120, 200, 50)
        pygame.draw.rect(screen, (255, 0, 0), quit_button)
        quit_text = font.render("Quit", True, (0, 0, 0))
        quit_text_rect = quit_text.get_rect(center=quit_button.center)
        screen.blit(quit_text, quit_text_rect)

        mouse_x, mouse_y = pygame.mouse.get_pos()

        if retry_button.collidepoint((mouse_x, mouse_y)) and pygame.mouse.get_pressed()[0]:
            game_over = False
            retry_game = False
            enemies = [house.spawn_enemy(player, enemies)]
            enemies_killed = 0

        if quit_button.collidepoint((mouse_x, mouse_y)) and pygame.mouse.get_pressed()[0]:
            pygame.quit()
            sys.exit()

    pygame.display.update()
    clock.tick(60)
