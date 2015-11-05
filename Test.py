import copy
import math
import pygame, sys
import random
from pygame.locals import *

__author__ = 'Robbert'

# Dimensions
tilesPerMetre = 2 # So 1 tiles equals 0,5m.. should add a visible scale at some point
tileSize = 4
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


# Buildings total and ratio
houseAmount = 40


# a dictionary linking the different houses with their sizes (in tiles, which scale to 1 / tilesPerMetre)
# tuples are build up this way.. house: (width, height, margin)
buildingSizes = {
    smallHouse: (8 * tilesPerMetre, 8 * tilesPerMetre, 2 * tilesPerMetre),
    mediumHouse: (10 * tilesPerMetre, 7.5 * tilesPerMetre, 3 * tilesPerMetre),
    largeHouse: (11 * tilesPerMetre, 10.5 * tilesPerMetre, 6 * tilesPerMetre)
}

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
    red: (237,28,36),
    orange: (255,201,14),
    yellow: (255,242,0)

    #white: (255,255,255),
    #black: (0,0,0)
}

# color per building
buildingColors = {
    smallHouse : red,
    mediumHouse: orange,
    largeHouse: yellow
}


# a list representing our base tilemap filled with grass
tilemap = [[grass for w in range(mapWidth)] for h in range(mapHeight)]


# add all requiblue buildings to the tilemap at random positions for now
def placeRandomBuildings():
    buildingList = [largeHouse] * int(houseAmount * 0.15) + [mediumHouse] * int(houseAmount * 0.25) + [smallHouse] * int(houseAmount * 0.6)
    global tilemap
    i = 0
    error = False
    while i != houseAmount and not error:
        randomBuilding = buildingList.pop()
        attempt = 0
        while True:  # selects a random position and check if it's empty (grass).. loops until found empty spot, might be infinite if there's no valid location left
            randomRow = random.randint(buildingSizes[randomBuilding][2], mapHeight - 1 - int(math.ceil(buildingSizes[randomBuilding][1])) - buildingSizes[randomBuilding][2])
            randomColumn = random.randint(buildingSizes[randomBuilding][2], mapWidth - 1 - int(math.ceil(buildingSizes[randomBuilding][0])) - buildingSizes[randomBuilding][2])
            empty = True
            for row in range(randomRow - buildingSizes[randomBuilding][2], int(math.ceil(randomRow + buildingSizes[randomBuilding][1] + buildingSizes[randomBuilding][2])), 1):
                for column in range(randomColumn - buildingSizes[randomBuilding][2], int(math.ceil(randomColumn + buildingSizes[randomBuilding][0]) + buildingSizes[randomBuilding][2]), 1):
                    if tilemap[row][column] != grass:
                        empty = False
                        break
            if empty:
                print("Empty plot found! placing building")
                for row in range(randomRow, int(math.ceil(randomRow + buildingSizes[randomBuilding][1])), 1):
                    for column in range(randomColumn, int(randomColumn + math.ceil(buildingSizes[randomBuilding][0])), 1):
                        tilemap[row][column] = randomBuilding
                i += 1
                break
            else:
                attempt += 1
                print("Not empty! Attempt: ", attempt)
                # to avoid an infinite loop, reset the tilemap and start over at attempt 50000..
                if attempt > 50000:
                    tilemap = [[grass for w in range(mapWidth)] for h in range(mapHeight)]
                    error = True
                    placeRandomBuildings()
                    break




# This function calculates the score based on the margin around and updates the score list
# need to clean this, the score is now based on smallest margin around the 4 sides of a building
global scoreList
scoreList = []

