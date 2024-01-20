import pygame
from scripts.Tiles import TileImages, TileMap, Tile
import sqlite3


def create_level(level_name: str):
    conn = sqlite3.connect('levels.db')

    cur = conn.cursor()
    cur.execute(f'DROP TABLE IF EXISTS {level_name}')

    table_creation_query = f'''
    CREATE TABLE {level_name} (
        image_path TEXT,
        row INTEGER,
        col INTEGER,
        x INTEGER,
        y INTEGER,
        width INTEGER,
        height INTEGER,
        reversed BOOLEAN,
        wall BOOLEAN
    );
    '''

    cur.execute(table_creation_query)

    conn.commit()
    conn.close()


pygame.init()

screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Simple Map Editor")

font = pygame.font.Font(None, 36)
text_wall = font.render("Тип тайла: обычный", True, 'black')
tile_wall = False

tile_images = TileImages()
tile_images.load_tile_images({
    "grass": "images/grass.png",
    "water": "images/dirt.jpg",
})

tile_size = 40

tile_map = TileMap()
tile_map.load_tilemap("images/tilesets/Dungeon_Tileset.png", rows=10, cols=10, tile_size=tile_size)

map_width, map_height = round(screen_width / tile_size), round(screen_height / tile_size)

level_map = []

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
                    new_tile.rect = pygame.Rect(tile_x * tile_size, tile_y * tile_size, tile_size, tile_size)
                    if tile_wall:
                        new_tile.wall = True

                    tile_map.add_tile(new_tile)
            elif event.button == 3:
                tile_x = event.pos[0] // tile_size
                tile_y = event.pos[1] // tile_size
                if 0 <= tile_x < map_width and 0 <= tile_y < map_height:
                    tile_map.current_tile_map = [tile for tile in tile_map.current_tile_map
                                                 if tile.x != tile_x * tile_size or tile.y != tile_y * tile_size]

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                current_tile_row = (current_tile_row - 1) % tile_map.rows
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                current_tile_row = (current_tile_row + 1) % tile_map.rows

            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                current_tile_col = (current_tile_col - 1) % tile_map.cols
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                current_tile_col = (current_tile_col + 1) % tile_map.cols

            if event.key == pygame.K_e:
                tile_wall = not tile_wall

            if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                level_name = 'level1'
                create_level(level_name)

                db = sqlite3.connect("levels.db")
                cursor = db.cursor()
                for tile in tile_map.current_tile_map:
                    rect = tile.rect.copy()

                    path = tile_map.path
                    row = tile.row
                    col = tile.col
                    x, y, width, height = rect.x, rect.y, rect.width, rect.height

                    query = f'INSERT INTO {level_name} (image_path, row, col, x, y, width, height, reversed, wall)' \
                            f' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'
                    values = (path, row, col, x, y, width, height, False, tile.wall)

                    cursor.execute(query, values)
                    db.commit()

            current_tile = tile_map.get_tile(current_tile_row, current_tile_col)

    screen.fill((255, 255, 255))
    tile_map.draw_tiles(screen, glow_walls=True)

    screen.blit(current_tile.image, pygame.mouse.get_pos())
    if tile_wall:
        text_wall = font.render("Тип тайла: стена", True, 'black')
    else:
        text_wall = font.render("Тип тайла: обычный", True, 'black')
    screen.blit(text_wall, (10, 10))
    pygame.display.flip()

pygame.quit()
