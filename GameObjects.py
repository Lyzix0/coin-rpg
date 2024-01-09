import enum
import pygame
import math
import GameExceptions
from main import player_pos, player_speed, screen_height, player_radius, screen_width, current_time, bullets, \
    bullet_speed, count_of_pop, bullet_cooldown, last_shot, bullets_from_player, player_health

last_shot = pygame.time.get_ticks()
class Form(enum.Enum):
    circle = 1
    rect = 2


class Direction:
    def __init__(self, x, y):
        """
        :param x: Параметр для направления по горизонтали. Принимает значение от -1 до 1
        :param y: Параметр для направления по вертикали. Принимает значение от -1 до 1
        """
        if x in (-1, 0, 1) and y in (-1, 0, 1):
            self._x = x
            self._y = y
        else:
            raise GameExceptions.DirectInitException()

    @property
    def x(self):
        """
        :return: направление по горизонтали
        """
        return self._x

    @property
    def y(self):
        """
        :return: направление по вертикали
        """
        return self._y


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
    def __init__(self):
        self.pos = player_pos
        self.radius = player_radius
        self.health = 100

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player_pos[0] > player_radius:
            player_pos[0] -= player_speed
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player_pos[0] > player_radius:
            player_pos[0] -= player_speed
        if keys[pygame.K_d] and player_pos[0] < screen_width - player_radius:
            player_pos[0] += player_speed
        if keys[pygame.K_w] and player_pos[1] > player_radius:
            player_pos[1] -= player_speed
        if keys[pygame.K_s] and player_pos[1] < screen_height - player_radius:
            player_pos[1] += player_speed

        keys = pygame.key.get_pressed()

    def shoot(self):
        # Стрельба игрока
        last_shot = pygame.time.get_ticks()
        if pygame.mouse.get_pressed()[0]:  # Стрельба при нажатии левой кнопки мыши
            speed_2 = 0
            if current_time - last_shot > bullet_cooldown:
                for i in range(count_of_pop):
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    angle = math.atan2(mouse_y - player_pos[1], mouse_x - player_pos[0])
                    bullet_x = player_pos[0] + player_radius * math.cos(angle)  # Вычисляем начальные координаты пули
                    bullet_y = player_pos[1] + player_radius * math.sin(angle)
                    bullet_dx = bullet_speed * math.cos(angle)
                    bullet_dy = bullet_speed * math.sin(angle)
                    if (mouse_x > screen_width // 2 and mouse_y < screen_height // 2) or (
                            mouse_x < screen_width // 2 and mouse_y > screen_height // 2):
                        new_bullet = [bullet_x, bullet_y, bullet_dx + speed_2, bullet_dy + speed_2]
                    else:
                        new_bullet = [bullet_x, bullet_y, bullet_dx + speed_2, bullet_dy - speed_2]
                    bullets.append(new_bullet)
                    bullets_from_player.append(new_bullet)
                    last_shot = current_time
                    speed_2 += (0.1 * -1)

    def draw(self, screen):
        pygame.draw.circle(screen, 'green', (player_pos[0], player_pos[1]), player_radius)
        pygame.draw.rect(screen, (0, 128, 0), (
            player_pos[0] - player_radius, player_pos[1] + 30, (player_health / 100) * (player_radius * 2), 5))

