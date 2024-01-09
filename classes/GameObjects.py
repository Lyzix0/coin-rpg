import pygame
import classes.GameExceptions as GameExceptions
from classes.Base import Form, Direction
from classes.Weapons import Weapon

last_shot = pygame.time.get_ticks()


class Object:
    def __init__(self, size: int = 10, form: Form = Form.rect):
        self.form = form
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

        match self.form:
            case Form.rect:
                rect = pygame.Rect(self.position.x, self.position.y, self.size, self.size)
                pygame.draw.rect(screen, 'green', rect)
            case Form.circle:
                center = self.position.x + self.size / 2, self.position.y + self.size / 2
                pygame.draw.circle(screen, 'green', center, self.size / 2)


class Entity(Object):
    def __init__(self, size: int = 10, form: Form = Form.rect, health: float | int = 100, speed: float | int = 1):
        super().__init__(size, form)
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


class Player(Entity):
    def __init__(self, size: int = 10, form: Form = Form.rect, health: float | int = 100, speed: float | int = 3):
        super().__init__(size, form, health, speed)
        self.current_weapon = None
        self._weapons = []
        self._bullets = []

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

        if keys[pygame.K_a] and self.can_move_left():
            self.position.x -= self.speed
        if keys[pygame.K_d] and self.can_move_right(screen.get_width()):
            self.position.x += self.speed
        if keys[pygame.K_w] and self.can_move_up():
            self.position.y -= self.speed
        if keys[pygame.K_s] and self.can_move_down(screen.get_height()):
            self.position.y += self.speed

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
        # отрисовка всех пуль
        if self._bullets:
            for bullet in self._bullets:
                bullet.draw(screen)

        # рисуем персонажа
        super().draw(screen)
