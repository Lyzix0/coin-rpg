import enum
import pygame


class Forms(enum.Enum):
    circle = 1
    rect = 2


class Entity:
    def __init__(self, health: float | int = 100, speed: float = 0.2, size: int = 10, form: Forms = Forms.rect):
        self.form = form
        self._position = pygame.Vector2(10, 10)
        self.health = health
        self.speed = speed
        self.size = size

    def place(self, position: pygame.Vector2 | tuple[float, float]):
        if isinstance(position, pygame.Vector2):
            self._position = position
        else:
            self._position = pygame.Vector2(*position)

    @property
    def position(self):
        return self._position

    def draw(self, screen: pygame.surface):
        match self.form:
            case Forms.rect:
                rect = self.position.x, self.position.y, self.position.x + self.size, self.position.y + self.size
                pygame.draw.rect(screen, 'green', rect)
            case Forms.circle:
                center = self.position.x, self.position.y
                pygame.draw.circle(screen, 'green', center, self.size)


player = Entity(form=Forms.circle)
player.place((10, 10))
