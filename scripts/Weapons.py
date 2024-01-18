from __future__ import annotations

import pygame
import math
from scripts.Base import load_image


class Weapon:
    def __init__(self, damage: int | float = 10, rate_of_fire: int | float = 1, bullet_speed: int | float = 10,
                 bullet_image_path: str = None):
        if not bullet_image_path:
            return

        self._damage = damage
        self._rate_of_fire = rate_of_fire
        self._bullet_speed = bullet_speed
        self._bullet_image = load_image(bullet_image_path)
        self._bullet_image = pygame.transform.scale(self._bullet_image, (30, 30))
        self._last_shot_time = 0
        # Добавить информацию о размере окна, если она необходима для дальнейших вычислений

    def shoot(self, start_position):
        current_time = pygame.time.get_ticks()
        if current_time - self._last_shot_time > 1000 / self._rate_of_fire:
            self._last_shot_time = current_time
            # Получаем позицию курсора
            target_position = pygame.mouse.get_pos()

            # Вычисляем вектор направления
            direction = pygame.math.Vector2(target_position[0] - start_position.x,
                                            target_position[1] - start_position.y)
            direction = direction.normalize()

            return Bullet(start_position, self._bullet_speed, self._damage, self._bullet_image, direction)
        return


class Bullet:
    def __init__(self, position, speed, damage, image, direction):
        self.position = pygame.math.Vector2(position)
        self.speed = speed
        self.damage = damage
        self.original_image = image
        self.direction = direction

        # Вычисляем угол для поворота спрайта
        angle = self.direction.angle_to(pygame.math.Vector2(1, 0))
        # Поворачиваем спрайт
        self.image = pygame.transform.rotate(self.original_image, angle)
        # Стартовая позиция изображения с учетом поворота
        self.rect = self.image.get_rect(center=self.position)

    def update(self):
        self.position += self.direction * self.speed
        # Обновляем позицию rectangle, используемую для отрисовки
        self.rect.center = self.position

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        self.update()  # Обновление позиции снаряда при каждом вызове рисования.

