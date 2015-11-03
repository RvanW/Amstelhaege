import copy
import math
import pygame, sys
import random
from pygame.locals import *

__author__ = 'Robbert'

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
grass2 = -1
grass = 0
water = 1
smallHouse = 2
mediumHouse = 3
largeHouse = 4


# Buildings total and ratio
houseAmount = 60


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
    grass: pygame.image.load('grass2.png'),
    grass2: pygame.image.load('grass.png'),
    water: pygame.image.load('water.png'),
    smallHouse: pygame.image.load('smallhouse.png'),
    mediumHouse: pygame.image.load('mediumhouse.png'),
    largeHouse: pygame.image.load('largehouse.png')
}


# a list representing our base tilemap filled with grass
tilemap = [[grass for w in range(mapWidth)] for h in range(mapHeight)]


# add all required buildings to the tilemap at random positions for now
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
                if attempt > 50000:
                    tilemap = [[grass for w in range(mapWidth)] for h in range(mapHeight)]
                    error = True
                    placeRandomBuildings()
                    break

placeRandomBuildings()


# This function calculates the score based on the margin around and updates the score list
# need to do more math here, the score is now based on smallest margin around the 4 sides of a building
global scoreList
scoreList = []

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
                    while not found: # calculate increasingly margin around building in this while loop until hitting another building
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
                                found = True
                                break
                            elif mapBuffer[marginRow][column + x - 1 + buildingSizes[foundBuilding][0]] not in (grass, grass2):
                                print("MARGINROW object found right with x of ", x)
                                found = True
                                break
                            else:
                                # tilemap[marginRow][column - x] = grass2
                                # tilemap[marginRow][column + x - 1 + buildingSizes[foundBuilding][0]] = grass2
                                continue
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
                                print("MARGINCOLUMN object found down with x of ", x)
                                found = True
                                break
                            elif mapBuffer[row + x - 1 + int(buildingSizes[foundBuilding][1])][marginColumn] not in (grass, grass2):
                                print("MARGINCOLUMN object found up with x of ", x)
                                found = True
                                break
                            else:
                                tilemap[row + x - 1 + int(buildingSizes[foundBuilding][1])][marginColumn] = grass2
                                tilemap[row - x][marginColumn] = grass2
                                continue
                        x += 1
                    buildingScore = int(math.floor((x - buildingSizes[foundBuilding][2]) / tilesPerMetre))
                    print buildingScore, " replacing building with none in mapBuffer"
                    for replaceRow in range(row, int(math.ceil(row + buildingSizes[foundBuilding][1])), 1):
                        for replaceColumn in range(column, int(column + math.ceil(buildingSizes[foundBuilding][0])), 1):
                            mapBuffer[replaceRow][replaceColumn] = None

                    textpos = ( column, row )
                    print textpos
                    scoreList.append([foundBuilding,buildingScore,textpos])

getScore()


def update_game_display():
    # loop through each row
    for row in range(mapHeight):
        # loop through each column in the row
        for column in range(mapWidth):
            # draw the resource at that position in the tilemap, using the correct image
            if tilemap[row][column] in textures:
                display.blit(textures[tilemap[row][column]], (column * tileSize, row * tileSize))
            else:
                display.blit()


    # set up text displaying scores
    # Display some text
    font = pygame.font.Font(None, 36)
    totalValue = 0
    totalScore = 0
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
    totalScoreText = font.render("Total free space: " + str(totalScore), 1, (250,250,250))
    display.blit(totalValueText, (mapWidth * tileSize + 50, (mapHeight * tileSize) / 2 - 50))
    display.blit(totalScoreText, (mapWidth * tileSize + 50, (mapHeight * tileSize) / 2))
    # update the display
    pygame.display.update()

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




