import pygame
from pygame import sprite, transform, image, display, time, event, mixer, QUIT, K_LEFT, K_RIGHT, K_UP, K_DOWN, font
import random
import math

# Required classes
# Parent class for sprites
class GameSprite(sprite.Sprite):
    # Class constructor
    def __init__(self, player_image, player_x, player_y, player_speed):
        super().__init__()
        # Every sprite must store the image property
        self.image = transform.scale(image.load(player_image), (65, 65))
        self.speed = player_speed
        # Every sprite must have the rect property — the rectangle it is fitted in
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

# Bullet class (aimed at cursor)
class Bullet(sprite.Sprite):
    def __init__(self, image_file, start_pos, target_pos, speed=15, size=(20, 20)):
        super().__init__()
        self.image = transform.scale(image.load(image_file), size)
        self.rect = self.image.get_rect()
        # place bullet centered at start_pos
        self.rect.center = start_pos

        # calculate velocity vector towards target_pos
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        dist = math.hypot(dx, dy)
        if dist == 0:
            dist = 1
        self.vx = dx / dist * speed
        self.vy = dy / dist * speed

    def update(self):
        # move by velocity vector
        self.rect.x += self.vx
        self.rect.y += self.vy
        # remove if off-screen
        if (self.rect.right < 0 or self.rect.left > win_width or
            self.rect.bottom < 0 or self.rect.top > win_height):
            self.kill()

# Player class
class Player(GameSprite):
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[K_LEFT] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.x < win_width - 70:
            self.rect.x += self.speed
        if keys[K_UP] and self.rect.y > 5:
            self.rect.y -= self.speed
        if keys[K_DOWN] and self.rect.y < win_height - 70:
            self.rect.y += self.speed

    def fire_at(self, target_pos):
        """Create a bullet aimed at target_pos (screen coordinates)."""
        # start from player's center
        start = (self.rect.centerx, self.rect.centery)
        b = Bullet('bullet.png', start, target_pos, speed=18, size=(20, 20))
        bullets.add(b)

# Enemy class
class Enemy1(GameSprite):
    def __init__(self, player_image, player_x, player_y, player_speed, direction_x=1, direction_y=1):
        super().__init__(player_image, player_x, player_y, player_speed * 5)  # scaled speed
        self.direction_x = direction_x
        self.direction_y = direction_y

    def update(self):
        self.rect.x += self.speed * self.direction_x
        self.rect.y += self.speed * self.direction_y

        # Reverse direction when hitting horizontal boundaries
        if self.rect.right >= win_width or self.rect.left <= 0:
            self.direction_x *= -1

        # Reverse direction when hitting vertical boundaries
        if self.rect.bottom >= win_height or self.rect.top <= 0:
            self.direction_y *= -1

