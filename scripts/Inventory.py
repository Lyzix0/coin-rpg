import pygame
from scripts import GameExceptions
from scripts.GameObjects import Object


class Cell:
    def __init__(self, image: pygame.surface, cell_name: str):
        self.image = image
        self.name = cell_name


class Inventory:

    def __init__(self, screen):
        self.cells = []
        self.screen = screen
        self.height = 50
        self.width = 500
        self.x = 150
        self.y = 550
        self.inventory_color = (255, 255, 255)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw_inventory(self):
        pygame.draw.rect(self.screen, self.inventory_color, self.rect, 2)
        for _ in range(0, 500, 50):
            pygame.draw.line(self.screen, (255, 255, 255), [150 + _, 550], [150 + _, 600], 3)
        for i in range(min(len(self.cells), 10)):
            self.screen.blit(self.cells[i].image, (155 + i * 50, 555))

    def add_item(self, cell: Cell):
        cell.image = pygame.transform.scale(cell.image, (40, 40))
        self.cells.append(cell)


class HealingPotion(Object):
    def __init__(self, icon_path: str, size: int = 10, healing_power: int = 20, active_objects: list = None):
        super().__init__(size)
        self.healing_power = healing_power
        self.icon = pygame.image.load(icon_path)
        self.alive = True
        self.active_objects = active_objects

    def draw(self, screen: pygame.surface):
        if not self.placed:
            raise GameExceptions.NotPlacedException
        if not self.alive:
            return
        rect = pygame.Rect(self.position.x, self.position.y, self.size / 3 * 1.4, self.size / 3)
        pygame.draw.rect(screen, 'green', rect)
        icon_size = (self.size, self.size)
        icon = pygame.transform.scale(self.icon, icon_size)
        screen.blit(icon, (self.position.x - 10, self.position.y - 10))

    def handle_collision(self, inventory, player):
        if self.alive and self.position.distance_to(player.position) < (self.size + player.size) / 2:
            cell = Cell(self.icon, 'xdd')
            inventory.add_item(cell)
            self._die()

    def _die(self):
        self.alive = False
        print("Зелье исцеления использовано!")
        if self.active_objects is not None:
            self.active_objects.remove(self)
