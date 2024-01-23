import sys

import pygame

from scripts.Tiles import *
from scripts.Sprites import *
from scripts.Inventory import *
from scripts.GameObjects import Entity, Form, Direction, Player, Enemy, Coin, ScoreCounter
from scripts.Weapons import Weapon
from scripts.Tiles import Trap


pygame.init()

clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()
running = True
all_sprites = pygame.sprite.Group()
screen_width = 800
screen_height = 600

screen = pygame.display.set_mode((screen_width, screen_height))

pygame.display.set_caption("Test field")

new_player = Player(size=50, animation_delay=200)
new_player.place((300, 250))
weapon = Weapon(10, 1, 10, 'images/bullet.png')
new_player.add_weapon(weapon)

idle_sprites = SpriteSheet('images/player/idle/idle_sprites.png', 4, 50)
run_sprites = SpriteSheet('images/player/run/run_sprites.png', 6, 50)

new_player.set_sprites(idle_sprites.sprites)

level1 = TileMap()
level1.load_tilemap('images/tilesets/Dungeon_Tileset.png', rows=10, cols=10, tile_size=40)

heal = level1.get_tile(9, 8)
heal = HealingPotion(heal)
heal.place((400, 350))

level1_map = [
    ["grass", "dirt", "grass", "grass", "grass", "grass"],
    ["dirt", "dirt", "grass", "dirt", "grass", "grass"],
    ["grass", "grass", "dirt", "grass", "dirt", "grass"],
    ["grass", "dirt", "grass", "grass", "grass", "grass"],
]

inventory = Inventory(screen, new_player)

level1.load_level('level1')

trap_tilemap = TileMap()
trap_tilemap.load_tilemap('images/peaks/peaks.png', rows=1, cols=1)

trap = Trap(trap_tilemap.get_tile(0, 0).image, 250, 300, sprites_damage=[True, True, False, False])
trap.sprites = SpriteSheet('images/peaks/peaks.png', 4, 32)
trap_tilemap.add_tile(trap)

enemies_list = []

enemy1 = Enemy(size=30, health=50, speed=2, animation_delay=200)
enemy_sprites = SpriteSheet('images/sprite0_strip4.png', 4, 40)
enemy1.set_sprites(enemy_sprites.sprites)
enemy1.place((400, 100))
coins = []
enemies_list.append(enemy1)
score_counter = ScoreCounter()
index = 100
coin_position = pygame.Vector2(400, 400)
coin = Coin(coin_position, score_counter, all_sprites)
coins.append(coin)
while running:
    screen.fill(pygame.color.Color(36, 20, 25))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                index = 0
            elif event.key == pygame.K_2:
                index = 1
            elif event.key == pygame.K_3:
                index = 2
            elif event.key == pygame.K_4:
                index = 3
            elif event.key == pygame.K_5:
                index = 4
            elif event.key == pygame.K_6:
                index = 5
            elif event.key == pygame.K_7:
                index = 6
            elif event.key == pygame.K_8:
                index = 7
        elif event.type == pygame.USEREVENT + 1:
            new_player.speed /= 2
            pygame.time.set_timer(pygame.USEREVENT + 1, 0)

    new_player.move(screen, tilemaps=[level1])

    if new_player.moving:
        new_player.set_sprites(run_sprites.sprites)
    else:
        new_player.set_sprites(idle_sprites.sprites)

    level1.draw_tiles(screen)

    heal.draw(screen)
    heal.handle_collision(inventory, new_player)

    trap_tilemap.draw_tiles(screen)
    trap.handle_collision(new_player)

    player_position = new_player.position

    for enemy in enemies_list:
        enemy.update()
        enemy.make_shoot(player_position)
        enemy.draw(screen)

    if pygame.mouse.get_pressed()[0]:
        new_player.make_shoot()

    new_player.draw_health_bar(screen)
    inventory.draw_inventory()

    keys = pygame.key.get_pressed()

    if index != 100:
        inventory.use_by_index(index)
        index = 100

    new_player.draw(screen, True)
    score_counter.draw_score(screen)
    for i in coins:
        i.draw(screen)
        if i.check_collision(new_player.rect):
            print("Coin collected!")
            coins.remove(i)
    clock.tick(60)
    pygame.display.flip()

pygame.quit()
sys.exit()
