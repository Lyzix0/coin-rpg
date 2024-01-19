import time

import pygame

from scripts import GameExceptions
from scripts.GameObjects import Object
from scripts.Inventory import Cell


class Trap(Object):
    def __init__(self, icon_path: str, size: int = 10, effect: str = "damage", power: int = 10, cooldown_time: int = 2,
                 active_objects: list = None):
        super().__init__(size)
        self.effect = effect
        self.power = power
        self.icon = pygame.image.load(icon_path)
        self.alive = True
        self.active_objects = active_objects
        self.cooldown_time = cooldown_time
        self.last_activation_time = 0

    def draw(self, screen: pygame.surface):
        if not self.placed:
            raise GameExceptions.NotPlacedException

        if not self.alive:
            return

        rect = pygame.Rect(self.position.x, self.position.y, self.size / 3 * 1.4, self.size / 3)
        pygame.draw.rect(screen, 'gray', rect)
        icon_size = (self.size, self.size)
        icon = pygame.transform.scale(self.icon, icon_size)
        screen.blit(icon, (self.position.x - 10, self.position.y - 8))

    def handle_collision(self, inventory, player):
        current_time = time.time()

        if self.alive and current_time - self.last_activation_time > self.cooldown_time:
            if self.position.distance_to(player.position) < (self.size / 2 + player.size / 2) / 2:
                if self.effect == "damage":
                    player.take_damage(self.power)
                elif self.effect == "poison":
                    player.apply_poison_effect(duration=self.duration)

                # Update last activation time
                self.last_activation_time = current_time

    def _die(self):
        self.alive = False
        if self.active_objects is not None:
            self.active_objects.remove(self)
