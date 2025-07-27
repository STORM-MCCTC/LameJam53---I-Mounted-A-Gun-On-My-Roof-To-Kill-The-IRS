import pygame
import math
import random
import time

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
pygame.display.set_caption("I Mounted A Gun On My Roof To Kill The IRS Because I Committed Tax Evasion")
icon = pygame.image.load("assets/textures/IRS.png")
pygame.display.set_icon(icon)

# Load assets
background = pygame.image.load("assets/textures/background.png").convert()
background = pygame.transform.scale(background, (1280, 720))
raw_cannon_image = pygame.image.load("assets/textures/cannon.png").convert_alpha()
cannon_image = pygame.transform.scale(raw_cannon_image, (300, 300))
basic_IRS = pygame.image.load("assets/textures/IRS.png")
basic_IRS = pygame.transform.scale(basic_IRS, (150, 150))
title_screen = pygame.image.load("assets/textures/title.png").convert_alpha()
title_screen = pygame.transform.scale(title_screen, (640, 360))
title_surface = pygame.Surface((1280, 720))
title_surface.blit(title_screen, ((1280 - title_screen.get_width()) // 2, (720 - title_screen.get_height()) // 2))
shoot_sfx = pygame.mixer.Sound("assets/sfx/gun.wav")
end_explosion_sfx = pygame.mixer.Sound("assets/sfx/end_explosion.wav")
explosion_sfx = pygame.mixer.Sound("assets/sfx/explosion.wav")
explosion_image = pygame.image.load("assets/textures/explosion.png").convert_alpha()
explosion_image = pygame.transform.scale(explosion_image, (150, 150))
bullet_image = pygame.image.load("assets/textures/bullet.png").convert_alpha()
bullet_image = pygame.transform.scale(bullet_image, (64, 64))
font = pygame.font.Font("assets/fonts/daydream_3/Daydream.ttf", 16)
font2 = pygame.font.Font("assets/fonts/daydream_3/Daydream.ttf", 64)
pygame.mixer.music.load("assets/music/Mozart-EineKleineNachtmusik8-bit.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

#functions
def fade_out(surface, duration=1000):
    fade = pygame.Surface((1280, 720))
    fade.fill((0, 0, 0))
    for alpha in range(0, 255, int(255 / (duration / (1000 / 60)))):
        fade.set_alpha(alpha)
        screen.blit(surface, (0, 0))
        screen.blit(fade, (0, 0))
        pygame.display.update()
        clock.tick(60)

def crossfade(title_surface, game_surface_func, duration=1000):
    steps = int(duration / (1000 / 60))  # number of frames
    for i in range(steps + 1):
        alpha = int((i / steps) * 255)

        # Get the current frame of the game
        game_surface = game_surface_func()

        # Blend both surfaces using alpha
        blended_surface = title_surface.copy()
        temp_game_surface = game_surface.copy()
        temp_game_surface.set_alpha(alpha)
        blended_surface.blit(temp_game_surface, (0, 0))

        # Show the blended result
        screen.blit(blended_surface, (0, 0))
        pygame.display.flip()
        clock.tick(60)

def draw_initial_game_frame():
    game_surface = pygame.Surface((1280, 720))

    # Background
    game_surface.blit(background, (0, 0))

    # Cannon rotation toward mouse
    mouse_x, mouse_y = pygame.mouse.get_pos()
    dx = mouse_x - cannon_x
    dy = mouse_y - cannon_y
    angle = math.degrees(math.atan2(-dy, dx)) + 180
    rotated_cannon = pygame.transform.rotate(cannon_image, angle)
    rect = rotated_cannon.get_rect(center=(cannon_x, cannon_y))
    game_surface.blit(rotated_cannon, rect.topleft)

    return game_surface

def draw_title_frame():
    surface = pygame.Surface((1280, 720))
    surface.blit(background, (0, 0))

    # Cannon aiming
    mouse_x, mouse_y = pygame.mouse.get_pos()
    dx = mouse_x - cannon_x
    dy = mouse_y - cannon_y
    angle = math.degrees(math.atan2(-dy, dx)) + 180
    rotated_cannon = pygame.transform.rotate(cannon_image, angle)
    rect = rotated_cannon.get_rect(center=(cannon_x, cannon_y))
    surface.blit(rotated_cannon, rect.topleft)

    surface.blit(title_screen, ((1280 - title_screen.get_width()) // 2, (720 - title_screen.get_height()) // 2))
    return surface

# Cannon position
cannon_x = 1060
cannon_y = 720 // 2

# Lists
projectiles = []
enemies = []
explosions = []

# Settings
projectile_speed = 10
cannon_shoot_delay = 3000
enemy_speed = 2.0
enemy_spawn_delay = 1000
fire_cooldown = 1000
last_shot_time = 0

# Money Sys
money = 0.0
moneyMultiplier = 1.0

# Waves
wave = 1
wave_high = 0
enemies_remaining = 5  # enemies in the current wave
spawned_enemies = 0
wave_font = pygame.font.Font("assets/fonts/daydream_3/Daydream.ttf", 32)
wave_active = True

#upgrade system
upgrades = [
    {"name": "Money Multiplier", "key": "moneyMultiplier", "cost": 20, "amount": 1},
    {"name": "Projectile Speed", "key": "projectile_speed", "cost": 10, "amount": 2},
    {"name": "Fire Rate", "key": "fire_cooldown", "cost": 10, "amount": -100},
]

def increase_multiplier():
    global moneyMultiplier
    moneyMultiplier *= 2

def increase_projectile_speed():
    global projectile_speed
    projectile_speed += 5

def reduce_cooldown():
    global fire_cooldown
    fire_cooldown = max(100, fire_cooldown - 100)

def upgrade_phase():
    global money, moneyMultiplier, projectile_speed, fire_cooldown

    upgrade_active = True
    start_time = pygame.time.get_ticks()

    while upgrade_active:
        screen.blit(background, (0, 0))

        # Timer
        elapsed = (pygame.time.get_ticks() - start_time) // 1000
        remaining = max(0, 60 - elapsed)
        screen.blit(font.render(f"Upgrade Time: {remaining}s", True, (255, 255, 0)), (10, 10))

        # Show money
        screen.blit(font.render(f"Money: ${money}", True, (255, 255, 255)), (10, 50))
        screen.blit(font.render("press 'enter' to continue", True, (255, 255, 255)), (10, 90))

        # Draw upgrade buttons
        for i, upgrade in enumerate(upgrades):
            x, y = 100, 150 + i * 100
            pygame.draw.rect(screen, (0, 100, 200), (x, y, 400, 80))
            screen.blit(font.render(f"{upgrade['name']} (${upgrade['cost']})", True, (255, 255, 255)), (x + 10, y + 20))

        pygame.display.flip()

        # SINGLE event loop!
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    upgrade_active = False  # skip phase

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                for i, upgrade in enumerate(upgrades):
                    ux, uy, uw, uh = 100, 150 + i * 100, 400, 80
                    if ux <= mx <= ux + uw and uy <= my <= uy + uh:
                        if money >= upgrade["cost"]:
                            money -= upgrade["cost"]
                            if upgrade["key"] == "moneyMultiplier":
                                moneyMultiplier += upgrade["amount"]
                            elif upgrade["key"] == "projectile_speed":
                                projectile_speed += upgrade["amount"]
                            elif upgrade["key"] == "fire_cooldown":
                                fire_cooldown = max(100, fire_cooldown + upgrade["amount"])

        # Auto-exit after 60 seconds
        if remaining <= 0:
            upgrade_active = False

        clock.tick(60)

# Timer for enemy spawn
ENEMY_SPAWN = pygame.USEREVENT + 1
pygame.time.set_timer(ENEMY_SPAWN, enemy_spawn_delay)

# Title screen loop
show_title = True
while show_title:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            show_title = False

    screen.blit(background, (0, 0))

    # Get mouse position
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Calculate angle to mouse (in degrees)
    dx = mouse_x - cannon_x
    dy = mouse_y - cannon_y
    angle = math.degrees(math.atan2(-dy, dx)) + 180

    # Rotate cannon
    rotated_cannon = pygame.transform.rotate(cannon_image, angle)

    # Adjust for rotation offset to keep cannon centered
    rect = rotated_cannon.get_rect(center=(cannon_x, cannon_y))

    # Draw cannon
    screen.blit(rotated_cannon, rect.topleft)

    # Draw title image centered (same math used in title_surface)
    title_x = (1280 - title_screen.get_width()) // 2
    title_y = (720 - title_screen.get_height()) // 2
    screen.blit(title_screen, (title_x, title_y))

    pygame.display.flip()
    clock.tick(60)


# Game loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Spawn enemy on timer
        if event.type == ENEMY_SPAWN and wave_active:
            if spawned_enemies < enemies_remaining:
                y_pos = random.randint(50, 670)
                enemies.append([0, y_pos])
                spawned_enemies += 1

        # Fire projectile
        if event.type == pygame.MOUSEBUTTONDOWN:
            current_time = pygame.time.get_ticks()
            if current_time - last_shot_time >= fire_cooldown:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                dx = mouse_x - cannon_x
                dy = mouse_y - cannon_y
                distance = math.hypot(dx, dy) or 1
                dx /= distance
                dy /= distance
                projectiles.append([cannon_x, cannon_y, dx, dy])
                shoot_sfx.play()
                last_shot_time = current_time

    current_time = pygame.time.get_ticks()

    # Draw background
    screen.blit(background, (0, 0))

    # Get mouse position
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Calculate angle to mouse (in degrees)
    dx = mouse_x - cannon_x
    dy = mouse_y - cannon_y
    angle = math.degrees(math.atan2(-dy, dx)) + 180

    # Rotate cannon
    rotated_cannon = pygame.transform.rotate(cannon_image, angle)

    # Adjust for rotation offset to keep cannon centered
    rect = rotated_cannon.get_rect(center=(cannon_x, cannon_y))

    # Draw cannon
    screen.blit(rotated_cannon, rect.topleft)

    # Draw On screen Text
    screen.blit(font.render(f"Money: {money}", True, (255, 255, 255)), (10, 10))
    screen.blit(font.render(f"Wave: {wave}", True, (255, 255, 255)), (10, 40))
    screen.blit(font.render(f"Multiplier: X{moneyMultiplier}", True, (255, 255, 255)), (10, 70))

    # Update projectiles
    for ball in projectiles:
        ball[0] += ball[2] * projectile_speed
        ball[1] += ball[3] * projectile_speed

    # Remove offscreen projectiles
    projectiles = [b for b in projectiles if 0 <= b[0] <= 1280 and 0 <= b[1] <= 720]

    # Update enemies and check if they reach the cannon
    for enemy in enemies:
        enemy[0] += enemy_speed
        if enemy[0] + 240 >= cannon_x:
            end_explosion_sfx.play()

            # Show GAME OVER text
            screen.blit(font2.render("GAMEOVER :(", True, (255, 0, 0)), (320, 160))
            pygame.display.flip()
            pygame.time.delay(1000)

            if wave > wave_high:
                wave_high = wave

            # Reset game state
            enemies.clear()
            projectiles.clear()
            money = 0
            moneyMultiplier = 1
            wave = 0
            enemy_speed = 2.0
            projectile_speed = 10
            cannon_shoot_delay = 3000
            enemy_speed = 2.0
            enemy_spawn_delay = 1000
            fire_cooldown = 1000
            last_shot_time = 0

            # Restart title loop
            show_title = True
            while show_title:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                    elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                        show_title = False

                # Draw title screen
                screen.blit(background, (0, 0))
                screen.blit(font.render(f"HighScore: Wave {wave_high}", True, (255, 255, 255)), (10, 10))

                mouse_x, mouse_y = pygame.mouse.get_pos()
                dx = mouse_x - cannon_x
                dy = mouse_y - cannon_y
                angle = math.degrees(math.atan2(-dy, dx)) + 180
                rotated_cannon = pygame.transform.rotate(cannon_image, angle)
                rect = rotated_cannon.get_rect(center=(cannon_x, cannon_y))
                screen.blit(rotated_cannon, rect.topleft)

                screen.blit(title_screen, ((1280 - title_screen.get_width()) // 2, (720 - title_screen.get_height()) // 2))
                pygame.display.flip()
                clock.tick(60)

            break  # Exit current game loop so it restarts

    # Check for collisions and remove enemies hit
    for ball in projectiles:
        ball_rect = pygame.Rect(ball[0] - 4, ball[1] - 4, 8, 8)
        for enemy in enemies:
            enemy_rect = pygame.Rect(enemy[0], enemy[1], 150, 150)
            if ball_rect.colliderect(enemy_rect):
                enemies.remove(enemy)
                explosions.append([enemy[0], enemy[1], pygame.time.get_ticks()])
                projectiles.remove(ball)
                explosion_sfx.play()
                Multiplieroutput = 1 * moneyMultiplier
                money += Multiplieroutput
                break

    # Explosion handler
    for explosion in explosions[:]:
        x, y, start_time = explosion
        if current_time - start_time < 500:
            screen.blit(explosion_image, (x, y))
        else:
            explosions.remove(explosion)

    # Draw projectiles
    for ball in projectiles:
        x, y, dx, dy = ball

        # Calculate angle in degrees
        angle = math.degrees(math.atan2(-dy, dx)) + 180

        # Rotate the bullet
        rotated_bullet = pygame.transform.rotate(bullet_image, angle)

        # Draw with center alignment
        rect = rotated_bullet.get_rect(center=(x, y))
        screen.blit(rotated_bullet, rect.topleft)

    # Draw enemies
    for enemy in enemies:
        screen.blit(basic_IRS, (enemy[0], enemy[1]))

    #Wave logic
    if wave_active and spawned_enemies == enemies_remaining and len(enemies) == 0:
        wave_active = False
        wave_cooldown = pygame.time.get_ticks()

        # Upgrade phase before next wave
        upgrade_phase()

        # After upgrade, start new wave
        wave += 1
        enemies_remaining = 5 + wave * 2
        spawned_enemies = 0
        if enemy_speed < 10:
            enemy_speed += 0.5

    if not wave_active:
        if pygame.time.get_ticks() - wave_cooldown > 2000:  # 2-second delay
            wave_active = True

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
