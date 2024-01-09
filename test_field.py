import sys
import pygame
from GameObjects import Entity, Form, Direction

pygame.init()

clock = pygame.time.Clock()

running = True

screen_width = 800
screen_height = 600

screen = pygame.display.set_mode((screen_width, screen_height))

pygame.display.set_caption("Test field")

new_player = Entity(form=Form.circle, size=100)
new_player.place((200, 250))

while running:
    screen.fill('black')

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    new_player.draw(screen)
    new_player.draw_health_bar(screen)
    new_player.move(Direction(-1, 1))

    clock.tick(60)
    pygame.display.flip()

pygame.quit()
sys.exit()
