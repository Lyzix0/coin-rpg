import pygame
from scripts.Tiles import TileImages, TileMap, Tile
import sqlite3

pygame.init()

screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Simple Map Editor")


tile_images = TileImages()
tile_images.load_tile_images({
    "grass": "images/grass.png",
    "water": "images/dirt.jpg",
})

tile_map = TileMap()
tile_map.load_tilemap("images/tilesets/Dungeon_Tileset.png", rows=10, cols=10, tile_size=32)


map_width, map_height = 20, 15
tile_size = 32


level_map = [["" for _ in range(map_width)] for _ in range(map_height)]

running = True
current_tile_row = 0
current_tile_col = 0
current_tile = tile_map.get_tile(current_tile_row, current_tile_col)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                tile_x = event.pos[0] // tile_size
                tile_y = event.pos[1] // tile_size
                if 0 <= tile_x < map_width and 0 <= tile_y < map_height:
                    new_tile = tile_map.get_tile(current_tile_row, current_tile_col)
                    new_tile.rect = pygame.Rect(tile_x * tile_size, tile_y * tile_size, 32, 32)
                    tile_map.add_tile(new_tile)
                    level_map[tile_y][tile_x] = new_tile
            elif event.button == 3:
                tile_x = event.pos[0] // tile_size
                tile_y = event.pos[1] // tile_size
                if 0 <= tile_x < map_width and 0 <= tile_y < map_height:
                    tile_map.current_tile_map = [tile for tile in tile_map.current_tile_map
                                                 if tile.x != tile_x * tile_size or tile.y != tile_y * tile_size]
                    level_map[tile_y][tile_x] = ""

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                current_tile_row = (current_tile_row - 1) % tile_map.rows
            elif event.key == pygame.K_DOWN:
                current_tile_row = (current_tile_row + 1) % tile_map.rows

            if event.key == pygame.K_LEFT:
                current_tile_col = (current_tile_col - 1) % tile_map.cols
            elif event.key == pygame.K_RIGHT:
                current_tile_col = (current_tile_col + 1) % tile_map.cols

            if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                db = sqlite3.connect("levels.db")
                cursor = db.cursor()
                for row in level_map:
                    for item in row:
                        if isinstance(item, Tile):
                            r = item.rect.copy()

                            path = tile_map.path
                            row = item.row
                            col = item.col
                            x, y, width, height = r.x, r.y, r.width, r.height
                            cursor.execute(f'INSERT INTO level1 VALUES ({path}, {row}, {col}, {x}, {y}, {width}, {height})')

                            db.commit()

            current_tile = tile_map.get_tile(current_tile_row, current_tile_col)

    screen.fill((255, 255, 255))
    tile_map.draw_all_tiles(screen)
    tile_map.draw_tiles(screen)

    screen.blit(current_tile.image, pygame.mouse.get_pos())

    pygame.display.flip()

pygame.quit()
