import pygame
import math
import random

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
pygame.mixer.music.load("assets/music/Mozart-EineKleineNachtmusik8-bit.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)
shoot_sfx = pygame.mixer.Sound("assets/sfx/gun.wav")
end_explosion_sfx = pygame.mixer.Sound("assets/sfx/end_explosion.wav")
explosion_sfx = pygame.mixer.Sound("assets/sfx/explosion.wav")
explosion_image = pygame.image.load("assets/textures/explosion.png").convert_alpha()
explosion_image = pygame.transform.scale(explosion_image, (150, 150))

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
enemy_speed = 2
enemy_spawn_delay = 1000

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
            title_snapshot = screen.copy()  # Capture current screen (background + cannon + title)
            crossfade(title_snapshot, draw_initial_game_frame)
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
        if event.type == ENEMY_SPAWN:
            y_pos = random.randint(50, 670)
            enemies.append([0, y_pos])

        # Fire projectile
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            dx = mouse_x - cannon_x
            dy = mouse_y - cannon_y
            distance = math.hypot(dx, dy) or 1
            dx /= distance
            dy /= distance
            projectiles.append([cannon_x, cannon_y, dx, dy])
            shoot_sfx.play()

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

            # Reset game state
            enemies.clear()
            projectiles.clear()

            # Capture current game frame to crossfade back to title
            game_snapshot = screen.copy()
            crossfade(game_snapshot, draw_title_frame)
            
            # Restart title loop
            show_title = True
            while show_title:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                    elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                        title_snapshot = screen.copy()
                        crossfade(title_snapshot, draw_initial_game_frame)
                        show_title = False

                # Draw title screen
                screen.blit(background, (0, 0))

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
                break
    
    current_time = pygame.time.get_ticks()
    for explosion in explosions[:]:
        x, y, start_time = explosion
        if current_time - start_time < 500:
            screen.blit(explosion_image, (x, y))
        else:
            explosions.remove(explosion)

    # Draw projectiles
    for ball in projectiles:
        pygame.draw.circle(screen, "red", (int(ball[0]), int(ball[1])), 8)

    # Draw enemies
    for enemy in enemies:
        screen.blit(basic_IRS, (enemy[0], enemy[1]))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
