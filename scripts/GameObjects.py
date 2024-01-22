from __future__ import annotations

import pygame
import scripts.GameExceptions as GameExceptions
from scripts.Base import Form, Direction, rotate
from scripts.Weapons import Weapon
from scripts.Sprites import *
from scripts.Tiles import *
import math
last_shot = pygame.time.get_ticks()


class Object:
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


class Entity(Object):
    def __init__(self, size: int = 10, health: float | int = 100, speed: float | int = 1):
        super().__init__(size)
        self._health = health
        self.speed = speed
        self.alive = True

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

    def move(self, screen, tilemaps: [TileMap] = []):
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

    def add_weapon(self, weapon: Weapon):
        current_weapon = weapon
        self.current_weapon = current_weapon
        self._weapons.append(current_weapon)

    def make_shoot(self):
        if not self.current_weapon:
            return

        bullet = self.current_weapon.shoot(self.position.copy())
        if bullet:
            self._bullets.append(bullet)

    def draw(self, screen, draw_surface: bool = False):
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
            bullet.draw(screen)

    def set_sprites(self, sprites):
        if self.sprites == sprites:
            return
        self.sprite_number = 0
        self.sprites.clear()
        for sprite in sprites:
            self.sprites.append(sprite)

class Enemy(Entity, pygame.sprite.Sprite):
    def __init__(self, size: int = 10, health: float | int = 50, speed: float | int = 2, animation_delay: int = 200):
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
        self.current_weapon = Weapon(10, 1, 10, 'images/bullet.png')

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

    def move_towards_player(self, player_position, min_distance=50):
        dx = player_position.x - self.position.x
        dy = player_position.y - self.position.y
        distance = math.sqrt(dx**2 + dy**2)

        if distance > min_distance:
            if distance != 0:
                dx /= distance
                dy /= distance

            self.position.x += dx * self.speed
            self.position.y += dy * self.speed

            if dx > 0:
                self.facing_right = True
            elif dx < 0:
                self.facing_right = False

    def make_shoot(self, player_position):
        if not self.current_weapon:
            return

        bullet = self.current_weapon.shoot(self.position.copy(), player_position)
        if bullet:
            self._bullets.append(bullet)

    def update_bullets(self):
        for bullet in self._bullets:
            bullet.update()

    def draw_bullets(self, screen):
        for bullet in self._bullets:
            bullet.draw(screen)

    def update(self, player_position):
        self.update_animation()
        self.move_towards_player(player_position)
        self.update_bullets()

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

        self.draw_bullets(screen)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, position, direction, speed, damage, image_path):
        super().__init__()
        self.original_image = pygame.image.load(image_path)
        #self.image = pygame.transform.scale(self.original_image, (8, 8))  # Adjust the size as needed
        self.rect = self.original_image.get_rect(center=position)
        self.position = pygame.Vector2(position)
        self.direction = direction
        self.speed = speed
        self.damage = damage
        self.img = pygame.image.load("images/1x1.png")


    def update(self):
        self.position += self.direction * self.speed
        self.rect.center = self.position
        self.rotate_towards_direction()

    def rotate_towards_direction(self):
        angle = -math.degrees(math.atan2(self.direction.y, self.direction.x))
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.img = pygame.transform.scale(self.image, (15, 15))
        self.rect = self.img.get_rect(center=self.rect.center)

    def draw(self, screen):
        screen.blit(self.img, self.rect)


class Weapon:
    def __init__(self, damage: int, fire_rate: int, bullet_speed: int, bullet_image_path: str):
        self.damage = damage
        self.fire_rate = fire_rate
        self.bullet_speed = bullet_speed
        self.bullet_imag = pygame.image.load(bullet_image_path)
        self.bullet_image = pygame.transform.scale(self.bullet_imag,(8,8))
        self.last_shot_time = 0

    def shoot(self, start_position: pygame.Vector2, target_position: pygame.Vector2):
        now = pygame.time.get_ticks()

        if now - self.last_shot_time > 1000 / self.fire_rate:
            self.last_shot_time = now

            direction = target_position - start_position
            direction.normalize()

            bullet = Bullet(start_position, direction, self.bullet_speed/50, self.damage, 'images/bullet.png')

            return bullet
        return None


