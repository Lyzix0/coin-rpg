import pygame
from scripts.Base import load_image
from scripts.Tiles import TileImages, TileMap, Tile

# Initialize Pygame
pygame.init()

# Set up display
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Simple Map Editor")

# Set up TileImages and TileMap
tile_images = TileImages()
tile_images.load_tile_images({
    "grass": "images/grass.png",  # Replace with the actual path to your grass tile image
    "water": "images/dirt.jpg",  # Replace with the actual path to your water tile image
    # Add more tiles as needed
})

tile_map = TileMap()
tile_map.load_tilemap("images/tilesets/Dungeon_Tileset.png", rows=3, cols=3, tile_size=32)  # Replace with the actual path to your spritesheet

# Set up variables for the map editor
map_width, map_height = 20, 15  # Change as needed
tile_size = 32

# Create an empty map
empty_map = [["" for _ in range(map_width)] for _ in range(map_height)]

# Main loop
running = True
current_tile_index = 0  # Initial tile index
current_tile = tile_map.get_tile(current_tile_index, 0)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button to place tiles
                tile_x = event.pos[0] // tile_size
                tile_y = event.pos[1] // tile_size
                if 0 <= tile_x < map_width and 0 <= tile_y < map_height:
                    new_tile = tile_map.get_tile(current_tile_index, 0)
                    new_tile.rect = pygame.Rect(tile_x * tile_size, tile_y * tile_size, 32, 32)
                    tile_map.add_tile(new_tile)
                    empty_map[tile_y][tile_x] = current_tile
            elif event.button == 3:  # Right mouse button to remove tiles
                tile_x = event.pos[0] // tile_size
                tile_y = event.pos[1] // tile_size
                if 0 <= tile_x < map_width and 0 <= tile_y < map_height:
                    # Remove tile at the clicked position
                    tile_map.current_tile_map = [tile for tile in tile_map.current_tile_map
                                                 if tile.x != tile_x * tile_size or tile.y != tile_y * tile_size]
                    empty_map[tile_y][tile_x] = ""

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                current_tile_index = (current_tile_index - 1) % tile_map.get_tile(current_tile_index, 0)
            elif event.key == pygame.K_RIGHT:
                current_tile_index = (current_tile_index + 1) % tile_map.get_tile(current_tile_index, 0)
            current_tile_type = tile_map.get_tile(current_tile_index, 0)
            current_tile.image = tile_map.get_tile(current_tile_index, 0)

    # Draw the map
    screen.fill((255, 255, 255))  # Fill the screen with white background
    tile_map.draw_all_tiles(screen)
    tile_map.draw_tiles(screen)

    # Draw the current tile for preview
    screen.blit(current_tile.image, pygame.mouse.get_pos())

    pygame.display.flip()

pygame.quit()