# Wall class
class Wall(sprite.Sprite):
    def __init__(self, color, wall_x, wall_y, wall_width, wall_height):
        super().__init__()
        self.image = pygame.Surface([wall_width, wall_height])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = wall_x
        self.rect.y = wall_y

    def draw(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

# Game scene
win_width = 1200
win_height = 700
window = display.set_mode((win_width, win_height))
display.set_caption("Maze")
background = transform.scale(image.load("background.jpg"), (win_width, win_height))

# Game characters
packman = Player('hero.png', 5, win_height - 80, 4)

final = GameSprite('treasure.png', win_width - 120, win_height - 80, 0)

# Walls
wall1 = Wall((0, 255, 0), 100, 100, 1000, 20)
wall2 = Wall((0, 255, 0), 100, 580, 1000, 20)
wall3 = Wall((0, 255, 0), 100, 100, 20, 500)
wall4 = Wall((0, 255, 0), 1080, 100, 20, 500)
wall5 = Wall((0, 255, 0), 300, 150, 300, 20)
wall6 = Wall((0, 255, 0), 300, 150, 20, 200)
wall7 = Wall((0, 255, 0), 600, 300, 200, 20)
wall8 = Wall((0, 255, 0), 600, 300, 20, 150)
wall9 = Wall((0, 255, 0), 450, 450, 200, 20)
wall10 = Wall((0, 255, 0), 450, 450, 20, 80)
wall11 = Wall((0, 255, 0), 800, 200, 20, 200)
wall12 = Wall((0, 255, 0), 200, 350, 200, 20)
wall13 = Wall((0, 255, 0), 900, 400, 20, 180)
wall14 = Wall((0, 255, 0), 700, 500, 150, 20)

walls = sprite.Group()
walls.add(wall1, wall2, wall3, wall4, wall5, wall6, wall7, wall8, wall9, wall10, wall11, wall12, wall13, wall14)

# Bullets group
bullets = sprite.Group()

# Monsters group (use spawn_monster to create)
monsters = sprite.Group()

# Helper to spawn a monster that doesn't overlap walls or the player
def spawn_monster():
    attempts = 0
    while attempts < 20:
        monster_x = random.randint(100, win_width - 100)
        monster_y = random.randint(100, win_height - 100)
        direction_x = random.choice([-1, 1])
        direction_y = random.choice([-1, 1])
        m = Enemy1('cyborg.png', monster_x, monster_y, 2, direction_x, direction_y)
        # ensure new monster doesn't immediately collide with walls or player
        collision_with_wall = any(m.rect.colliderect(w.rect) for w in walls)
        collision_with_player = m.rect.colliderect(packman.rect)
        if not collision_with_wall and not collision_with_player:
            monsters.add(m)
            return m
        attempts += 1
    # fallback: add at a fixed safe place
    m = Enemy1('cyborg.png', win_width//2, win_height//2, 2, random.choice([-1,1]), random.choice([-1,1]))
    monsters.add(m)
    return m

# Spawn initial monster
spawn_monster()

# Track monster kill time to respawn after cooldown
spawn_cooldown_ms = 20000  # 20 seconds
last_monster_kill_time = None

# Adjust player and treasure positions to fit the maze
packman.rect.x = 120
packman.rect.y = 120

# Treasure position inside the maze
final.rect.x = 1000
final.rect.y = 150

# Fonts
pygame.font.init()
font = pygame.font.Font(None, 70)
win_text = font.render('YOU WIN!', True, (255, 215, 0))
lose_text = font.render('YOU LOSE!', True, (255, 0, 0))

# Music
mixer.init()
mixer.music.load('jungles.ogg')
mixer.music.play()
coin_sound = mixer.Sound('money.ogg')
impact_sound = mixer.Sound('kick.ogg')

game = True
clock = time.Clock()
FPS = 60

# Game loop
while game:
    for e in event.get():
        if e.type == QUIT:
            game = False
        # Fire bullet by left mouse click aimed at cursor
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            packman.fire_at(mouse_pos)
        # Optionally also allow spacebar to fire toward cursor
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_SPACE:
                mouse_pos = pygame.mouse.get_pos()
                packman.fire_at(mouse_pos)

    # Update game state
    window.blit(background, (0, 0))
    packman.update()
    monsters.update()
    bullets.update()

    # Draw everything
    packman.reset()
    monsters.draw(window)   # shows monster(s)
    for w in walls:
        w.draw()
    final.reset()
    bullets.draw(window)

    # Bullet hits monster -> remove both
    hits = sprite.groupcollide(monsters, bullets, True, True)
    if hits:
        # play impact sound when bullet hits monster
        try:
            impact_sound.play()
        except Exception:
            pass
        # Start cooldown timer for respawn
        last_monster_kill_time = pygame.time.get_ticks()

    # If there are no monsters and cooldown elapsed, respawn one
    if len(monsters) == 0 and last_monster_kill_time is not None:
        now = pygame.time.get_ticks()
        if now - last_monster_kill_time >= spawn_cooldown_ms:
            spawn_monster()
            last_monster_kill_time = None

    # Check for collisions (player touches treasure)
    if sprite.collide_rect(packman, final):
        window.blit(win_text, (win_width // 2 - win_text.get_width() // 2, win_height // 2 - win_text.get_height() // 2))
        mixer.music.stop()
        try:
            coin_sound.play()
        except Exception:
            pass
        display.update()
        pygame.time.wait(5000)
        game = False
        pygame.quit()  # Close the window

    # Player collides with any remaining monster or with walls -> lose
    if sprite.spritecollide(packman, monsters, False) or sprite.spritecollide(packman, walls, False):
        window.blit(lose_text, (win_width // 2 - lose_text.get_width() // 2, win_height // 2 - lose_text.get_height() // 2))
        mixer.music.stop()
        try:
            impact_sound.play()
        except Exception:
            pass
        display.update()
        pygame.time.wait(3000)
        game = False
        pygame.quit()

    display.update()
    clock.tick(FPS)