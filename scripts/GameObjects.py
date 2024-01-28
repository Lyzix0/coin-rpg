from __future__ import annotations
import pygame.font
import random
import scripts.GameExceptions as GameExceptions
from scripts.Base import Form, Direction, rotate
from scripts.Weapons import Weapon, EnemyWeapon, EnemyBullet, PlayerBullet
import os

last_shot = pygame.time.get_ticks()


class GameObject:
    def __init__(self, size: int = 10):
        self._position = None
        self.size = size
        self.placed = False

    def place(self, position: pygame.Vector2 | tuple[float, float]):
        """
        Функция, которая вызывает объект на игровое поле. Можно использовать лишь один раз на экземпляре класа.
        """
        if self.placed:
            raise GameExceptions.PlaceException

        if isinstance(position, pygame.Vector2):
            self._position = position
        else:
            self._position = pygame.Vector2(*position)

        self.placed = True

    @property
    def position(self) -> pygame.Vector2:
        """
        :return: Позиция объекта на игровом поле
        """
        return self._position

    def draw(self, screen: pygame.surface):
        """
        Функция рисует указанную форму объекта на игровом поле.
        :param screen: Окно игры
        """
        if not self.placed:
            raise GameExceptions.NotPlacedException

        rect = pygame.Rect(self.position.x, self.position.y, self.size, self.size)
        pygame.draw.rect(screen, 'green', rect)


class Entity(GameObject):
    def __init__(self, size: int = 10, health: float | int = 100, speed: float | int = 1):
        super().__init__(size)
        self._health = health
        self.speed = speed
        self.alive = True
        self._damage_timer = 0

    def draw(self, screen):
        """
        Функция рисует указанную форму сущности на игровом поле, при условии, что он жив
        :param screen: Окно игры
        """
        if not self.alive:
            return

        super().draw(screen)

    def draw_health_bar(self, screen):
        """
        Функция рисует полоску здоровья сущности, при условии, что она жива
        :param screen: Окно игры
        """

        if not self.alive:
            return

        green_bar = pygame.Rect(self.position.x, self.position.y + self.size + 5, (self._health / 100) * self.size, 5)
        red_bar = pygame.Rect(self.position.x, self.position.y + self.size + 5, self.size, 5)

        pygame.draw.rect(screen, 'red', red_bar)
        pygame.draw.rect(screen, (0, 128, 0), green_bar)

    @property
    def health(self) -> int:
        """
        :return: Количество здоровья сущности
        """
        return self._health

    def take_damage(self, damage: int):
        """
        Функция наносит урон сущности. Если количество жизней сущности не положительное, сущность умирает
        :param damage: урон, наносимый сущности
        """
        if self.alive:
            self._health -= damage
            self._damage_timer = 500

            if self._health <= 0:
                self._die()

    def _die(self):
        self.alive = False
        print("Объект удален!")

    def move(self, direction: Direction):
        dx, dy = direction.x, direction.y
        self.position.x += dx * self.speed
        self.position.y += dy * self.speed


