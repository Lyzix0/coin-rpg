import enum
import os
import sys
import pygame
from scripts import GameExceptions


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


def load_image(path: str, colorkey='black'):
    # если файл не существует, то выходим
    if not os.path.isfile(path):
        print(f"Файл с изображением '{path}' не найден")
        sys.exit()
    image = pygame.image.load(path)

    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def rotate(img, pos, angle):
    w, h = img.get_size()
    img2 = pygame.Surface((w*2, h*2), pygame.SRCALPHA)
    img2.blit(img, (w-pos[0], h-pos[1]))
    return pygame.transform.rotate(img2, angle)