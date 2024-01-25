import pygame


from scripts.Sprites import SpriteSheet
from scripts.Tiles import TileImages, TileMap, Tile, Trap, Enemy
import sqlite3


def create_level(db_name: str):
    conn = sqlite3.connect(db_name)

    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS tiles (
            image_path TEXT,
            row INTEGER,
            col INTEGER,
            x INTEGER,
            y INTEGER,
            width INTEGER,
            height INTEGER,
            rotated BOOLEAN,
            wall BOOLEAN
        );
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS traps (
            image_path TEXT,
            cols INTEGER,
            x INTEGER,
            y INTEGER,
            width INTEGER,
            height INTEGER,
            sprites_damage TEXT
        );
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS enemies (
            image_path TEXT,
            cols INTEGER,
            x INTEGER,
            y INTEGER,
            width INTEGER,
            height INTEGER
        );
    ''')

    conn.commit()
    conn.close()


def save_tiles(tile_map):
    create_level(level_path)

    db = sqlite3.connect(level_path)
    cursor = db.cursor()

    cursor.execute('DELETE FROM tiles')

    for tile in tile_map.current_tile_map:
        rect = tile.rect.copy()

        path = tile_map.path
        row = tile.row
        col = tile.col
        x, y, width, height = rect.x, rect.y, rect.width, rect.height

        query = f'INSERT INTO tiles (image_path, row, col, x, y, width, height, rotated, wall)' \
                f' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'
        values = (path, row, col, x, y, width, height, tile.rotated, tile.wall)

        cursor.execute(query, values)
        db.commit()


def save_traps(tile_map, path='images/peaks/peaks.png', sprites_damage: [bool] = None):
    if sprites_damage is None:
        sprites_damage = [True, True, False, False]

    create_level(level_path)

    db = sqlite3.connect(level_path)
    cursor = db.cursor()

    cursor.execute('DELETE FROM traps')
    for tile in tile_map.current_tile_map:
        if not isinstance(tile, Trap):
            continue

        rect = tile.rect.copy()

        x, y, width, height = rect.x, rect.y, rect.width, rect.height
        cols = len(tile.sprites.sprites)

        query = f'INSERT INTO traps (image_path, cols, x, y, width, height, sprites_damage)' \
                f' VALUES (?, ?, ?, ?, ?, ?, ?)'
        values = (path, cols, x, y, width, height, " ".join(map(str, sprites_damage)))

        cursor.execute(query, values)
        db.commit()


def save_enemies():
    create_level(level_path)

    db = sqlite3.connect(level_path)
    cursor = db.cursor()

    cursor.execute('DELETE FROM enemies')

    for current_enemy in enemies:
        rect = current_enemy.rect.copy()

        x, y, width, height = rect.x, rect.y, rect.width, rect.height

        query = f'INSERT INTO enemies (image_path, cols, x, y, width, height)' \
                f' VALUES (?, ?, ?, ?, ?, ?)'
        values = (current_enemy.name, 4, x, y, width, height)

        cursor.execute(query, values)
        db.commit()


def place_enemy(image_path: str, cols: int = 4, colorkey=None, enemy_name: str = 'enemy'):
    mouse_position = pygame.mouse.get_pos()
    new_enemy = Enemy(40, 100, name=enemy_name)
    new_enemy.set_sprites(SpriteSheet(image_path, cols, 40, colorkey).sprites)
    new_enemy.place(pygame.Vector2(mouse_position[0], mouse_position[1]))
    enemies.append(new_enemy)



pygame.init()

screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Simple Map Editor")

font = pygame.font.Font(None, 36)
text_wall = font.render("Тип тайла: обычный", True, 'black')
level_path = 'all_levels/level2.db'
tile_wall = False

tile_images = TileImages()
tile_images.load_tile_images({
    "grass": "images/tilesets/grass.png",
    "water": "images/tilesets/dirt.jpg",
})

tile_size = 40

tile_map = TileMap()
tile_map.load_tilemap("images/tilesets/Dungeon_Tileset.png", rows=10, cols=10, tile_size=tile_size)

map_width, map_height = round(screen_width / tile_size), round(screen_height / tile_size)

level_map = []
enemies = []

running = True
current_tile_row = 0
current_tile_col = 0
current_tile = tile_map.get_tile(current_tile_row, current_tile_col)
rotated = False

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
                    new_tile.rotate(rotated)

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
            match event.key:
                case pygame.K_w:
                    current_tile_row = (current_tile_row - 1) % tile_map.rows
                case pygame.K_s:
                    current_tile_row = (current_tile_row + 1) % tile_map.rows
                case pygame.K_a:
                    current_tile_col = (current_tile_col - 1) % tile_map.cols
                case pygame.K_d:
                    current_tile_col = (current_tile_col + 1) % tile_map.cols

            if event.key == pygame.K_e:
                tile_wall = not tile_wall

            if event.key == pygame.K_r:
                rotated = not rotated
                current_tile.rotate(rotated)

            if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                create_level(level_path)
                save_tiles(tile_map)
                save_traps(tile_map)
                save_enemies()

            current_tile = tile_map.get_tile(current_tile_row, current_tile_col)

            if event.key == pygame.K_t:
                mouse_pos = pygame.mouse.get_pos()
                tile_x = mouse_pos[0] // tile_size
                tile_y = mouse_pos[1] // tile_size
                if 0 <= tile_x < map_width and 0 <= tile_y < map_height:
                    new_tile = Trap(surface=pygame.image.load('images/peaks/peaks.png'))
                    new_tile.sprites = SpriteSheet('images/peaks/peaks.png', 4, tile_size)

                    new_tile.rect = pygame.Rect(tile_x * tile_size, tile_y * tile_size, tile_size, tile_size)
                    new_tile.rotate(rotated)

                    if tile_wall:
                        new_tile.wall = True

                    tile_map.add_tile(new_tile)

            if event.key == pygame.K_1:
                place_enemy('images/enemies/enemy.png', 4, 'white', enemy_name='enemy1')
            elif event.key == pygame.K_2:
                place_enemy('images/enemies/enemy2.png', 4, 'white', enemy_name='enemy2')

    screen.fill((255, 255, 255))
    tile_map.draw_tiles(screen, glow_walls=True)

    rotated_tile_image = pygame.transform.flip(current_tile.image, rotated, False)

    screen.blit(rotated_tile_image, pygame.mouse.get_pos())

    for enemy in enemies:
        enemy.draw(screen)

    if tile_wall:
        text_wall = font.render("Тип тайла: стена", True, 'black')
    else:
        text_wall = font.render("Тип тайла: обычный", True, 'black')
    screen.blit(text_wall, (10, 10))
    pygame.display.flip()

pygame.quit()
