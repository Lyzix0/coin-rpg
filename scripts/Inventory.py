import pygame
from scripts import GameExceptions
from scripts.GameObjects import Object



class Cell:
    def __init__(self, image: pygame.surface, cell_name: str):
        self.image = image
        self.name = cell_name


class Inventory:

    def __init__(self, screen, player):
        self.cells = []
        self.screen = screen
        self.height = 50
        self.player = player
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

    def use_by_index(self, index: int):
        if 0 <= index < len(self.cells):
            cell = self.cells[index]
            if cell.name == "xdd" and self.player.health < 100:
                self.player.apply_healing(20)
                self.cells.pop(index)
                pygame.time.delay(200)

            if cell.name == "speed":
                self.player.speed *= 2
                self.cells.pop(index)
                pygame.time.set_timer(pygame.USEREVENT + 1, 20000)
                pygame.time.delay(200)



class SpeedPotion(Object):
    def __init__(self, icon_path: str, size: int = 10, speed: int = 2, active_objects: list = None):
        super().__init__(size)
        self.speed = speed
        self.icon = pygame.image.load(icon_path)
        self.alive = True
        self.active_objects = active_objects

    def draw(self, screen: pygame.surface):
        if not self.placed:
            raise GameExceptions.NotPlacedException
        if not self.alive:
            return
        rect = pygame.Rect(self.position.x+10, self.position.y+10, self.size / 3 * 1.4, self.size / 3)
        pygame.draw.rect(screen, 'green', rect)
        icon_size = (self.size*2, self.size*2)
        icon = pygame.transform.scale(self.icon, icon_size)
        screen.blit(icon, (self.position.x-13, self.position.y-13))

    def handle_collision(self, inventory, player):
        if self.alive and self.position.distance_to(player.position) < (self.size + player.size) / 2:
            cell = Cell(self.icon, 'speed')
            inventory.add_item(cell)
            self._die()

    def _die(self):
        self.alive = False
        if self.active_objects is not None:
            self.active_objects.remove(self)

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
        if self.active_objects is not None:
            self.active_objects.remove(self)



