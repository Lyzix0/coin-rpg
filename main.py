import sys
import math
import random
import pygame


# Инициализация Pygame
pygame.init()
clock = pygame.time.Clock()
# Установка размеров экрана
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Dumb rpg")

# Параметры игрока
player_radius = 25
player_pos = [screen_width // 2, screen_height // 2]
player_speed = 0.5  # Уменьшили скорость игрока
player_health = 100
coins_collected = 0

# Параметры врагов
enemy_size = 50
enemies = []
enemy_speed = 0.1  # Уменьшили скорость врагов
enemy_health = 100
enemy_bullet_cooldown = 1000  # Задержка между выстрелами врагов (в миллисекундах)
last_enemy_shot = pygame.time.get_ticks()

# Скорость снарядов
bullet_speed = 1
bullet_cooldown = 300  # Задержка между выстрелами (в миллисекундах)
last_shot = pygame.time.get_ticks()

enemy_bullets = []
bullets = []  # Список для хранения пуль
coins = []  # Список для хранения монеток
trail = []

enemy_triangle_speed = 0.05  # Например, установим скорость треугольников в 0.05 (вы можете выбрать другое значение)

player_health_upgrade_cost = 20
player_damage_upgrade_cost = 30
bullet_stream_upgrade_cost = 25

count_of_pop = 1
bullets_from_player = []
bullets_from_enemies = []


def show_menu():
    global player_health, bullet_cooldown, bullet_speed, player_health_upgrade_cost, player_damage_upgrade_cost, bullet_stream_upgrade_cost, coins_collected, count_of_pop

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return "game"  # Возвращаемся к игре после нажатия Enter
                elif event.key == pygame.K_1:
                    if coins_collected >= player_health_upgrade_cost:
                        player_health += 20  # Увеличиваем здоровье
                        coins_collected -= player_health_upgrade_cost  # Уменьшаем количество монеток
                        player_health_upgrade_cost += 10  # Увеличиваем стоимость улучшения здоровья
                elif event.key == pygame.K_2:
                    if coins_collected >= player_damage_upgrade_cost:
                        bullet_speed += 1
                        if bullet_cooldown - 100 >= 0:
                            bullet_cooldown -= 100
                        coins_collected -= player_damage_upgrade_cost
                        player_damage_upgrade_cost += 15  # Увеличиваем стоимость улучшения урона
                elif event.key == pygame.K_3:
                    if coins_collected >= bullet_stream_upgrade_cost:
                        count_of_pop += 1
                        coins_collected -= bullet_stream_upgrade_cost
                        bullet_stream_upgrade_cost += 12  # Увеличиваем стоимость улучшения потока пуль

        # Рисуем меню
        screen.fill('black')
        font = pygame.font.Font(None, 50)
        text = font.render("Game Over", True, 'red')
        text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2 - 50))
        screen.blit(text, text_rect)

        font = pygame.font.Font(None, 36)
        text = font.render("Press Enter to Play Again", True, 'green')
        text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2 + 50))
        screen.blit(text, text_rect)

        font = pygame.font.Font(None, 36)
        text = font.render("Press '1' to Upgrade Health", True, 'blue')
        text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2 + 100))
        screen.blit(text, text_rect)

        text = font.render(f"Cost: {player_health_upgrade_cost} coins", True, 'blue')
        text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2 + 130))
        screen.blit(text, text_rect)

        text = font.render("Press '2' to Upgrade speed", True, 'blue')
        text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2 + 170))
        screen.blit(text, text_rect)

        text = font.render(f"Cost: {player_damage_upgrade_cost} coins", True, 'blue')
        text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2 + 200))
        screen.blit(text, text_rect)

        text = font.render("Press '3' to Upgrade Bullet Stream", True, 'blue')
        text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2 + 240))
        screen.blit(text, text_rect)

        text = font.render(f"Cost: {bullet_stream_upgrade_cost} coins", True, 'blue')
        text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2 + 270))
        screen.blit(text, text_rect)

        text = font.render(f"Coins: {coins_collected}", True, 'green')
        screen.blit(text, (10, 10))

        pygame.display.update()


