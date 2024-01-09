import pygame
from classes.Base import load_image


class Weapon:
    def __init__(self, damage: int | float = 10, rate_of_fire: int | float = 1, bullet_speed: int | float = 10,
                 bullet_image_path: str = None):
        if not bullet_image_path:
            return

        self._damage = damage  # Урон от одного выстрела
        self._rate_of_fire = rate_of_fire  # Скорострельность (выстрелов в секунду)
        self._bullet_speed = bullet_speed  # Скорость полета снаряда
        self._bullet_image = load_image(bullet_image_path)  # Изображение снаряда
        self._bullet_image = pygame.transform.scale(self._bullet_image, (100, 100))
        self._last_shot_time = 0  # Время последнего выстрела

    def shoot(self, start_position):
        """
        Метод для совершения выстрела из оружия.

        :param start_position: начальная позиция снаряда (где находится стрелок)
        :return: объект Bullet или None, если нельзя стрелять из-за скорострельности
        """
        current_time = pygame.time.get_ticks()
        if current_time - self._last_shot_time > 1000 / self._rate_of_fire:
            self._last_shot_time = current_time
            return Bullet(start_position, self._bullet_speed, self._damage, self._bullet_image)
        return


class Bullet:
    def __init__(self, position, speed, damage, image):
        self.position = position
        self.speed = speed
        self.damage = damage
        self.image = image

    def draw(self, screen):
        # Отрисовка снаряда на экране
        screen.blit(self.image, self.position)
        self.position.x += self.speed
