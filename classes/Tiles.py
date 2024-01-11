from typing import overload

import pygame
from pygame import Surface

from classes.Base import load_image


class Tile(pygame.sprite.Sprite):
    def __init__(self, surface: pygame.Surface, x: int | float = 0, y: int | float = 0):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y

        self.image = surface
        self.rect = self.image.get_rect()


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
    def __init__(self, tile_size: int = 32, path: str = None, rows=1, cols=1):
        self._tile_map_surface = None
        self._current_tile_map = []
        self.tile_size = tile_size

        self._load_tilemap(path, rows, cols)

    def draw_all_tiles(self, screen, x_offset: int | float = 0, y_offset: int | float = 0):
        if self._tile_map_surface is None:
            raise TypeError("Нельзя отрисовать пустой tilemap!")

        for row in self._tile_map_surface:
            temp_x_offset = x_offset
            for sprite in row:
                if sprite:
                    screen.blit(sprite, (temp_x_offset, y_offset))
                temp_x_offset += self.tile_size
            y_offset += self.tile_size

    def draw_tiles(self, screen):
        for tile in self._current_tile_map:
            screen.blit(tile.image, tile.rect)

    def get_tile(self, row, col):
        new_tile = Tile(self._tile_map_surface[row][col])
        return new_tile

    def add_tile(self, tile: Tile):
        self._current_tile_map.append(tile)

    def _load_tilemap(self, path, rows=1, cols=1):
        """
        Загружает и нарезает спрайт-лист на отдельные кадры (спрайты).

        Args:
            path: Путь к файлу спрайт-листа.
            rows: Количество рядов спрайтов в спрайт-листе.
            cols: Количество столбцов спрайтов в спрайт-листе.

        Returns:
            Список Pygame Surface, каждый из которых является отдельным спрайтом.
        """
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

        self._tile_map_surface = sprites





