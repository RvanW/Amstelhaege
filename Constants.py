import pygame


# Dimensions
tilesPerMetre = 2  # So 1 tile equals 0,5m.. because buildings can be 10,5m
tileSize = 2
mapHeight = 150 * tilesPerMetre
mapWidth = 160 * tilesPerMetre
margin = 400  # set in amount of pixels so we can add menu here

# set up the display
pygame.init()
display = pygame.display.set_mode((mapWidth * tileSize + margin, mapHeight * tileSize))

# Constants representing the different tiles
grass = 0
water = 1
smallHouse = 2
mediumHouse = 3
largeHouse = 4

# a dictionary linking the different houses with their sizes (in tiles, which scale to 1 / tilesPerMetre)
# tuples are build up this way.. house: (width, height, margin)
buildingSizes = {
    smallHouse: (8 * tilesPerMetre, 8 * tilesPerMetre, 2 * tilesPerMetre),
    mediumHouse: (10 * tilesPerMetre, int(7.5 * tilesPerMetre), 3 * tilesPerMetre),
    largeHouse: (11 * tilesPerMetre, int(10.5 * tilesPerMetre), 6 * tilesPerMetre)
}


# a dictionary indicating the price range of the houses and percentile increase in value per extra metre
houseValues = {
    smallHouse: (285000, 0.03),
    mediumHouse: (399000, 0.04),
    largeHouse: (610000, 0.06)
}


# a dictionary linking resources to textures
textures = {
    grass: pygame.image.load('Textures/grass_grid.png'),
    water: pygame.image.load('Textures/water.png'),
    smallHouse: pygame.image.load('Textures/smallhouse.png'),
    mediumHouse: pygame.image.load('Textures/mediumhouse.png'),
    largeHouse: pygame.image.load('Textures/largehouse.png')
}

margin_textures = {
    smallHouse: pygame.image.load('Textures/smallmargin.png'),
    mediumHouse: pygame.image.load('Textures/mediummargin.png'),
    largeHouse: pygame.image.load('Textures/largemargin.png')
}


# colors
colors = {
    "blue": (0, 0, 255),
    "darkblue": (0, 0, 175),
    "red": (180, 28, 36),
    "orange": (234, 94, 0),
    "yellow": (200, 222, 0),
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "green": (1,137,7),
    "lightgrey": (123, 123, 123),
    "darkgrey": (50, 50, 50)
}


