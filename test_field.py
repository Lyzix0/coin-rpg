import sys
import pygame
from classes.Tiles import *
from classes.Sprites import *
from classes.GameObjects import Entity, Form, Direction, Player, Inventory
from classes.Weapons import Weapon

pygame.init()

clock = pygame.time.Clock()

running = True

screen_width = 800
screen_height = 600
tile_size = 64

screen = pygame.display.set_mode((screen_width, screen_height))

pygame.display.set_caption("Test field")

new_player = Player(size=50, animation_delay=200)
new_player.place((250, 200))
weapon = Weapon(10, 1, 10, 'images/bullet.png')
new_player.add_weapon(weapon)

idle_sprites = SpriteSheet('images/player/idle/idle_sprites.png', 4, 50)
run_sprites = SpriteSheet('images/player/Run/run_sprites.png', 6, 50)

new_player.set_sprites(idle_sprites.sprites)

level1 = TileMap()
level1.load_tilemap('images/tilesets/Dungeon_Tileset.png', rows=10, cols=10)

heal = level1.get_tile(9, 8)
heal.set_x(300)
heal.set_y(200)

level1.add_tile(heal)

level1_map = [
    ["grass", "dirt", "grass", "grass", "grass", "grass"],
    ["dirt", "dirt", "grass", "dirt", "grass", "grass"],
    ["grass", "grass", "dirt", "grass", "dirt", "grass"],
    ["grass", "dirt", "grass", "grass", "grass", "grass"],
]

walls = TileMap()
inventory = Inventory(screen)
for i in range(6):
    for j in range(5):
        tile = level1.get_tile(j, i)
        tile.set_x(i * 32 + 200)
        tile.set_y(j * 32 + 150)
        walls.add_tile(tile)

while running:
    screen.fill(pygame.color.Color(36, 20, 25))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # level1.draw_all_tiles(screen, 150, 30)
    # idle_sprites.draw_sprite(screen, 0)

    new_player.move(screen)

    if new_player.moving:
        new_player.set_sprites(run_sprites.sprites)
    else:
        new_player.set_sprites(idle_sprites.sprites)

    walls.draw_tiles(screen)

    level1.draw_tiles(screen)

    new_player.draw(screen)

    if pygame.mouse.get_pressed()[0]:
        new_player.make_shoot()

    new_player.draw_health_bar(screen)
    inventory.draw_inventory()
    clock.tick(60)
    pygame.display.flip()

pygame.quit()
sys.exit()
