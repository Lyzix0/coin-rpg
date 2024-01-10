import sys
import pygame
from classes.Tiles import *
from classes.Base import load_image
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

new_player = Player(form=Form.circle, size=50)
new_player.place((200, 250))
weapon = Weapon(10, 1, 10, 'images/bullet.png')
new_player.add_weapon(weapon)

level1 = TileMap(50)

level1_map = [
    ["grass", "dirt", "grass", "grass", "grass", "grass"],
    ["dirt", "dirt", "grass", "dirt", "grass", "grass"],
    ["grass", "grass", "dirt", "grass", "dirt", "grass"],
    ["grass", "dirt", "grass", "grass", "grass", "grass"],
]

level1.load_tilemap('images/tilesets/Dungeon_Tileset.png', rows=10, cols=10)


while running:
    screen.fill('black')

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    level1.draw_tilemap(screen, 150, 30)

    new_player.draw(screen)
    new_player.draw_health_bar(screen)

    new_player.move(screen)

    if pygame.mouse.get_pressed()[0]:
        new_player.make_shoot()

    clock.tick(60)
    pygame.display.flip()

pygame.quit()
sys.exit()
