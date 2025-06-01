import asyncio
import platform
import pygame
import sys
import random
import math
import numpy as np
from pygame import sndarray

# Constants
TILE = 24
COLUMNS = 28
ROWS = 31
W, H = COLUMNS * TILE, ROWS * TILE
FPS = 60

# Colors
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
PINK = (255, 184, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 184, 82)

# Directions
dirs = {
    'UP': (0, -1),
    'DOWN': (0, 1),
    'LEFT': (-1, 0),
    'RIGHT': (1, 0),
    'NONE': (0, 0)
}

# Maze layout
layout = [
    "1111111111111111111111111111",
    "1000000000000000000000000001",
    "1011110111110111110111111101",
    "1020000100000100000100000201",
    "1011110111110111110111111101",
    "1000000000000000000000000001",
    "1011110110111110110111111101",
    "1000000110000000110000000101",
    "1111110111110111110111111101",
    "0000010100000100000101000000",
    "1111010111110111110101111101",
    "1000010000100000000100000101",
    "1011111110101111110101111101",
    "1000000000000000000000000001",
    "1111010111110111110101111101",
    "0000010100000100000101000000",
    "1111110111110111110111111101",
    "1000000110000000110000000101",
    "1011110110111110110111111101",
    "1000000000000000000000000001",
    "1011110111110111110111111101",
    "1020000100000100000100000201",
    "1011110111110111110111111101",
    "1000000000000000000000000001",
    "1111111111111111111111111111",
    "0000000000000000000000000000",
    "1111111111111111111111111111",
    "1000000000000000000000000001",
    "1000000000000000000000000001",
    "1000000000000000000000000001",
    "1111111111111111111111111111",
    "0000000000000000000000000000"
]

maze = [[int(ch) for ch in row] for row in layout]

