import sys
from scripts.Tiles import *
from scripts.Sprites import *
from scripts.Inventory import *
from scripts.GameObjects import Entity, Form, Direction, Player
from scripts.Weapons import Weapon


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

level1.add_tile(heal)

healing_potion = HealingPotion(icon_path='images/health.png', size=30, healing_power=30)
healing_potion.place((250, 250))

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

while running:
    screen.fill(pygame.color.Color(36, 20, 25))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # level1.draw_all_tiles(screen, 150, 30)
    # idle_sprites.draw_sprite(screen, 0)
    new_player.move(screen, walls)

    if new_player.moving:
        new_player.set_sprites(run_sprites.sprites)
    else:
        new_player.set_sprites(idle_sprites.sprites)

    walls.draw_tiles(screen)
    level1.draw_tiles(screen)

    new_player.draw(screen)

    healing_potion.draw(screen)

    healing_potion.handle_collision(inventory, new_player)

    if pygame.mouse.get_pressed()[0]:
        new_player.make_shoot()

    new_player.draw_health_bar(screen)
    inventory.draw_inventory()
    clock.tick(60)
    pygame.display.flip()

pygame.quit()
sys.exit()
