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

            return PlayerBullet(start_position, self._bullet_speed, self._damage, self._bullet_image, direction)
        return


class PlayerBullet:
    def __init__(self, position, speed, damage, image, direction):
        self.position = pygame.math.Vector2(position)
        self.speed = speed
        self.damage = damage
        self.original_image = image
        self.direction = direction
        self.can_damage = True

        # Вычисляем угол для поворота спрайта
        angle = self.direction.angle_to(pygame.math.Vector2(1, 0))
        # Поворачиваем спрайт
        self.image = pygame.transform.rotate(self.original_image, angle)
        # Стартовая позиция изображения с учетом поворота
        self.rect = self.image.get_rect(center=self.position)

    def update(self, screen, walls):
        if not self.can_damage:
            return

        if walls:
            for wall in walls:
                if wall.rect.collidepoint(self.rect.center):
                    return

        self.position += self.direction * self.speed
        # Обновляем позицию rectangle, используемую для отрисовки
        self.rect.center = self.position
        self._draw(screen=screen)

    def _draw(self, screen):
        screen.blit(self.image, self.rect)


class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, position, direction, speed, damage, image_path):
        super().__init__()
        self.original_image = load_image(image_path, colorkey='white')
        self.rect = self.original_image.get_rect(center=position)
        self.position = pygame.Vector2(position)
        self.direction = direction
        self.speed = speed
        self.damage = damage
        self.img = self.original_image
        self.start_time = pygame.time.get_ticks()
        self.can_damage = True

    def update(self, screen, walls=None):
        if walls:
            for wall in walls:
                if wall.rect.collidepoint(self.rect.center):
                    return

        self.position += self.direction * self.speed
        self.rect.center = self.position
        self.rotate_towards_direction()
        self._draw(screen)

    def rotate_towards_direction(self):
        self.img = pygame.transform.scale(self.img, (40, 40))
        self.rect = self.img.get_rect(center=self.rect.center)

    def _draw(self, screen):
        screen.blit(self.img, self.rect)


class EnemyWeapon:
    def __init__(self, damage: int, fire_rate: int | float, bullet_speed: int, bullet_image_path: str):
        self.damage = damage
        self.fire_rate = fire_rate
        self.bullet_speed = bullet_speed
        self.bullet_img = pygame.image.load(bullet_image_path)
        self.bullet_image = pygame.transform.scale(self.bullet_img, (8, 8))
        self.last_shot_time = 0

    def shoot(self, start_position: pygame.Vector2, target_position: pygame.Vector2):
        now = pygame.time.get_ticks()

        if now - self.last_shot_time > 1000 / self.fire_rate:
            self.last_shot_time = now

            direction = target_position - start_position
            direction.normalize()

            bullet = EnemyBullet(start_position, direction, self.bullet_speed / 50, self.damage,
                                 'images/enemy_bullet.png')

            return bullet
        return None