class Player(Entity, pygame.sprite.Sprite):
    def __init__(self, size: int = 10, health: float | int = 100, speed: float | int = 3, animation_delay: int = 250):
        super().__init__(size, health, speed)
        self.current_weapon = None
        self._weapons = []
        self._bullets = []

        self.sprite_number = 0
        self.sprites = []

        self.facing_right = True
        self.moving = False

        self.animation_delay = animation_delay
        self._last_time_update = 0
        self.rect = pygame.Rect(0, 0, 32, 32)

    def apply_healing(self, amount):
        self._health = min(self._health + amount, 100)

    def apply_poison_effect(self, duration: int):
        self.speed /= 2  # Reduce speed to half
        self.poison_effect_end_time = pygame.time.get_ticks() + duration

    def can_move_left(self):
        return self.position.x + self.size + 10 > self.size

    def can_move_right(self, screen_width):
        return self.position.x < screen_width - self.size

    def can_move_up(self):
        return self.position.y + self.size > self.size

    def can_move_down(self, screen_height):
        return self.position.y < screen_height - self.size

    def move(self, screen, tilemaps=None):
        if tilemaps is None:
            tilemaps = []

        keys = pygame.key.get_pressed()
        dx, dy = 0, 0

        if keys[pygame.K_a] and self.can_move_left():
            dx -= self.speed
        if keys[pygame.K_d] and self.can_move_right(screen.get_width()):
            dx += self.speed
        if keys[pygame.K_w] and self.can_move_up():
            dy -= self.speed
        if keys[pygame.K_s] and self.can_move_down(screen.get_height()):
            dy += self.speed

        rect_after_move = self.rect.copy()
        rect_after_move.x += dx
        rect_after_move.y += dy

        collision_detected = False

        walls = [tile for tilemap in tilemaps for tile in tilemap.current_tile_map if tile.wall]

        for wall in walls:
            if (rect_after_move.right > wall.rect.left and
                    rect_after_move.left < wall.rect.right and
                    rect_after_move.bottom > wall.rect.top and
                    rect_after_move.top < wall.rect.bottom):
                collision_detected = True
                break

        if not collision_detected:
            self.position.x += dx
            self.position.y += dy
            if dx > 0:
                self.facing_right = True
            elif dx < 0:
                self.facing_right = False

        self.moving = dx != 0 or dy != 0
        self.rect = pygame.Rect(self.position.x, self.position.y, self.size, self.size)

    def add_weapon(self, weapon: EnemyWeapon):
        current_weapon = weapon
        self.current_weapon = current_weapon
        self._weapons.append(current_weapon)

    def make_shoot(self):
        if not self.current_weapon:
            return

        bullet = self.current_weapon.shoot(pygame.Vector2(*self.rect.center))
        if bullet:
            self._bullets.append(bullet)

    def draw(self, screen, draw_surface: bool = False, walls=None):
        if walls is None:
            walls = []

        self.rect.y += 30
        self.rect.x += 8
        self.rect.height -= 23
        self.rect.width = 32

        if draw_surface:
            pygame.draw.rect(screen, 'green', self.rect, 2)

        now = pygame.time.get_ticks()

        if not self.alive:
            return

        if now - self._last_time_update > self.animation_delay:
            self._last_time_update = now
            self.sprite_number = (self.sprite_number + 1) % len(self.sprites)

        if not self.facing_right:
            sprite = pygame.transform.flip(self.sprites[self.sprite_number], True, False)
        else:
            sprite = self.sprites[self.sprite_number]

        screen.blit(sprite, self.position)

        for bullet in self._bullets:
            bullet.update(screen, walls)

    def set_sprites(self, sprites):
        if self.sprites == sprites:
            return
        self.sprite_number = 0
        self.sprites.clear()
        for sprite in sprites:
            self.sprites.append(sprite)

    def update(self, screen, draw_surface: bool = False, walls=None, tilemaps=None,
               all_enemy_bullets: [[EnemyBullet]] = None):
        if all_enemy_bullets is None:
            all_enemy_bullets = []

        if self.alive:
            self.move(screen, tilemaps)
            self.draw(screen, draw_surface, walls)

            for enemy_bullets in all_enemy_bullets:
                for bullet in enemy_bullets:
                    if bullet.rect.colliderect(self.rect) and bullet.can_damage:
                        self.take_damage(10)
                        bullet.can_damage = False

    @property
    def bullets(self):
        return self._bullets


class Enemy(Entity, pygame.sprite.Sprite):
    def __init__(self, size: int = 10, health: float | int = 50, speed: float | int = 5, animation_delay: int = 200,
                 name: str = 'enemy'):
        super().__init__(size, health, speed)
        self.animation_delay = animation_delay
        self._last_time_update = 0
        self.rect = pygame.Rect(0, 0, 32, 32)
        self.sprites = []
        self.sprite_number = 0
        self.facing_right = True
        self.moving = False
        self.current_weapon = None
        self._bullets = []
        self.current_weapon = EnemyWeapon(10, random.random(), 1, '../main/images/enemy_bullet.png')
        self.direction = None
        self.name = name
        self._start_update_time = pygame.time.get_ticks() + random.randint(50, 1500)

    def set_sprites(self, sprites):
        if self.sprites == sprites:
            return
        self.sprite_number = 0
        self.sprites.clear()
        for sprite in sprites:
            self.sprites.append(sprite)

    def update_animation(self):
        now = pygame.time.get_ticks()
        if now - self._last_time_update > self.animation_delay:
            self._last_time_update = now
            self.sprite_number = (self.sprite_number + 1) % len(self.sprites)

    def move_randomly(self, walls=None):
        collision_detected = False

        if walls is None:
            walls = []

        now = pygame.time.get_ticks()

        if now % 600 < 450:
            self.moving = False
            self.direction = random.choice(['up', 'down', 'left', 'right'])
        else:
            self.moving = True

            movement_speed = self.speed
            if self.direction in ['up', 'down']:
                movement_speed *= 0.7

            new_position = self.position.copy()

            if self.direction == 'up':
                new_position.y -= movement_speed
            elif self.direction == 'down':
                new_position.y += movement_speed
            elif self.direction == 'left':
                new_position.x -= movement_speed
                self.facing_right = False
            elif self.direction == 'right':
                new_position.x += movement_speed
                self.facing_right = True

            for wall in walls:
                if wall.rect.colliderect(pygame.Rect(*new_position, self.size, self.size)):
                    collision_detected = True
                    break

            if not collision_detected:
                self.position.x = new_position.x
                self.position.y = new_position.y

    def make_shoot(self, player: Player):
        if not self.current_weapon or not player.alive:
            return

        bullet = self.current_weapon.shoot(self.position.copy(),
                                           pygame.Vector2(player.position.x + random.randint(1, 30),
                                                          player.position.y + random.randint(10, 40)))
        if bullet:
            self._bullets.append(bullet)

    def update_bullets(self, screen, walls=None):
        for bullet in self._bullets:
            bullet.update(screen, walls)

    def update(self, screen, walls=None, player_bullets: [PlayerBullet] = None, player: Player = None):
        if player_bullets is None:
            player_bullets = []

        if self.alive:
            self.update_animation()
            self.draw(screen)
            if pygame.time.get_ticks() < self._start_update_time:
                return
            self.move_randomly(walls)
            if player:
                self.make_shoot(player)

            for bullet in player_bullets:
                if self.rect.colliderect(bullet.rect) and bullet.can_damage:
                    self.take_damage(10)
                    bullet.can_damage = False

        self.update_bullets(screen, walls)

    def draw(self, screen):
        self.rect.y = self.position.y + 30
        self.rect.x = self.position.x + 8
        self.rect.height = self.size - 23
        self.rect.width = 32

        now = pygame.time.get_ticks()

        if now - self._last_time_update > self.animation_delay:
            self._last_time_update = now
            self.sprite_number = (self.sprite_number + 1) % len(self.sprites)

        if not self.facing_right:
            sprite = pygame.transform.flip(self.sprites[self.sprite_number], True, False)
        else:
            sprite = self.sprites[self.sprite_number]

        screen.blit(sprite, self.position)

    @property
    def bullets(self):
        return self._bullets


