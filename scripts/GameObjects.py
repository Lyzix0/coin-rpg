from __future__ import annotations

import pygame
import scripts.GameExceptions as GameExceptions
from scripts.Base import Form, Direction, rotate
from scripts.Weapons import Weapon
from scripts.Sprites import *
from scripts.Tiles import *

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
        self._health += amount

    def can_move_left(self):
        return self.position.x + self.size + 10 > self.size

    def can_move_right(self, screen_width):
        return self.position.x < screen_width - self.size

    def can_move_up(self):
        return self.position.y + self.size > self.size

    def can_move_down(self, screen_height):
        return self.position.y < screen_height - self.size

    def move(self, screen, walls=None):
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
        if walls:
            # Задаем значения смещения для каждой стороны (left, right, top, bottom)
            offset_left = 12
            offset_right = 12
            offset_top = 12
            offset_bottom = 36  # Уменьшаем это значение, если хотим уменьшить отклонение снизу

            for wall in walls.current_tile_map:
                if (rect_after_move.right > wall.rect.left + offset_left and
                        rect_after_move.left < wall.rect.right - offset_right and
                        rect_after_move.bottom > wall.rect.top and
                        rect_after_move.top < wall.rect.bottom - offset_bottom):
                    collision_detected = True
                    break

        if not collision_detected:
            self.position.x += dx
            self.position.y += dy
            self.facing_right = dx > 0

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

    def draw(self, screen):
        now = pygame.time.get_ticks()

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

