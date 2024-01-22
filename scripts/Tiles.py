from __future__ import annotations

import sqlite3
import time
import pygame
from scripts.Base import load_image
from scripts.Sprites import SpriteSheet


class Tile(pygame.sprite.Sprite):
    def __init__(self, surface: pygame.Surface, x: int | float = 0, y: int | float = 0, row: int = 0, col: int = 0,
                 wall: bool = False):
        pygame.sprite.Sprite.__init__(self)
        self.image = surface
        self.col = col
        self.row = row
        self.wall = wall
        self.rect = pygame.Rect(x, y, surface.get_width(), surface.get_height())

    def set_x(self, new_x):
        self.rect.x = new_x

    def set_y(self, new_y):
        self.rect.y = new_y

    @property
    def x(self):
        return self.rect.x

    @property
    def y(self):
        return self.rect.y


class Trap(Tile):
    def __init__(self, surface: pygame.Surface, x: int | float = 0, y: int | float = 0, row: int = 0, col: int = 0,
                 cooldown_time: int = 1):
        super().__init__(surface, x, y, row, col)

        self.duration = 1000
        self.power = 10
        self.alive = True
        self.cooldown_time = cooldown_time
        self.last_activation_time = 0
        self.effect = 'damage'

        self.last_image_change_time = 0
        self.sprites = None
        self.current_image_index = 0

    def handle_collision(self, player):
        current_time = time.time()

        if self.alive and current_time - self.last_activation_time > self.cooldown_time:
            if self.rect.colliderect(player.rect):
                if self.effect == "damage":
                    player.take_damage(self.power)
                elif self.effect == "poison":
                    player.apply_poison_effect(duration=self.duration)

                self.last_activation_time = current_time

    def change_image(self):
        if not self.sprites:
            return

        current_time = time.time()

        if current_time - self.last_image_change_time > 1:
            self.current_image_index = (self.current_image_index + 1) % len(self.sprites.sprites)
            self.image = self.sprites.sprites[self.current_image_index]
            self.last_image_change_time = current_time


class TileImages:
    def __init__(self, tile_size: int = 32):
        self.tile_size = tile_size
        self.tile_images = None

    def load_tile_images(self, tile_paths=None):
        self.tile_images = tile_paths

        for tile_name, tile_path in self.tile_images.items():
            try:
                image = pygame.transform.scale(load_image(tile_path), (self.tile_size, self.tile_size))
                self.tile_images[tile_name] = image
            except pygame.error as e:
                print(f"Не удалось загрузить изображение '{tile_path}': {e}")

    def draw_images(self, screen, map_data):
        if not self.tile_images:
            return

        for y, row in enumerate(map_data):
            for x, tile_type in enumerate(row):
                screen.blit(self.tile_images[tile_type], (x * self.tile_size, y * self.tile_size))


class TileMap:
    def __init__(self):
        self.path = None
        self.rows = 0
        self.cols = 0
        self.tile_map_surface = None
        self.current_tile_map = []
        self.tile_size = 0

    def draw_all_tiles(self, screen, x_offset: int | float = 0, y_offset: int | float = 0):
        if self.tile_map_surface is None:
            raise TypeError("Нельзя отрисовать пустой tilemap!")

        for row in self.tile_map_surface:
            temp_x_offset = x_offset
            for sprite in row:
                if sprite:
                    screen.blit(sprite, (temp_x_offset, y_offset))
                temp_x_offset += self.tile_size
            y_offset += self.tile_size

    def draw_tiles(self, screen, glow_walls=False):
        for tile in self.current_tile_map:
            if tile.__class__.__name__ == "Trap":
                tile.change_image()
            screen.blit(tile.image, tile.rect)
            if glow_walls and tile.wall:
                pygame.draw.rect(screen, color='green', rect=tile.rect, width=1)

    def get_tile(self, row, col):
        new_tile = Tile(self.tile_map_surface[row][col], row=row, col=col)
        return new_tile

    def add_tile(self, tile: Tile):
        self.current_tile_map.append(tile)

    def load_level(self, level_name):
        db = sqlite3.connect('levels.db')
        cur = db.cursor()

        tiles = cur.execute(f'SELECT * FROM {level_name}').fetchall()

        for tile in tiles:
            path = tile[0]
            if path == self.path:
                new_tile = self.get_tile(tile[1], tile[2])
                new_tile.rect = pygame.Rect(tile[3], tile[4], tile[5], tile[6])
                new_tile.wall = tile[8]
                self.current_tile_map.append(new_tile)

    def load_tilemap(self, path, rows=1, cols=1, tile_size=32):
        """
        Загружает и нарезает спрайт-лист на отдельные кадры (спрайты).

        Args:
            path: Путь к файлу спрайт-листа.
            rows: Количество рядов спрайтов в спрайт-листе.
            cols: Количество столбцов спрайтов в спрайт-листе.
            tile_size: размер тайла в пикселях

        Returns:
            Список Pygame Surface, каждый из которых является отдельным спрайтом.
        """
        self.cols = cols
        self.rows = rows
        self.tile_size = tile_size
        self.path = path
        spritesheet = load_image(path)
        new_width = self.tile_size / (spritesheet.get_width() / rows) * spritesheet.get_width()
        new_height = self.tile_size / (spritesheet.get_height() / cols) * spritesheet.get_height()

        spritesheet = pygame.transform.scale(spritesheet, (new_width, new_height))

        sprites = []
        for row in range(rows):
            temp = []
            for col in range(cols):
                x = col * self.tile_size
                y = row * self.tile_size
                rect = pygame.Rect(x, y, self.tile_size, self.tile_size)
                sprite = spritesheet.subsurface(rect)

                temp.append(sprite)

            sprites.append(temp)

        self.tile_map_surface = sprites