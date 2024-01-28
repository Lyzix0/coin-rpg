from __future__ import annotations

import pygame
from scripts import GameExceptions
from scripts.GameObjects import GameObject
from scripts.Tiles import Tile


class Cell:
    def __init__(self, image: pygame.surface, cell_name: str):
        self.image = image
        self.name = cell_name


class Inventory:
    def __init__(self, screen, player):
        self.cells = {0: None, 1: None, 2: None, 3: None, 4: None, 5: None, 6: None, 7: None, 8: None, 9: None}
        self.screen = screen
        self.height = 50
        self.player = player
        self.width = 500
        self.x = 150
        self.y = 650
        self.inventory_color = (255, 255, 255)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw_inventory(self):
        pygame.draw.rect(self.screen, self.inventory_color, self.rect, 2)
        for _ in range(0, 500, 50):
            pygame.draw.line(self.screen, (255, 255, 255), [150 + _, 650], [150 + _, 700], 3)
        for i in range(min(len(self.cells), 10)):
            if self.cells[i]:
                self.screen.blit(self.cells[i].image, (155 + i * 50, 655))

    def add_item(self, cell: Cell):
        cell.image = pygame.transform.scale(cell.image, (40, 40))
        for i in range(10):
            if self.cells[i] is None:
                self.cells[i] = cell
                break

    def use_by_index(self, index: int):
        if 0 <= index < len(self.cells) and self.cells[index]:
            cell = self.cells[index]
            if cell.name == "heal":
                self.player.apply_healing(20)
                self.cells[index] = None

            if cell.name == "speed":
                self.player.speed *= 1.3
                self.cells[index] = None
                pygame.time.set_timer(pygame.USEREVENT + 1, 20000)


class SpeedPotion(GameObject):
    def __init__(self, icon: str | Tile, size: int = 40, speed: int = 20, active_objects: list = None):
        super().__init__(size)
        self.duration = 20
        self.speed = speed
        if type(icon) == 'str':
            self.icon = pygame.image.load(icon)
        else:
            self.icon = icon.image
        self.alive = True
        self.active_objects = active_objects

    def draw(self, screen: pygame.surface):
        if not self.placed:
            raise GameExceptions.NotPlacedException
        if not self.alive:
            return
        # rect = pygame.Rect(self.position.x, self.position.y, self.size / 3 * 1.4, self.size / 3)
        # pygame.draw.rect(screen, 'green', rect)
        icon_size = (self.size, self.size)
        icon = pygame.transform.scale(self.icon, icon_size)
        screen.blit(icon, (self.position.x - 10, self.position.y - 10))

    def handle_collision(self, inventory, player):
        if self.alive and self.position.distance_to(player.position) < (self.size + player.size) / 2:
            cell = Cell(self.icon, 'speed')
            inventory.add_item(cell)
            self._die()

    def _die(self):
        self.alive = False
        if self.active_objects is not None:
            self.active_objects.remove(self)


class HealingPotion(GameObject):
    def __init__(self, icon: str | Tile, size: int = 40, healing_power: int = 20, active_objects: list = None):
        super().__init__(size)
        self.healing_power = healing_power
        if type(icon) == 'str':
            self.icon = pygame.image.load(icon)
        else:
            self.icon = icon.image
        self.alive = True
        self.active_objects = active_objects

    def draw(self, screen: pygame.surface):
        if not self.placed:
            raise GameExceptions.NotPlacedException
        if not self.alive:
            return
        # rect = pygame.Rect(self.position.x, self.position.y, self.size / 3 * 1.4, self.size / 3)
        # pygame.draw.rect(screen, 'green', rect)
        icon_size = (self.size, self.size)
        icon = pygame.transform.scale(self.icon, icon_size)
        screen.blit(icon, (self.position.x - 10, self.position.y - 10))

    def handle_collision(self, inventory, player):
        if self.alive and self.position.distance_to(player.position) < (self.size + player.size) / 2:
            cell = Cell(self.icon, 'heal')
            inventory.add_item(cell)
            self._die()

    def _die(self):
        self.alive = False
        if self.active_objects is not None:
            self.active_objects.remove(self)



