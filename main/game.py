import sys
from scripts.GameObjects import Player, Coin, ScoreCounter, particles
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


def options():
    while True:
        OPTIONS_MOUSE_POS = pygame.mouse.get_pos()

        SCREEN.fill("white")

        OPTIONS_TEXT = get_font(45).render("This is the OPTIONS screen.", True, "Black")
        OPTIONS_RECT = OPTIONS_TEXT.get_rect(center=(640, 260))
        SCREEN.blit(OPTIONS_TEXT, OPTIONS_RECT)

        OPTIONS_BACK = Button(image=None, pos=(SCREEN_WIDTH // 2, 460),
                              text_input="BACK", font=get_font(50), base_color="Black", hovering_color="Green")

        OPTIONS_BACK.changeColor(OPTIONS_MOUSE_POS)
        OPTIONS_BACK.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if OPTIONS_BACK.checkForInput(OPTIONS_MOUSE_POS):
                    main_menu()

        pygame.display.update()


def main_menu():
    while True:
        SCREEN.blit(BG, (0, 0))

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(60).render("Coin-rpg", True, "#b68f40")

        MENU_RECT = MENU_TEXT.get_rect(center=(SCREEN_WIDTH // 2, 100))

        PLAY_BUTTON = Button(image=pygame.image.load("assets/Options Rect.png"), pos=(SCREEN_WIDTH // 2, 250),
                             text_input="Играть", font=get_font(50), base_color="#d7fcd4", hovering_color="White")

        OPTIONS_BUTTON = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(SCREEN_WIDTH // 2, 400),
                                text_input="Настройки", font=get_font(40), base_color="#d7fcd4", hovering_color="White")

        QUIT_BUTTON = Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(SCREEN_WIDTH // 2, 550),
                             text_input="Выйти", font=get_font(40), base_color="#d7fcd4", hovering_color="White")

        SCREEN.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.init()  # КОД ИГРЫ ЗДЕСЬ КОД ИГРЫ ЗДЕСЬ КОД ИГРЫ ЗДЕСЬ КОД ИГРЫ ЗДЕСЬ КОД ИГРЫ ЗДЕСЬ

                    clock = pygame.time.Clock()
                    running = True
                    all_sprites = pygame.sprite.Group()
                    screen_width = 800
                    screen_height = 700

                    screen = pygame.display.set_mode((screen_width, screen_height))

                    pygame.display.set_caption("Test field")

                    new_player = Player(size=50, animation_delay=200)
                    new_player.place((300, 250))
                    weapon = Weapon(10, 1, 10, 'images/bullet.png')
                    new_player.add_weapon(weapon)

                    idle_sprites = SpriteSheet('images/player/idle/idle_sprites.png', 4, 50)
                    run_sprites = SpriteSheet('images/player/run/run_sprites.png', 6, 50)
                    new_player.set_sprites(idle_sprites.sprites)

                    next_map = TileMap()
                    next_map.load_tilemap('images/tilesets/Dungeon_Tileset.png', rows=10, cols=10, tile_size=40)

                    heal = next_map.get_tile(9, 8)
                    heal = next_map.get_tile(9, 8)
                    heal = HealingPotion(heal)
                    heal.place((400, 350))

                    inventory = Inventory(screen, new_player)

                    next_map.load_level('all_levels/level2.db')
                    enemies_list = next_map.enemies

                    score_counter = ScoreCounter()
                    index = 100

                    coins = []
                    coin_position = pygame.Vector2(500, 250)
                    coin = Coin(coin_position, score_counter, all_sprites)
                    coins.append(coin)

                    walls = [tile for tile in next_map.current_tile_map if tile.wall]
                    traps = [trap for trap in next_map.current_tile_map if isinstance(trap, Trap)]

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

                        if new_player.moving:
                            new_player.set_sprites(run_sprites.sprites)
                        else:
                            new_player.set_sprites(idle_sprites.sprites)

                        next_map.draw_tiles(screen)

                        heal.draw(screen)
                        heal.handle_collision(inventory, new_player)

                        player_position = new_player.position
                        for enemy in enemies_list:
                            enemy.update(screen, walls=walls, player_bullets=new_player.bullets,
                                         player=new_player)

                        if pygame.mouse.get_pressed()[0]:
                            new_player.make_shoot()
                        # for i in particles:
                        #     i.draw(screen)
                        #     #particles.remove(i)
                        # new_player.draw_health_bar(screen)
                        # inventory.draw_inventory()

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
                            trap.handle_collision(new_player)

                        new_player.update(screen, draw_surface=False, walls=walls, tilemaps=[next_map],
                                          all_enemy_bullets=[enemy.bullets for enemy in enemies_list])

                        score_counter.draw_score(screen)
                        for i in coins:
                            i.draw(screen)
                            if i.check_collision(new_player.rect):
                                coins.remove(i)

                        for enemy in next_map.enemies:
                            enemy.update(screen, walls, new_player.bullets, new_player)

                        clock.tick(60)
                        pygame.display.flip()
                if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                    options()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()


main_menu()
