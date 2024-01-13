import pygame
import classes.GameExceptions as GameExceptions
from classes.Base import Form, Direction, rotate
from classes.Weapons import Weapon
from classes.Sprites import *

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

    def can_move_left(self):
        return self.position.x + self.size > self.size

    def can_move_right(self, screen_width):
        return self.position.x < screen_width - self.size

    def can_move_up(self):
        return self.position.y + self.size > self.size

    def can_move_down(self, screen_height):
        return self.position.y < screen_height - self.size

    def move(self, screen):

        keys = pygame.key.get_pressed()

        self.moving = False

        if keys[pygame.K_a] and self.can_move_left():
            self.facing_right = False
            self.position.x -= self.speed
            self.moving = True
        if keys[pygame.K_d] and self.can_move_right(screen.get_width()):
            self.position.x += self.speed
            self.facing_right = True
            self.moving = True
        if keys[pygame.K_w] and self.can_move_up():
            self.position.y -= self.speed
            self.moving = True
        if keys[pygame.K_s] and self.can_move_down(screen.get_height()):
            self.position.y += self.speed
            self.moving = True

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

