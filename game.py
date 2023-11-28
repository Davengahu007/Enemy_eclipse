import os
import sys
import math
import random

import pygame

from scripts.utils import load_image, load_images, Animation
from scripts.entities import Player, Enemy
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.particle import Particle
from scripts.spark import Spark
from menu import Menu


class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('enemy eclipse')
        self.screen = pygame.display.set_mode((640, 480))
        self.display = pygame.Surface((320, 240), pygame.SRCALPHA)
        self.display_2 = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()

        self.movement = [False, False]

        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'player': load_image('entities/player.png'),
            'background': load_image('background.png'),
            'clouds': load_images('clouds'),
            'enemy/idle': Animation(load_images('entities/enemy/idle'), img_dur=6),
            'enemy/run': Animation(load_images('entities/enemy/run'), img_dur=4),
            'player/idle': Animation(load_images('entities/player/idle'), img_dur=6),
            'player/run': Animation(load_images('entities/player/run'), img_dur=4),
            'player/jump': Animation(load_images('entities/player/jump')),
            'player/slide': Animation(load_images('entities/player/slide')),
            'player/wall_slide': Animation(load_images('entities/player/wall_slide')),
            'particle/leaf': Animation(load_images('particles/leaf'), img_dur=20, loop=False),
            'particle/particle': Animation(load_images('particles/particle'), img_dur=6, loop=False),
            'gun': load_image('gun.png'),
            'projectile': load_image('projectile.png'),
        }

        self.sfx = {
            'jump': pygame.mixer.Sound('data/sfx/jump.wav'),
            'dash': pygame.mixer.Sound('data/sfx/dash.wav'),
            'hit': pygame.mixer.Sound('data/sfx/hit.wav'),
            'shoot': pygame.mixer.Sound('data/sfx/shoot.wav'),
            'ambience': pygame.mixer.Sound('data/sfx/ambience.wav'),
        }

        self.sfx['ambience'].set_volume(0.2)
        self.sfx['shoot'].set_volume(0.4)
        self.sfx['hit'].set_volume(0.8)
        self.sfx['dash'].set_volume(0.3)
        self.sfx['jump'].set_volume(0.7)

        self.clouds = Clouds(self.assets['clouds'], count=16)

        self.player = Player(self, (50, 50), (8, 15))

        self.tilemap = Tilemap(self, tile_size=16)

        self.menu = Menu(self.screen)

        self.level = 0
        self.lives = 3
        self.lives_font = pygame.font.Font(None, 24)
        self.load_level(self.level)

        self.screenshake = 0
        self.level_indicator_shown = False
        self.in_menu = True
        self.show_level_loading = False

    def load_level(self, map_id):
        self.show_level_indicator(self.level)  # Moved from run() to load_level()

        self.tilemap.load('data/maps/' + str(map_id) + '.json')

        self.leaf_spawners = []
        for tree in self.tilemap.extract([('large_decor', 2)], keep=True):
            self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))

        self.enemies = []
        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1)]):
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']
                self.player.air_time = 0
            else:
                self.enemies.append(Enemy(self, spawner['pos'], (8, 15)))

        self.projectiles = []
        self.particles = []
        self.sparks = []

        self.scroll = [0, 0]
        self.dead = 0
        self.transition = -30

    def show_level_indicator(self, level):
        indicator_font = pygame.font.Font(None, 36)
        indicator_text = f"Level {level + 1} loading ..."

        white = (255, 255, 255)
        text_surface = indicator_font.render(indicator_text, True, white)
        text_rect = text_surface.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))

        background = pygame.Surface(self.screen.get_size())
        background.fill((0, 0, 0))
        background.blit(text_surface, text_rect)
        self.screen.blit(background, (0, 0))
        pygame.display.flip()
        self.show_level_loading = True

        start_time = pygame.time.get_ticks()
        while pygame.time.get_ticks() - start_time < 500:
            pygame.event.pump()

    def run_level_indicator(self):
        # Reset the transition and dead states
        self.transition = 0
        self.dead = 0

        # Check if the level loading indicator should be shown
        if self.show_level_loading:
            indicator_font = pygame.font.Font(None, 36)
            indicator_text = f"Level {self.level + 1} loading ..."

            white = (255, 255, 255)
            text_surface = indicator_font.render(indicator_text, True, white)
            text_rect = text_surface.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))

            background = pygame.Surface(self.screen.get_size())
            background.fill((0, 0, 0))
            background.blit(text_surface, text_rect)
            self.screen.blit(background, (0, 0))
            pygame.display.flip()

            start_time = pygame.time.get_ticks()
            while pygame.time.get_ticks() - start_time < 500:
                pygame.event.pump()

            # Reset the flag after showing the indicator
            self.show_level_loading = False

        # Load the level
        self.load_level(self.level)

    def show_death_indicator(self):
        indicator_font = pygame.font.Font(None, 36)
        indicator_text = "You died!"

        red = (255, 0, 0)
        text_surface = indicator_font.render(indicator_text, True, red)
        text_rect = text_surface.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))

        background = pygame.Surface(self.screen.get_size())
        background.fill((0, 0, 0))
        background.blit(text_surface, text_rect)
        self.screen.blit(background, (0, 0))
        pygame.display.flip()

        start_time = pygame.time.get_ticks()
        while pygame.time.get_ticks() - start_time < 1000:
            pygame.event.pump()

    def update_high_score(self):
        if self.level > self.menu.high_score:
            self.menu.high_score = self.level

    def run(self):
        pygame.mixer.music.load('data/music.wav')
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        heart_font = pygame.font.SysFont('segoeuisymbol', 20)
        heart_emoji = '❤️'

        self.sfx['ambience'].play(-1)

        # Initially show the menu
        self.in_menu = True


        while True:
            if self.in_menu:
                self.menu.display()
                if self.menu.handle_input():
                    self.in_menu = False
                    self.level = 0  # Reset the level when starting a new game
                    self.run_level_indicator()  # Show level loading screen
            else:
                self.display.fill((0, 0, 0, 0))
                self.display_2.blit(self.assets['background'], (0, 0))
                self.screenshake = max(0, self.screenshake - 1)

                if not len(self.enemies):
                    self.transition += 1
                    if self.transition > 30:
                        self.level = min(self.level + 1, len(os.listdir('data/maps')) - 1)
                        self.run_level_indicator()

                if self.transition < 0:
                    self.transition += 1

                if self.dead:
                    self.dead += 1
                    if self.dead >= 10:
                        self.transition = min(30, self.transition + 1)
                    if self.dead > 40:
                        self.show_death_indicator()
                        self.lives -= 1  # Decrease a life
                        if self.lives > 0:
                            self.load_level(self.level)  # Respawn in current level
                        else:
                            self.lives = 3  # Reset lives
                            self.level = 0  # Start from first level
                            self.load_level(self.level)  # Respawn in first level

                self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30
                self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 30
                render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

                for rect in self.leaf_spawners:
                    if random.random() * 49999 < rect.width * rect.height:
                        pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                        self.particles.append(
                            Particle(self, 'leaf', pos, velocity=[-0.1, 0.3], frame=random.randint(0, 20)))

                self.clouds.update()
                self.clouds.render(self.display_2, offset=render_scroll)

                self.tilemap.render(self.display, offset=render_scroll)

                for enemy in self.enemies.copy():
                    kill = enemy.update(self.tilemap, (0, 0))
                    enemy.render(self.display, offset=render_scroll)
                    if kill:
                        self.enemies.remove(enemy)

                if not self.dead:
                    self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
                    self.player.render(self.display, offset=render_scroll)

                # [[x, y], direction, timer]
                for projectile in self.projectiles.copy():
                    projectile[0][0] += projectile[1]
                    projectile[2] += 1
                    img = self.assets['projectile']
                    self.display.blit(img, (projectile[0][0] - img.get_width() / 2 - render_scroll[0],
                                            projectile[0][1] - img.get_height() / 2 - render_scroll[1]))
                    if self.tilemap.solid_check(projectile[0]):
                        self.projectiles.remove(projectile)
                        for i in range(4):
                            self.sparks.append(
                                Spark(projectile[0], random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0),
                                      2 + random.random()))
                    elif projectile[2] > 360:
                        self.projectiles.remove(projectile)
                    elif abs(self.player.dashing) < 50:
                        if self.player.rect().collidepoint(projectile[0]):
                            self.projectiles.remove(projectile)
                            self.dead += 1
                            self.sfx['hit'].play()
                            self.screenshake = max(16, self.screenshake)
                            for i in range(30):
                                angle = random.random() * math.pi * 2
                                speed = random.random() * 5
                                self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random()))
                                self.particles.append(Particle(self, 'particle', self.player.rect().center,
                                                               velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                         math.sin(angle + math.pi) * speed * 0.5],
                                                               frame=random.randint(0, 7)))

                for spark in self.sparks.copy():
                    kill = spark.update()
                    spark.render(self.display, offset=render_scroll)
                    if kill:
                        self.sparks.remove(spark)

                display_mask = pygame.mask.from_surface(self.display)
                display_sillhouette = display_mask.to_surface(setcolor=(0, 0, 0, 180), unsetcolor=(0, 0, 0, 0))
                for offset in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    self.display_2.blit(display_sillhouette, offset)

                for particle in self.particles.copy():
                    kill = particle.update()
                    particle.render(self.display, offset=render_scroll)
                    if particle.type == 'leaf':
                        particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
                    if kill:
                        self.particles.remove(particle)

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LEFT:
                            self.movement[0] = True
                        if event.key == pygame.K_RIGHT:
                            self.movement[1] = True
                        if event.key == pygame.K_UP:
                            if self.player.jump():
                                self.sfx['jump'].play()
                        if event.key == pygame.K_x:
                            self.player.dash()
                    if event.type == pygame.KEYUP:
                        if event.key == pygame.K_LEFT:
                            self.movement[0] = False
                        if event.key == pygame.K_RIGHT:
                            self.movement[1] = False

                if self.transition:
                    transition_surf = pygame.Surface(self.display.get_size())
                    pygame.draw.circle(transition_surf, (255, 255, 255),
                                       (self.display.get_width() // 2, self.display.get_height() // 2),
                                       (30 - abs(self.transition)) * 8)
                    transition_surf.set_colorkey((255, 255, 255))
                    self.display.blit(transition_surf, (0, 0))

                    # Draw the lives text after all game updates but before blitting to self.display_2
                for i in range(self.lives):
                    heart_surface = heart_font.render(heart_emoji, True, (255, 0, 0))  # Render the heart emoji
                    self.display.blit(heart_surface, (10 + i * (heart_surface.get_width() + 5), 10))

                # Blit self.display onto self.display_2
                self.display_2.blit(self.display, (0, 0))

                # Final blit operations to self.screen with screenshake effect
                screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2,
                                      random.random() * self.screenshake - self.screenshake / 2)
                self.screen.blit(pygame.transform.scale(self.display_2, self.screen.get_size()), screenshake_offset)

                # Update the display and tick the clock
                pygame.display.update()
                self.clock.tick(60)
                self.update_high_score()


Game().run()