# Sound generation functions
def generate_square_wave(freq, duration, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = np.sign(np.sin(freq * 2 * np.pi * t))  # Square wave
    return wave * 0.5  # Reduce amplitude to avoid clipping

def generate_sawtooth_wave(freq, duration, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = 2 * (t * freq - np.floor(0.5 + t * freq))  # Sawtooth wave
    return wave * 0.4  # Reduce amplitude

def generate_waka_sound():
    sample_rate = 44100
    duration = 0.05
    wave1 = generate_square_wave(600, duration)
    wave2 = generate_square_wave(800, duration)
    wave = np.concatenate([wave1, wave2])  # Rapid alternation
    wave = (wave * 32767).astype(np.int16)
    stereo_wave = np.column_stack((wave, wave))
    return sndarray.make_sound(stereo_wave)

def generate_start_sound():
    sample_rate = 44100
    # Melody: C4, E4, G4, C5, G4, E4, C4 (approximate Pac-Man intro)
    notes = [
        (261.63, 0.15),  # C4
        (329.63, 0.15),  # E4
        (392.00, 0.15),  # G4
        (523.25, 0.15),  # C5
        (392.00, 0.15),  # G4
        (329.63, 0.15),  # E4
        (261.63, 0.30)   # C4 (longer)
    ]
    wave = np.concatenate([generate_square_wave(freq, dur) for freq, dur in notes])
    wave = (wave * 32767).astype(np.int16)
    stereo_wave = np.column_stack((wave, wave))
    return sndarray.make_sound(stereo_wave)

def generate_power_pellet_sound():
    sample_rate = 44100
    duration = 0.1
    wave1 = generate_square_wave(400, duration)
    wave2 = generate_square_wave(600, duration)
    wave = np.concatenate([wave1, wave2] * 3)  # Pulsing effect
    wave = (wave * 32767).astype(np.int16)
    stereo_wave = np.column_stack((wave, wave))
    return sndarray.make_sound(stereo_wave)

def generate_ghost_eaten_sound():
    sample_rate = 44100
    duration = 0.1
    wave1 = generate_square_wave(800, duration)
    wave2 = generate_square_wave(1200, duration)
    wave3 = generate_square_wave(1000, duration)
    wave = np.concatenate([wave1, wave2, wave3])  # Ascend then descend
    wave = (wave * 32767).astype(np.int16)
    stereo_wave = np.column_stack((wave, wave))
    return sndarray.make_sound(stereo_wave)

def generate_death_sound():
    sample_rate = 44100
    notes = [
        (600, 0.1),
        (550, 0.1),
        (500, 0.1),
        (450, 0.1),
        (400, 0.15),
        (350, 0.15),
        (300, 0.2)
    ]
    wave = np.concatenate([generate_square_wave(freq, dur) for freq, dur in notes])
    wave = (wave * 32767).astype(np.int16)
    stereo_wave = np.column_stack((wave, wave))
    return sndarray.make_sound(stereo_wave)

def generate_siren_sound():
    sample_rate = 44100
    duration = 0.2
    # Dynamic pitch modulation
    frequencies = [500, 600, 700, 800, 700, 600]
    wave = np.concatenate([generate_square_wave(freq, duration) for freq in frequencies])
    wave = (wave * 32767).astype(np.int16)
    stereo_wave = np.column_stack((wave, wave))
    return sndarray.make_sound(stereo_wave)

# Pacman class
class Pacman:
    def __init__(self):
        self.grid_x = 14
        self.grid_y = 23
        self.dir = 'NONE'
        self.next_dir = 'NONE'
        self.speed = 2
        self.pix_x = self.grid_x * TILE + TILE // 2
        self.pix_y = self.grid_y * TILE + TILE // 2
        self.radius = TILE // 2 - 2
        self.score = 0
        self.lives = 3

    def update(self):
        if self.next_dir != 'NONE':
            dx, dy = dirs[self.next_dir]
            new_x = self.grid_x + dx
            new_y = self.grid_y + dy
            if can_move(new_x, new_y):
                self.dir = self.next_dir

        dx, dy = dirs[self.dir]
        target_x = self.pix_x + dx * self.speed
        target_y = self.pix_y + dy * self.speed

        if dx != 0 or dy != 0:
            next_grid_x = (target_x - TILE // 2 + TILE // 2 * dx) // TILE
            next_grid_y = (target_y - TILE // 2 + TILE // 2 * dy) // TILE
            if can_move(next_grid_x, next_grid_y):
                self.pix_x = target_x
                self.pix_y = target_y
            else:
                self.pix_x = self.grid_x * TILE + TILE // 2
                self.pix_y = self.grid_y * TILE // 2
                self.dir = 'NONE'

        self.grid_x = int(self.pix_x // TILE)
        self.grid_y = int(self.pix_y // TILE)

        if maze[self.grid_y][self.grid_x] == 2:
            maze[self.grid_y][self.grid_x] = 0
            self.score += 10
            waka_sound.play()
        elif maze[self.grid_y][self.grid_x] == 3:
            maze[self.grid_y][self.grid_x] = 0
            self.score += 50
            global frightened_end_time, siren_sound
            frightened_end_time = pygame.time.get_ticks() + 7000
            siren_sound.stop()  # Pause siren during frightened mode
            power_pellet_sound.play()

    def draw(self):
        angle = math.radians(30)
        start_angle = angle + math.radians((pygame.time.get_ticks() // 100) % 2 * 30)
        end_angle = -angle - math.radians((pygame.time.get_ticks() // 100) % 2 * 30)
        pygame.draw.polygon(screen, YELLOW, [
            (self.pix_x, self.pix_y),
            (self.pix_x + math.cos(start_angle) * self.radius, self.pix_y - math.sin(start_angle) * self.radius),
            (self.pix_x + math.cos(end_angle) * self.radius, self.pix_y - math.sin(end_angle) * self.radius)
        ])
        pygame.draw.circle(screen, YELLOW, (self.pix_x, self.pix_y), self.radius)

# Ghost class
class Ghost:
    def __init__(self, grid_x, grid_y, color):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.pix_x = grid_x * TILE + TILE // 2
        self.pix_y = grid_y * TILE + TILE // 2
        self.dir = random.choice(['UP', 'DOWN', 'LEFT', 'RIGHT'])
        self.speed = 2
        self.color = color
        self.state = 'CHASE'
        self.scatter_target = {
            RED: (COLUMNS-1, 0),
            PINK: (0, 0),
            CYAN: (COLUMNS-1, ROWS-1),
            ORANGE: (0, ROWS-1)
        }[color]

    def get_chase_target(self):
        if self.color == RED:
            return (pacman.grid_x, pacman.grid_y)
        elif self.color == PINK:
            dx, dy = dirs[pacman.dir]
            target_x = pacman.grid_x + 4 * dx
            target_y = pacman.grid_y + 4 * dy
            target_x = max(0, min(COLUMNS-1, target_x))
            target_y = max(0, min(ROWS-1, target_y))
            return (target_x, target_y)
        elif self.color == CYAN:
            dx, dy = dirs[pacman.dir]
            ahead_x = pacman.grid_x + 2 * dx
            ahead_y = pacman.grid_y + 2 * dy
            blinky = None
            for g in ghosts:
                if g.color == RED:
                    blinky = g
                    break
            if blinky:
                bx, by = blinky.grid_x, blinky.grid_y
                vx, vy = ahead_x - bx, ahead_y - by
                target_x = bx + 2 * vx
                target_y = by + 2 * vy
                target_x = max(0, min(COLUMNS-1, target_x))
                target_y = max(0, min(ROWS-1, target_y))
                return (target_x, target_y)
            return (pacman.grid_x, pacman.grid_y)
        elif self.color == ORANGE:
            dist = math.hypot(self.grid_x - pacman.grid_x, self.grid_y - pacman.grid_y)
            if dist < 8:
                return self.scatter_target
            else:
                return (pacman.grid_x, pacman.grid_y)

    def update(self):
        global current_mode, frightened_end_time, siren_sound
        if self.state != 'EATEN':
            if pygame.time.get_ticks() < frightened_end_time:
                if self.state != 'FRIGHTENED':
                    self.state = 'FRIGHTENED'
            else:
                if self.state == 'FRIGHTENED':
                    siren_sound.play(loops=-1)  # Resume siren
                self.state = current_mode

        if self.state == 'FRIGHTENED':
            self.speed = 1
            target = (random.randint(0, COLUMNS-1), random.randint(0, ROWS-1))
        elif self.state == 'EATEN':
            self.speed = 4
            target = (14, 14)
        else:
            self.speed = 2
            if self.state == 'SCATTER':
                target = self.scatter_target
            else:
                target = self.get_chase_target()

        if self.pix_x % TILE == TILE // 2 and self.pix_y % TILE == TILE // 2:
            self.grid_x = self.pix_x // TILE
            self.grid_y = self.pix_y // TILE
            self.dir = self.choose_direction(target)

        dx, dy = dirs[self.dir]
        self.pix_x += dx * self.speed
        self.pix_y += dy * self.speed

        self.grid_x = int(self.pix_x // TILE)
        self.grid_y = int(self.pix_y // TILE)

        if self.state == 'EATEN' and (self.grid_x, self.grid_y) == (14, 14):
            self.state = current_mode

    def choose_direction(self, target):
        best_dir = 'NONE'
        min_dist = float('inf')
        for d in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
            if opposite_dir(d) == self.dir:
                continue
            dx, dy = dirs[d]
            nx = self.grid_x + dx
            ny = self.grid_y + dy
            if can_move(nx, ny):
                dist = (nx - target[0])**2 + (ny - target[1])**2
                if dist < min_dist:
                    min_dist = dist
                    best_dir = d
        return best_dir if best_dir != 'NONE' else opposite_dir(self.dir)

    def draw(self):
        rect = pygame.Rect(self.pix_x - TILE//2 + 2, self.pix_y - TILE//2 + 2, TILE-4, TILE-4)
        color = (100, 100, 255) if self.state == 'FRIGHTENED' else self.color
        pygame.draw.rect(screen, color, rect, border_radius=4)
        eye_offset = TILE // 8
        pygame.draw.circle(screen, WHITE, (self.pix_x - eye_offset, self.pix_y - eye_offset), TILE//10)
        pygame.draw.circle(screen, WHITE, (self.pix_x + eye_offset, self.pix_y - eye_offset), TILE//10)
        pygame.draw.circle(screen, BLUE, (self.pix_x - eye_offset, self.pix_y - eye_offset), TILE//20)
        pygame.draw.circle(screen, BLUE, (self.pix_x + eye_offset, self.pix_y - eye_offset), TILE//20)

# Utility functions
def can_move(x, y):
    return 0 <= x < COLUMNS and 0 <= y < ROWS and maze[y][x] != 1

def opposite_dir(d):
    return {'UP': 'DOWN', 'DOWN': 'UP', 'LEFT': 'RIGHT', 'RIGHT': 'LEFT', 'NONE': 'NONE'}[d]

# Game state
screen = pygame.display.set_mode((W, H))
running = True
current_mode = 'SCATTER'
pacman = None
ghosts = None
game_start_time = 0
frightened_end_time = 0
waka_sound = None
start_sound = None
power_pellet_sound = None
ghost_eaten_sound = None
death_sound = None
siren_sound = None

def setup():
    global pacman, ghosts, game_start_time, frightened_end_time, waka_sound, start_sound, power_pellet_sound, ghost_eaten_sound, death_sound, siren_sound
    pygame.init()
    pygame.display.set_caption("Pac-Man")
    pygame.mixer.stop()  # Stop any existing sounds
    waka_sound = generate_waka_sound()
    start_sound = generate_start_sound()
    power_pellet_sound = generate_power_pellet_sound()
    ghost_eaten_sound = generate_ghost_eaten_sound()
    death_sound = generate_death_sound()
    siren_sound = generate_siren_sound()
    start_sound.play()
    siren_sound.play(loops=-1)
    pacman = Pacman()
    ghosts = [Ghost(14, 11, RED), Ghost(13, 14, PINK), Ghost(14, 14, CYAN), Ghost(15, 14, ORANGE)]
    game_start_time = pygame.time.get_ticks()
    frightened_end_time = 0

def update_loop():
    global pacman, ghosts, game_start_time, frightened_end_time, running, current_mode

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                pacman.next_dir = 'UP'
            elif event.key == pygame.K_DOWN:
                pacman.next_dir = 'DOWN'
            elif event.key == pygame.K_LEFT:
                pacman.next_dir = 'LEFT'
            elif event.key == pygame.K_RIGHT:
                pacman.next_dir = 'RIGHT'

    elapsed_time = (pygame.time.get_ticks() - game_start_time) / 1000
    current_mode = 'SCATTER' if elapsed_time % 27 < 7 else 'CHASE'

    pacman.update()
    for ghost in ghosts:
        ghost.update()

    for ghost in ghosts:
        if abs(ghost.pix_x - pacman.pix_x) < TILE//2 and abs(ghost.pix_y - pacman.pix_y) < TILE//2:
            if ghost.state == 'FRIGHTENED':
                ghost.state = 'EATEN'
                pacman.score += 200
                ghost_eaten_sound.play()
            elif ghost.state in ['CHASE', 'SCATTER']:
                pacman.lives -= 1
                death_sound.play()
                siren_sound.stop()
                if pacman.lives > 0:
                    pacman = Pacman()
                    ghosts = [Ghost(14, 11, RED), Ghost(13, 14, PINK), Ghost(14, 14, CYAN), Ghost(15, 14, ORANGE)]
                    game_start_time = pygame.time.get_ticks()
                    frightened_end_time = 0
                    siren_sound.play(loops=-1)
                else:
                    # Display game over screen
                    screen.fill(BLACK)
                    font = pygame.font.SysFont('arial', 48)
                    game_over_surf = font.render("Game Over", True, WHITE)
                    score_surf = font.render(f"Final Score: {pacman.score}", True, WHITE)
                    screen.blit(game_over_surf, (W//2 - game_over_surf.get_width()//2, H//2 - 50))
                    screen.blit(score_surf, (W//2 - score_surf.get_width()//2, H//2 + 50))
                    pygame.display.flip()
                    pygame.time.wait(2000)  # Show game over for 2 seconds
                    running = False
                break

    screen.fill(BLACK)
    for y in range(ROWS):
        for x in range(COLUMNS):
            cell = maze[y][x]
            if cell == 1:
                pygame.draw.rect(screen, BLUE, (x*TILE, y*TILE, TILE, TILE))
            elif cell == 2:
                pygame.draw.circle(screen, WHITE, (x*TILE + TILE//2, y*TILE + TILE//2), 4)
            elif cell == 3:
                pygame.draw.circle(screen, WHITE, (x*TILE + TILE//2, y*TILE + TILE//2), 8)

    pacman.draw()
    for ghost in ghosts:
        ghost.draw()

    font = pygame.font.SysFont('arial', 24)
    score_surf = font.render(f"Score: {pacman.score}", True, WHITE)
    lives_surf = font.render(f"Lives: {pacman.lives}", True, WHITE)
    screen.blit(score_surf, (10, H - 30))
    screen.blit(lives_surf, (W - 120, H - 30))

    pygame.display.flip()

async def main():
    setup()
    global running
    while running:
        update_loop()
        await asyncio.sleep(1.0 / FPS)
    pygame.mixer.stop()  # Stop all sounds when game ends
    pygame.quit()

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
