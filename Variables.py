import pygame

# Dimensions
tilesPerMetre = 2 # So 1 tiles equals 0,5m.. should add a visible scale at some point
tileSize = 2
mapHeight = 150 * tilesPerMetre
mapWidth = 160 * tilesPerMetre
margin = 400 # set in amount of pixels so we can add menu here later

# set up the display
pygame.init()
display = pygame.display.set_mode((mapWidth * tileSize + margin, mapHeight * tileSize))

# Constants representing the different tiles
yellow = -5
orange = -4
red = -3
blue = -2 # for testing collision
grass2 = -1
grass = 0
water = 1
smallHouse = 2
mediumHouse = 3
largeHouse = 4

# a dictionary indicating the price range of the houses
houseValues = {
    smallHouse: (285000, 0.03),
    mediumHouse: (399000, 0.04),
    largeHouse: (610000, 0.06)
}

# a dictionary linking resources to textures
textures = {
    grass: pygame.image.load('grass.png'),
    grass2: pygame.image.load('grass2.png'),
    water: pygame.image.load('water.png'),
    smallHouse: pygame.image.load('smallhouse.png'),
    mediumHouse: pygame.image.load('mediumhouse.png'),
    largeHouse: pygame.image.load('largehouse.png')
}

# colors
colors = {
    blue: (0,0,255),
    red: (180,28,36),
    orange: (234,94,0),
    yellow: (200,222,0),
    "white": (255,255,255),
    "black": (0,0,0)
}

# color per building
buildingColors = {
    smallHouse : red,
    mediumHouse: orange,
    largeHouse: yellow
}
