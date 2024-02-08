import sys

import pygame

from scripts.GameObjects import Player, Coin, ScoreCounter, particles, coins, score_counter
from scripts.Inventory import *
from scripts.Tiles import *
from scripts.Weapons import Weapon


class Button:
    def __init__(self, image, pos, text_input, font, base_color, hovering_color):
        self.image = image
        self.x_pos = pos[0]
        self.y_pos = pos[1]
        self.font = font
        self.base_color, self.hovering_color = base_color, hovering_color
        self.text_input = text_input
        self.text = self.font.render(self.text_input, True, self.base_color)
        if self.image is None:
            self.image = self.text
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

    def update(self, screen):
        if self.image is not None:
            screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)

    def checkForInput(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top,
                                                                                          self.rect.bottom):
            return True
        return False

    def changeColor(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top,
                                                                                          self.rect.bottom):
            self.text = self.font.render(self.text_input, True, self.hovering_color)
        else:
            self.text = self.font.render(self.text_input, True, self.base_color)


pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

BG = pygame.image.load("assets/Background.png")


def get_font(size):
    return pygame.font.Font("assets/font.ttf", size)


def load_game():
    with open('game_data.txt', 'r', encoding='utf-8') as f:
        lines = f.read().split()

    play_game(level_name=lines[0], position=pygame.Vector2(float(lines[1]), float(lines[2])), health=int(lines[3]))


def save_game(tilemap: TileMap, player: Player):
    level = tilemap.level_name
    pos = player.position
    with open('game_data.txt', 'w', encoding='utf-8') as f:
        f.write(level)
        f.write(f"\n{pos.x} {pos.y}")
        f.write(f"\n{player.health}")


def main_menu():
    pygame.display.set_caption('Main Menu')
    while True:
        SCREEN.blit(BG, (0, 0))

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(60).render("Coin-rpg", True, "#b68f40")

        MENU_RECT = MENU_TEXT.get_rect(center=(SCREEN_WIDTH // 2, 100))

        PLAY_BUTTON = Button(image=pygame.image.load("assets/Options Rect.png"), pos=(SCREEN_WIDTH // 2, 250),
                             text_input="Новая игра", font=get_font(50), base_color="#d7fcd4", hovering_color="White")

        LOAD_GAME_BUTTON = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(SCREEN_WIDTH // 2, 400),
                                  text_input="Загрузить игру", font=get_font(30), base_color="#d7fcd4",
                                  hovering_color="White")

        QUIT_BUTTON = Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(SCREEN_WIDTH // 2, 550),
                             text_input="Выйти", font=get_font(30), base_color="#d7fcd4", hovering_color="White")

        SCREEN.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_BUTTON, LOAD_GAME_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    play_game()
                if LOAD_GAME_BUTTON.checkForInput(MENU_MOUSE_POS):
                    load_game()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()


def play_game(level_name: str = 'level1', position: pygame.Vector2 = pygame.Vector2(300, 300), health: int = 100):
    start_time = time.time()
    shoot_cooldown = 1
    last_shoot_time = start_time

    pygame.init()  # КОД ИГРЫ ЗДЕСЬ КОД ИГРЫ ЗДЕСЬ КОД ИГРЫ ЗДЕСЬ КОД ИГРЫ ЗДЕСЬ КОД ИГРЫ ЗДЕСЬ

    clock = pygame.time.Clock()
    running = True
    screen_width = 800
    screen_height = 700

    screen = pygame.display.set_mode((screen_width, screen_height))

    pygame.display.set_caption("Coin-rpg")

    new_player = Player(size=50, animation_delay=200)
    new_player.take_damage(100-health)
    new_player.place(position)
    weapon = Weapon(10, 1, 10, 'images/bullet.png')
    new_player.add_weapon(weapon)

    idle_sprites = SpriteSheet('images/player/idle/idle_sprites.png', 4, 50)
    run_sprites = SpriteSheet('images/player/run/run_sprites.png', 6, 50)
    new_player.set_sprites(idle_sprites.sprites)

    next_map = TileMap()
    next_map.load_tilemap('images/tilesets/Dungeon_Tileset.png', rows=10, cols=10, tile_size=40)

    inventory = Inventory(screen, new_player)

    next_map.load_level(f'all_levels/{level_name}.db', new_player)
    enemies_list = next_map.enemies

    index = 100

    traps = [trap for trap in next_map.current_tile_map if isinstance(trap, Trap)]

    while running:
        current_time = time.time()

        if pygame.mouse.get_pressed()[0] and (current_time - start_time >= 1) and (
                current_time - last_shoot_time >= shoot_cooldown):
            new_player.make_shoot()
            last_shoot_time = current_time

        screen.fill(pygame.color.Color(36, 20, 25))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                start_time = current_time
                save_game(next_map, new_player)
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

        if new_player.moving:
            new_player.set_sprites(run_sprites.sprites)
        else:
            new_player.set_sprites(idle_sprites.sprites)

        next_map.draw_tiles(screen)

        for enemy in enemies_list:
            enemy.update(screen, walls=next_map.walls, player_bullets=new_player.bullets,
                         player=new_player)

        inventory.draw_inventory()

        new_player.draw_health_bar(screen)

        for p in particles:
            p.draw(screen)
            p.image.set_alpha(p.image.get_alpha() - 10)
            if p.image.get_alpha() == 0:
                particles.remove(p)
                continue
            particles.remove(p)
            particles.insert(0, p)

        if index != 100:
            inventory.use_by_index(index)
            index = 100

        for trap in traps:
            if new_player.rect:
                trap.handle_collision(new_player)

        new_player.update(screen, draw_surface=False, walls=next_map.walls, tilemaps=[next_map],
                          all_enemy_bullets=[enemy.bullets for enemy in enemies_list])

        score_counter.draw_score(screen)
        for i in coins:
            i.draw(screen)
            if i.check_collision(new_player.rect):
                coins.remove(i)

        for enemy in next_map.enemies:
            enemy.update(screen, next_map.walls, new_player.bullets, new_player)

        for door in next_map.doors:
            door: Door
            door.handle_collision(new_player, next_map, screen, coins)

        clock.tick(60)
        if 0 < int(clock.get_fps()) < 56:
            print("FPS:", int(clock.get_fps()))
        pygame.display.flip()


main_menu()
