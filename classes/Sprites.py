import pygame
from classes.Base import load_image


class SpriteSheet:
    def __init__(self, image_path: str, cols: int = 1, tile_size: int = 32, colorkey=None):
        self.sprites: [pygame.sprite.Sprite] = []

        spritesheet = load_image(image_path, colorkey)

        spritesheet = pygame.transform.scale(spritesheet, (tile_size * cols, tile_size))

        y = 0

        for col in range(cols):
            x = col * tile_size
            rect = pygame.Rect(x, y, tile_size, tile_size)
            sprite = spritesheet.subsurface(rect)

            self.sprites.append(sprite)

    def draw_sprite(self, screen: pygame.Surface, sprite_number: int):
        screen.blit(self.sprites[sprite_number], self.sprites[sprite_number].get_rect())
