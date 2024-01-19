import sys
import pygame
from scripts.Tiles import *
from scripts.Sprites import *
from scripts.Inventory import *
from scripts.GameObjects import Entity, Form, Direction, Player
from scripts.Weapons import Weapon
from scripts.traps import Trap

pygame.init()

clock = pygame.time.Clock()

running = True

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
heal.set_x(300)
heal.set_y(200)

traps = []

# Create traps and add them to the list
trap1 = Trap(icon_path='images/trap12.png', size=30, effect='damage', power=15)
trap1.place((250, 250))
traps.append(trap1)

# trap2 = Trap(icon_path='images/poison_trap.png', size=20, effect='poison', power=5)
# trap2.place((200, 100))
# traps.append(trap2)


level1.add_tile(heal)
speed_potion = SpeedPotion(icon_path='images/speedpo.png', size=25, speed=2)
speed_potion.place((600, 600))

healing_potion = HealingPotion(icon_path='images/health.png', size=30, healing_power=30)
healing_potion.place((600, 600))

healing_potion1 = HealingPotion(icon_path='images/health.png', size=30, healing_power=30)
healing_potion1.place((600, 600))
level1_map = [
    ["grass", "dirt", "grass", "grass", "grass", "grass"],
    ["dirt", "dirt", "grass", "dirt", "grass", "grass"],
    ["grass", "grass", "dirt", "grass", "dirt", "grass"],
    ["grass", "dirt", "grass", "grass", "grass", "grass"],
]

walls = TileMap()
inventory = Inventory(screen, new_player)
for i in range(6):
    for j in range(5):
        if i in [0, 5] or j in (0, 4):
            tile = level1.get_tile(j, i)
            tile.set_x(i * level1.tile_size + 200)
            tile.set_y(j * level1.tile_size + 150)
            walls.add_tile(tile)
        else:
            tile = level1.get_tile(j, i)
            tile.set_x(i * level1.tile_size + 200)
            tile.set_y(j * level1.tile_size + 150)
            level1.add_tile(tile)
index = 100
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


    # level1.draw_all_tiles(screen, 150, 30)
    # idle_sprites.draw_sprite(screen, 0)
    new_player.move(screen, walls)

    if new_player.moving:
        new_player.set_sprites(run_sprites.sprites)
    else:
        new_player.set_sprites(idle_sprites.sprites)



    walls.draw_tiles(screen)
    level1.draw_tiles(screen)
    for trap in traps:
        trap.draw(screen)
        trap.handle_collision(inventory, new_player)
    new_player.draw(screen)

    speed_potion.draw(screen)

    speed_potion.handle_collision(inventory, new_player)

    healing_potion.draw(screen)

    healing_potion.handle_collision(inventory, new_player)

    healing_potion1.draw(screen)

    healing_potion1.handle_collision(inventory, new_player)
    if pygame.mouse.get_pressed()[0]:
        new_player.make_shoot()

    new_player.draw_health_bar(screen)
    inventory.draw_inventory()
    keys = pygame.key.get_pressed()


    if index != 100:
        inventory.use_by_index(index)
        index = 100
    clock.tick(60)
    pygame.display.flip()

pygame.quit()
sys.exit()