# Функция рисования персонажа и врагов
def draw_objects():
    screen.fill('black')
    pygame.draw.circle(screen, 'green', (player_pos[0], player_pos[1]), player_radius)
    pygame.draw.rect(screen, (0, 128, 0), (
        player_pos[0] - player_radius, player_pos[1] + 30, (player_health / 100) * (player_radius * 2), 5))
    for enemy in enemies:
        if enemy[3] != 4:
            pygame.draw.rect(screen, 'red', (enemy[0], enemy[1], enemy_size, enemy_size))
            # Хитбар врага (зеленая полоса)
            pygame.draw.rect(screen, (0, 128, 0), (enemy[0], enemy[1] - 10, (enemy[2] / 100) * enemy_size, 5))
    for bullet in bullets:
        pygame.draw.rect(screen, 'red', (bullet[0], bullet[1], 5, 5))
    for coin in coins:
        pygame.draw.circle(screen, 'yellow', (coin[0], coin[1]), 8)  # Увеличил размер монетки
    font = pygame.font.Font(None, 36)
    text = font.render(f"Coins: {coins_collected}", True, 'green')  # Отображение счетчика монеток
    screen.blit(text, (10, 10))
    for enemy in enemies:
        if enemy[3] == 4:  # Проверяем тип врага (гибрид)
            # Отрисовка хит-бара для гибридов
            pygame.draw.rect(screen, (0, 128, 0),
                             (enemy[0],
                              enemy[1] + enemy_size + 10,
                              (enemy[2] / (enemy_health * 2)) * enemy_size / 2, 5))

            pygame.draw.polygon(screen, 'blue', [
                (enemy[0], enemy[1] + enemy_size),
                (enemy[0] + enemy_size, enemy[1] + enemy_size),
                (enemy[0] + (enemy_size / 2), enemy[1])
            ])
        else:  # Для других типов врагов оставляем прежнюю логику
            pygame.draw.rect(screen, (0, 128, 0), (enemy[0], enemy[1] - 10, (enemy[2] / enemy_health) * enemy_size, 5))
            pygame.draw.rect(screen, 'red', (enemy[0], enemy[1], enemy_size, enemy_size))

    # Отрисовка игрока
    pygame.draw.circle(screen, 'green', (player_pos[0], player_pos[1]), player_radius)

    # Отрисовка следа
    for i, point in enumerate(trail):
        alpha = 255 - (i * 5)
        if alpha < 0:
            alpha = 0
        pygame.draw.circle(screen, (255, 255, 255, alpha), (point[0], point[1]), player_radius)


