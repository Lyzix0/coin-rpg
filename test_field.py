import sys
import pygame
from classes.Tiles import *
from classes.Sprites import *
from classes.GameObjects import Entity, Form, Direction, Player
from classes.Weapons import Weapon

pygame.init()

clock = pygame.time.Clock()

running = True

screen_width = 800
screen_height = 600
tile_size = 64

screen = pygame.display.set_mode((screen_width, screen_height))

pygame.display.set_caption("Test field")

new_player = Player(size=50)
new_player.place((200, 250))
weapon = Weapon(10, 1, 10, 'images/bullet.png')
new_player.add_weapon(weapon)

level1 = TileMap(50, 'images/tilesets/Dungeon_Tileset.png', rows=10, cols=10)

heal = level1.get_tile(9, 8)
level1.add_tile(heal)

level1_map = [
    ["grass", "dirt", "grass", "grass", "grass", "grass"],
    ["dirt", "dirt", "grass", "dirt", "grass", "grass"],
    ["grass", "grass", "dirt", "grass", "dirt", "grass"],
    ["grass", "dirt", "grass", "grass", "grass", "grass"],
]

idle_sprites = SpriteSheet('images/player/idle/idle_sprites.png', 4, 50, 'white')

current_sprite = 0
last_update_time = 0
animation_delay = 250

while running:
    screen.fill('black')

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # level1.draw_all_tiles(screen, 150, 30)
    level1.draw_tiles(screen)
    idle_sprites.draw_sprite(screen, 0)

    now = pygame.time.get_ticks()

    if now - last_update_time > animation_delay:
        last_update_time = now
        current_sprite = (current_sprite + 1) % len(idle_sprites.sprites)

    new_player.set_sprite(screen, idle_sprites.sprites[current_sprite])
    new_player.draw(screen)

    new_player.draw_health_bar(screen)

    new_player.move(screen)

    if pygame.mouse.get_pressed()[0]:
        new_player.make_shoot()

    clock.tick(60)
    pygame.display.flip()

pygame.quit()
sys.exit()
