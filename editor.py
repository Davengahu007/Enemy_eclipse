"""provide a map editor for a game, allowing users to create, edit, and save game maps"""
import sys
import os
import json

import pygame

from scripts.utils import load_images
from scripts.tilemap import Tilemap

RENDER_SCALE = 2.0


class Editor:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('editor')
        self.screen = pygame.display.set_mode((640, 480))
        self.display = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()

        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'spawners': load_images('tiles/spawners'),
        }

        self.movement = [False, False, False, False]

        self.tilemap = Tilemap(self, tile_size=16)

        try:
            self.tilemap.load('map.json')
        except FileNotFoundError:
            pass

        self.scroll = [0, 0]

        self.tile_list = list(self.assets)
        self.tile_group = 0
        self.tile_variant = 0

        self.clicking = False
        self.right_clicking = False
        self.shift = False
        self.ongrid = True

        self.spawn_point = None

    def get_next_map_number(self):
        map_folder = 'data/maps'
        map_files = [f for f in os.listdir(map_folder) if f.endswith('.json')]
        return len(map_files)

    """Clears the current tilemap and sets a default spawn point."""
    def create_new_map(self):
        self.tilemap.clear()
        self.tilemap.autotile()
        self.spawn_point = (100, 100)

    """Loads a map from a file, handling missing files by creating a new map."""
    def load_map(self, map_number):
        map_file_path = f'data/maps/{map_number}.json'
        try:
            self.tilemap.load(map_file_path)
            with open(f'data/maps/{map_number}.json', 'r') as f:
                map_data = json.load(f)
            self.tilemap.tilemap = map_data['tilemap']
            self.tilemap.tile_size = map_data['tile_size']
            self.tilemap.offgrid_tiles = map_data['offgrid']
            self.spawn_point = map_data.get('spawn_point', None)
        except FileNotFoundError:
            print(f"Map {map_number} not found. Creating a new map.")
            self.create_new_map()

    """Saves the current map state to a file."""
    def save_map(self, map_number):
        map_file_path = f'data/maps/{map_number}.json'
        self.tilemap.save(map_file_path)
        map_data = {
            'tilemap': self.tilemap.tilemap,
            'tile_size': self.tilemap.tile_size,
            'offgrid': self.tilemap.offgrid_tiles,
            'spawn_point': self.spawn_point
        }
        with open(f'data/maps/{map_number}.json', 'w') as f:
            json.dump(map_data, f)
        print(f"Map {map_number} saved.")

    """loads and displays maps, processes user inputs for map editing, and updates the display at a 60 FPS rate. """
    def run(self):
        map_number = self.get_next_map_number()
        self.load_map(map_number)

        while True:
            self.display.fill((0, 0, 0))

            self.scroll[0] += (self.movement[1] - self.movement[0]) * 2
            self.scroll[1] += (self.movement[3] - self.movement[2]) * 2
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            self.tilemap.render(self.display, offset=render_scroll)

            current_tile_img = self.assets[self.tile_list[self.tile_group]][self.tile_variant].copy()
            current_tile_img.set_alpha(255)

            mpos = pygame.mouse.get_pos()
            mpos = (mpos[0] / RENDER_SCALE, mpos[1] / RENDER_SCALE)
            tile_pos = (int((mpos[0] + self.scroll[0]) // self.tilemap.tile_size),
                        int((mpos[1] + self.scroll[1]) // self.tilemap.tile_size))

            if self.ongrid:
                self.display.blit(current_tile_img, (tile_pos[0] * self.tilemap.tile_size - self.scroll[0],
                                                     tile_pos[1] * self.tilemap.tile_size - self.scroll[1]))
            else:
                self.display.blit(current_tile_img, mpos)

            if self.clicking and self.ongrid:
                self.tilemap.tilemap[str(tile_pos[0]) + ';' + str(tile_pos[1])] = {
                    'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'pos': tile_pos}
            if self.right_clicking:
                tile_loc = str(tile_pos[0]) + ';' + str(tile_pos[1])
                if tile_loc in self.tilemap.tilemap:
                    del self.tilemap.tilemap[tile_loc]
                for tile in self.tilemap.offgrid_tiles.copy():
                    tile_img = self.assets[tile['type']][tile['variant']]
                    tile_r = pygame.Rect(tile['pos'][0] - self.scroll[0], tile['pos'][1] - self.scroll[1],
                                         tile_img.get_width(), tile_img.get_height())
                    if tile_r.collidepoint(mpos):
                        self.tilemap.offgrid_tiles.remove(tile)

            self.display.blit(current_tile_img, (5, 5))

            """event handling user inputs:quitting, editing tiles, selecting tile types, navigating the map editor."""
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.clicking = True
                        if not self.ongrid:
                            self.tilemap.offgrid_tiles.append(
                                {'type': self.tile_list[self.tile_group], 'variant': self.tile_variant,
                                 'pos': (mpos[0] + self.scroll[0], mpos[1] + self.scroll[1])})
                    if event.button == 3:
                        self.right_clicking = True
                    if self.shift:
                        if event.button == 4:
                            self.tile_variant = (self.tile_variant - 1) % len(
                                self.assets[self.tile_list[self.tile_group]])
                        if event.button == 5:
                            self.tile_variant = (self.tile_variant + 1) % len(
                                self.assets[self.tile_list[self.tile_group]])
                    else:
                        if event.button == 4:
                            self.tile_group = (self.tile_group - 1) % len(self.tile_list)
                            self.tile_variant = 0
                        if event.button == 5:
                            self.tile_group = (self.tile_group + 1) % len(self.tile_list)
                            self.tile_variant = 0

                """ Separate handling for touchpad events"""
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 4:
                    self.tile_variant = (self.tile_variant - 1) % len(
                        self.assets[self.tile_list[self.tile_group]])
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 5:
                    self.tile_variant = (self.tile_variant + 1) % len(
                        self.assets[self.tile_list[self.tile_group]])

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.clicking = False
                    if event.button == 3:
                        self.right_clicking = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_w:
                        self.movement[2] = True
                    if event.key == pygame.K_s:
                        self.movement[3] = True
                    if event.key == pygame.K_g:
                        self.ongrid = not self.ongrid
                    if event.key == pygame.K_t:
                        self.tilemap.autotile()
                    if event.key == pygame.K_n:
                        map_number = self.get_next_map_number()
                        self.create_new_map()
                    if event.key == pygame.K_o:
                        self.save_map(map_number)
                    if event.key == pygame.K_p:
                        self.spawn_point = tile_pos
                        print(f"Spawn point set to {self.spawn_point}")
                    if event.key == pygame.K_LSHIFT:
                        self.shift = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_d:
                        self.movement[1] = False
                    if event.key == pygame.K_w:
                        self.movement[2] = False
                    if event.key == pygame.K_s:
                        self.movement[3] = False
                    if event.key == pygame.K_LSHIFT:
                        self.shift = False

            if self.spawn_point:
                """Optionally, render a visual indicator for the spawn point"""
                spawn_indicator = pygame.Surface((self.tilemap.tile_size, self.tilemap.tile_size))
                spawn_indicator.fill((0, 255, 0))
                self.display.blit(spawn_indicator, (self.spawn_point[0] * self.tilemap.tile_size - self.scroll[0],
                                                    self.spawn_point[1] * self.tilemap.tile_size - self.scroll[1]))

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)


Editor().run()