def reset_game():
    global player_radius, player_pos, player_speed, player_health, coins_collected, enemy_size, enemies, enemy_speed, enemy_health, enemy_bullet_cooldown, last_enemy_shot, bullet_speed, bullet_cooldown, last_shot, bullets, coins, spawn_rate
    player_radius = 25
    player_pos = [screen_width // 2, screen_height // 2]
    player_health = 100
    spawn_rate = 5000
    # Параметры врагов
    enemy_size = 50
    enemies = []
    enemy_speed = 0.1  # Уменьшили скорость врагов
    enemy_health = 100
    enemy_bullet_cooldown = 1000  # Задержка между выстрелами врагов (в миллисекундах)
    last_enemy_shot = pygame.time.get_ticks()

    bullets = []  # Список для хранения пуль
    coins = []  # Список для хранения монеток


def generate_enemies():
    side = random.randint(1, 4)  # Случайно выбираем сторону, с которой появится враг
    if side == 1:  # Слева
        enemy_x = -enemy_size
        enemy_y = random.randint(0, screen_height - enemy_size)
    elif side == 2:  # Сверху
        enemy_x = random.randint(0, screen_width - enemy_size)
        enemy_y = -enemy_size
    elif side == 3:  # Справа
        enemy_x = screen_width
        enemy_y = random.randint(0, screen_height - enemy_size)
    else:  # Снизу
        enemy_x = random.randint(0, screen_width - enemy_size)
        enemy_y = screen_height
    global spawn_rate
    spawn_rate = max(2000, spawn_rate - 100)
    # Проверяем на пересечения между разными типами врагов
    for enemy in enemies:
        distance = math.sqrt((enemy_x - enemy[0]) ** 2 + (enemy_y - enemy[1]) ** 2)
        if distance < enemy_size * 2:
            return  # Если пересекаются, прекращаем создание врага

    # Добавляем нового врага в список
    if len(enemies) < max_enemies:
        if random.random() < 0.5:  # 50% шанс создать красного врага
            enemies.append([enemy_x, enemy_y, enemy_health, 1])  # 1 для красного врага
        else:
            enemies.append([enemy_x, enemy_y, enemy_health * 4, 4])  # 4 для синего врага (с большим здоровьем)


# Параметры для увеличения сложности со временем
time_passed = 0
spawn_rate = 5000  # Интервал для появления новых врагов (в миллисекундах)
enemy_speed_increment = 0.01  # Увеличение скорости врагов со временем
max_enemies = 20  # Максимальное количество врагов

# Время последнего обновления
last_time = pygame.time.get_ticks()

game_over = False


# Главный игровой цикл
while True:
    if game_over:
        next_action = show_menu()
        if next_action == "game":
            reset_game()
            game_over = False
        elif next_action == "shop":
            # Здесь можно добавить функционал для перехода в магазин
            pass

    current_time = pygame.time.get_ticks()
    time_passed += current_time - last_time
    last_time = current_time

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Стрельба игрока
    if pygame.mouse.get_pressed()[0]:  # Стрельба при нажатии левой кнопки мыши
        speed_2 = 0
        if current_time - last_shot > bullet_cooldown:
            for i in range(count_of_pop):
                mouse_x, mouse_y = pygame.mouse.get_pos()
                angle = math.atan2(mouse_y - player_pos[1], mouse_x - player_pos[0])
                bullet_x = player_pos[0] + player_radius * math.cos(angle)  # Вычисляем начальные координаты пули
                bullet_y = player_pos[1] + player_radius * math.sin(angle)
                bullet_dx = bullet_speed * math.cos(angle)
                bullet_dy = bullet_speed * math.sin(angle)
                if (mouse_x > screen_width // 2 and mouse_y < screen_height // 2) or (
                        mouse_x < screen_width // 2 and mouse_y > screen_height // 2):
                    new_bullet = [bullet_x, bullet_y, bullet_dx + speed_2, bullet_dy + speed_2]
                else:
                    new_bullet = [bullet_x, bullet_y, bullet_dx + speed_2, bullet_dy - speed_2]
                bullets.append(new_bullet)
                bullets_from_player.append(new_bullet)
                last_shot = current_time
                speed_2 += (0.1 * -1)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a] and player_pos[0] > player_radius:
        player_pos[0] -= player_speed
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a] and player_pos[0] > player_radius:
        player_pos[0] -= player_speed
    if keys[pygame.K_d] and player_pos[0] < screen_width - player_radius:
        player_pos[0] += player_speed
    if keys[pygame.K_w] and player_pos[1] > player_radius:
        player_pos[1] -= player_speed
    if keys[pygame.K_s] and player_pos[1] < screen_height - player_radius:
        player_pos[1] += player_speed

    keys = pygame.key.get_pressed()

    trail.append(player_pos.copy())
    # Обновление координат врагов
    for enemy in enemies:
        dir_x = player_pos[0] - enemy[0]
        dir_y = player_pos[1] - enemy[1]
        distance = math.sqrt(dir_x ** 2 + dir_y ** 2)
        dir_x /= distance if distance != 0 else 1
        dir_y /= distance if distance != 0 else 1
        enemy[0] += dir_x * enemy_speed
        enemy[1] += dir_y * enemy_speed

        # Стрельба врагов
        if current_time - last_enemy_shot > enemy_bullet_cooldown:  # Задержка между выстрелами врагов
            for enemy in enemies:
                angle = math.atan2(player_pos[1] - enemy[1], player_pos[0] - enemy[0])
                bullet_dx = bullet_speed * math.cos(angle)
                bullet_dy = bullet_speed * math.sin(angle)
                bullets.append([enemy[0], enemy[1], bullet_dx, bullet_dy])
                bullets_from_enemies.append([enemy[0], enemy[1], bullet_dx, bullet_dy])
                last_enemy_shot = current_time

        if enemy[2] <= 0:  # Проверяем, если у треугольника закончились жизни
            coins.append([enemy[0], enemy[1]])  # Добавляем первую монетку
            coins.append([enemy[0], enemy[1]])  # Добавляем вторую монетку
            enemies.remove(enemy)  # Удаляем треугольник из списка врагов
            break  # Прерываем цикл, чтобы избежать проверки после удаления

        else:  # Для других типов врагов оставляем прежнюю логику
            enemy[0] += dir_x * enemy_speed
            enemy[1] += dir_y * enemy_speed

            # Стрельба других врагов
            if current_time - last_enemy_shot > enemy_bullet_cooldown:
                angle = math.atan2(player_pos[1] - enemy[1], player_pos[0] - enemy[0])
                bullet_dx = bullet_speed * math.cos(angle)
                bullet_dy = bullet_speed * math.sin(angle)
                bullets.append([enemy[0], enemy[1], bullet_dx, bullet_dy])
                bullets_from_enemies.append([enemy[0], enemy[1], bullet_dx, bullet_dy])
                last_enemy_shot = current_time

    # Обновление координат пуль
    for bullet in bullets:
        bullet[0] += bullet[2]
        bullet[1] += bullet[3]

    # Удаление пуль, вышедших за пределы экрана
    bullets = [bullet for bullet in bullets if 0 < bullet[0] < screen_width and 0 < bullet[1] < screen_height]

    # Обработка коллизий между пулями и игроком
    for bullet in bullets:
        if math.hypot(bullet[0] - player_pos[0], bullet[1] - player_pos[1]) < player_radius:
            player_health -= 10
            bullets.remove(bullet)
            break  # Прерываем цикл, чтобы избежать проверки после удаления

    for enemy in enemies:
        for bullet in bullets:
            if (enemy[0] < bullet[0] < enemy[0] + enemy_size) and (enemy[1] < bullet[1] < enemy[1] + enemy_size):
                # Проверяем, стреляет ли игрок или враг
                if bullet in bullets_from_player:
                    enemy[2] -= 20  # Уменьшение жизней врага при попадании пули от игрока
                    if enemy[2] <= 0:
                        coins.append([enemy[0], enemy[1], enemy[3]])  # Добавляем монетку при убийстве врага
                    bullets.remove(bullet)  # Удаление пули при попадании
                elif bullet in bullets_from_enemies:  # Добавим проверку на пули, выпущенные другими врагами
                    pass  # Здесь можно добавить логику игнорирования пуль врагов при попадании
                else:
                    bullets.remove(bullet)  # Убираем пули, если враг стреляет
                break  # Прерываем цикл, чтобы избежать проверки после удаления

    # Удаление врагов, у которых закончились жизни
    enemies = [enemy for enemy in enemies if enemy[2] > 0]

    # Подбор монеток игроком
    for coin in coins:
        if math.hypot(coin[0] - player_pos[0], coin[1] - player_pos[1]) < player_radius:
            coins_collected += 1
            coins.remove(coin)
            # Здесь может быть функционал подбора монетки
            # Например, можно увеличить счет игрока или что-то еще

    # Увеличение сложности игры со временем
    if time_passed > spawn_rate and len(enemies) < max_enemies:
        generate_enemies()
        time_passed = 0
        enemy_speed += enemy_speed_increment

    # Ограничение длины следа
    if len(trail) > 50:
        trail.pop(0)  # Удаление самой старой точки из следа

    # Отрисовка следа
    for i, point in enumerate(trail):
        alpha = 255 - (i * 5)  # Уменьшение прозрачности по мере удаления от текущей позиции игрока
        if alpha < 0:
            alpha = 0
        pygame.draw.circle(screen, (255, 255, 255, alpha), (point[0], point[1]), player_radius)

    # Проверка на поражение игрока
    if player_health <= 0:
        game_over = True

    # Обновление экрана и объектов
    draw_objects()

    # new_player.draw(screen)
    # new_player.draw_health_bar(screen)

    pygame.display.flip()
    clock.tick(500)
    pygame.display.update()