# deep copy the current tilemap and calculate the score
def getScore():
    mapBuffer = copy.deepcopy(tilemap)
    while len(scoreList) < houseAmount:
        for row in range(mapHeight):
            # loop through each tile in the map
            for column in range(mapWidth):
                if mapBuffer[row][column] is None:
                    continue
                elif mapBuffer[row][column] not in (grass, grass2):
                    print("found building! calculating..")
                    foundBuilding = mapBuffer[row][column]
                    buildingScore = 0
                    x = 1
                    found = False
                    # calculate increasingly margin around building in this while loop until hitting another building or end of map
                    while not found:
                        print(x)
                        for marginRow in range(row - x, int(row + x + buildingSizes[foundBuilding][1])):
                            if marginRow < 0 or marginRow > (mapHeight - 1):
                                print("MARGINROW end of map vertical at x=", x)
                                found = True
                                break
                            elif column - x < 0 or column + x + buildingSizes[foundBuilding][0] > mapWidth:
                                print("MARGINROW end of map horizontal at x=", x)
                                found = True
                                break
                            elif mapBuffer[marginRow][column - x] not in (grass, grass2):
                                print("MARGINROW object found left with x of ", x)
                                tilemap[marginRow][column - x] = blue
                                found = True
                                break
                            elif mapBuffer[marginRow][column + x - 1 + buildingSizes[foundBuilding][0]] not in (grass, grass2):
                                print("MARGINROW object found right with x of ", x)
                                tilemap[marginRow][column + x - 1 + buildingSizes[foundBuilding][0]] = blue
                                found = True
                                break
                            else:
                                if x <= buildingSizes[foundBuilding][2]:
                                    tilemap[marginRow][column - x] = buildingColors[foundBuilding]
                                    tilemap[marginRow][column + x - 1 + buildingSizes[foundBuilding][0]] = buildingColors[foundBuilding]
                                else:
                                    tilemap[marginRow][column - x] = grass2
                                    tilemap[marginRow][column + x - 1 + buildingSizes[foundBuilding][0]] = grass2
                                continue
                        if not found:
                            for marginColumn in range(column - x, int(column + x + buildingSizes[foundBuilding][0])):
                                if marginColumn < 0 or marginColumn > (mapWidth - 1):
                                    print("MARGINCOLUMN end of map horizontal at x=", x)
                                    found = True
                                    break
                                elif row - x < 0 or row + x + buildingSizes[foundBuilding][1] > mapHeight:
                                    print("MARGINCOLUMN end of map vertical at x=", x)
                                    found = True
                                    break
                                elif mapBuffer[row - x][marginColumn] not in (grass, grass2):
                                    print("MARGINCOLUMN object collision found downwards at (",row - x, marginColumn)
                                    tilemap[row - x][marginColumn] = blue
                                    found = True
                                    break
                                elif mapBuffer[row + x - 1 + int(buildingSizes[foundBuilding][1])][marginColumn] not in (grass, grass2):
                                    tilemap[row + x - 1 + int(buildingSizes[foundBuilding][1])][marginColumn] = blue
                                    print("MARGINCOLUMN object found upwards with x of ", x)
                                    found = True
                                    break
                                else:
                                    if x <= buildingSizes[foundBuilding][2]:
                                        tilemap[row + x - 1 + int(buildingSizes[foundBuilding][1])][marginColumn] = buildingColors[foundBuilding]
                                        tilemap[row - x][marginColumn] = buildingColors[foundBuilding]
                                    else:
                                        tilemap[row + x - 1 + int(buildingSizes[foundBuilding][1])][marginColumn] = grass2
                                        tilemap[row - x][marginColumn] = grass2
                                    continue
                        if not found: x += 1
                    x -= 1 # because we started with x = 1
                    buildingScore = int(math.floor((x - buildingSizes[foundBuilding][2]) / tilesPerMetre))
                    print buildingScore, " replacing building with none in mapBuffer"
                    # replace all tiles of the building with none so these will be skipped in the rest of our loop
                    for replaceRow in range(row, int(math.ceil(row + buildingSizes[foundBuilding][1])), 1):
                        for replaceColumn in range(column, int(column + math.ceil(buildingSizes[foundBuilding][0])), 1):
                            mapBuffer[replaceRow][replaceColumn] = None

                    textpos = ( column, row )
                    scoreList.append([foundBuilding,buildingScore,textpos])




def update_game_display():
    # loop through each row
    for row in range(mapHeight):
        # loop through each column in the row
        for column in range(mapWidth):
            # draw the resource at that position in the tilemap, using the correct image
            if tilemap[row][column] in textures:
                texture = pygame.transform.scale(textures[tilemap[row][column]],(tileSize,tileSize))
                display.blit(texture, (column * tileSize, row * tileSize))
            elif tilemap[row][column] in colors:
                tile = pygame.Surface((tileSize,tileSize))
                tile.fill((255,255,255, 100))

                pygame.draw.rect(tile, colors[tilemap[row][column]], (0, 0, tileSize, tileSize))
                tile.set_alpha(175)

                display.blit(tile,(column * tileSize, row * tileSize))




    # set up text displaying scores
    # Display some text
    font = pygame.font.Font(None, 36)
    totalValue = 0
    totalScore = 0
    # draw a score on each house and add it's value to total value
    for buildingType, score, position in scoreList:
        scoreText = font.render(str(score), 1, (10, 10, 10))
        totalScore += score
        textpos = scoreText.get_rect()
        textMarginWidth = textpos.width / 2
        textMarginHeight = textpos.height / 2
        centerX = buildingSizes[buildingType][0] / 2 * tileSize - textMarginWidth
        centerY = buildingSizes[buildingType][1] / 2 * tileSize - textMarginHeight
        buildingValue = houseValues[buildingType][0] * (1 + (houseValues[buildingType][1] * score)) # formula to calculate building value here
        display.blit(scoreText, ((position[0] * tileSize + centerX) , (position[1] * tileSize + centerY)))
        totalValue += buildingValue

    totalValueText = font.render("Total value: " + str(totalValue), 1, (250,250,250))
    totalScoreText = font.render("Total (extra) free space: " + str(totalScore), 1, (250,250,250))
    display.blit(totalValueText, (mapWidth * tileSize + 50, (mapHeight * tileSize) / 2 - 50))
    display.blit(totalScoreText, (mapWidth * tileSize + 50, (mapHeight * tileSize) / 2))
    # update the display
    pygame.display.update()


placeRandomBuildings()
getScore()
update_game_display()

running = True
while running:

    # get all the user events
    for event in pygame.event.get():
        # if the user wants to quit
        if event.type == QUIT:
            # and the game and close the window
            pygame.quit()
            sys.exit()