class ScoreCounter:
    def __init__(self):
        self.score = 0
        self.font = pygame.font.Font("../main/images/font/Pixel Emulator.otf", 20)
        self.text_color = (255, 215, 0)

    def increase_score(self, amount):
        self.score += amount

    def get_score(self):
        return self.score

    def draw_score(self, screen):
        text = self.font.render(f"Coins:{self.score}", True, self.text_color)
        screen.blit(text, (10, 10))


class Coin(pygame.sprite.Sprite):
    def __init__(self, position: pygame.Vector2, score_counter: ScoreCounter, all_sprites: pygame.sprite.Group,
                 animation_delay: int = 200, sprite_size: int = 32):
        super().__init__()
        self.position = position
        self.sprite_size = sprite_size
        self.animation_delay = animation_delay
        self.sprites = self.load_sprites()  # Загружаем изображения для анимации
        self.sprite_number = 0
        self.rect = pygame.Rect(self.position.x, self.position.y, 32, 32)
        self._last_time_update = 0
        self.score_counter = score_counter
        self.all_sprites = all_sprites

    def load_sprites(self):
        sprite_folder = "images/coin_animation"  # Папка с изображениями для анимации
        sprite_files = [f for f in os.listdir(sprite_folder) if f.endswith('.png')]
        sprite_files.sort()
        sprites = [pygame.transform.scale(pygame.image.load(os.path.join(sprite_folder, f)),
                                          (self.sprite_size, self.sprite_size)) for f in sprite_files]
        return sprites

    def update_animation(self):
        now = pygame.time.get_ticks()
        if now - self._last_time_update > self.animation_delay:
            self._last_time_update = now
            self.sprite_number = (self.sprite_number + 1) % len(self.sprites)

    def draw(self, screen):
        self.update_animation()
        sprite = self.sprites[self.sprite_number]
        screen.blit(sprite, self.position)

    def check_collision(self, player_rect):
        if self.rect.colliderect(player_rect):
            self.score_counter.increase_score(1)
            self.kill()
            return True
        return False


class Door(GameObject, pygame.sprite.Sprite):
    def __init__(self, icon, size: int = 40, is_locked: bool = True, active_objects: list = None,
                 all_sprites: list = None, enemies_list: list = None):
        super().__init__(size)
        self.is_locked = is_locked
        if type(icon) == 'str':
            self.icon = pygame.image.load(icon)
        else:
            self.icon = icon.image
        self.active_objects = active_objects
        self.all_sprites = all_sprites
        self.level_name = 2
        self.enemies_list = enemies_list
        self.active_objects = active_objects

    def draw(self, screen: pygame.surface):
        if not self.placed:
            raise GameExceptions.NotPlacedException
        icon_size = (self.size, self.size)
        icon = pygame.transform.scale(self.icon, icon_size)
        screen.blit(icon, (self.position.x - 10, self.position.y - 10))

    def handle_collision(self, player, next_map, screen: pygame.surface):
        if self.position.distance_to(player.position) < (self.size + player.size) / 2:
            for _ in next_map.current_tile_map:
                next_map.current_tile_map.remove(_)
            next_map.load_tilemap('images/tilesets/Dungeon_Tileset.png', rows=10, cols=10, tile_size=40)
            try:
                if os.path.exists(f'all_levels/level{self.level_name}.db'):
                    next_map.load_level(f'all_levels/level{self.level_name}.db')

                if self.all_sprites is not None:
                    self.all_sprites.remove(self)

                self.placed = (10000, 10000)
                dim_surface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
                dim_surface.fill((0, 0, 0, 128))
                screen.blit(dim_surface, (0, 0))
                pygame.display.flip()

            except Exception as e:
                print(f"An error occurred: {e}")
