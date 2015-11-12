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
houseAmount = 20


# a dictionary linking the different houses with their sizes (in tiles, which scale to 1 / tilesPerMetre)
# tuples are build up this way.. house: (width, height, margin)
buildingSizes = {
    smallHouse: (8 * tilesPerMetre, 8 * tilesPerMetre, 2 * tilesPerMetre),
    mediumHouse: (10 * tilesPerMetre, int(7.5 * tilesPerMetre), 3 * tilesPerMetre),
    largeHouse: (11 * tilesPerMetre, int(10.5 * tilesPerMetre), 6 * tilesPerMetre)
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


# clears all layers
def initialize_tilemaps():
    global tileMap
    # a list representing our base tileMap filled with grass
    tileMap = [[grass for w in range(mapWidth)] for h in range(mapHeight)]
    global tilemap_required_margins
    # another tilemap layer representing the required margins
    tilemap_required_margins = [[None for w in range(mapWidth)] for h in range(mapHeight)]
    # any extra space around the margin that is calculated goes in this layer
    global tilemap_extra_space
    tilemap_extra_space = [[None for w in range(mapWidth)] for h in range(mapHeight)]
initialize_tilemaps()


def check_valid_location(row,column,buildingType,map):
    for y in range(row - buildingSizes[buildingType][2], int(math.ceil(row + buildingSizes[buildingType][1] + buildingSizes[buildingType][2])), 1):
        for x in range(column - buildingSizes[buildingType][2], int(math.ceil(column + buildingSizes[buildingType][0]) + buildingSizes[buildingType][2]), 1):
            if x > mapWidth - 1 or y > mapHeight - 1:
                return False
            elif map[y][x] != grass:
                return False
    return True


def place_building(place_row,place_column,buildingType,map):
    for row in range(place_row, int(math.ceil(place_row + buildingSizes[buildingType][1])), 1):
        for column in range(place_column, int(place_column + math.ceil(buildingSizes[buildingType][0])), 1):
            map[row][column] = buildingType


# add all required buildings to the tileMap at random positions for now
def placeRandomBuildings():
    global tileMap
    global tilemap_required_margins
    # build up an array with all the required buildings
    buildingList = [largeHouse] * int(houseAmount * 0.15) + [mediumHouse] * int(houseAmount * 0.25) + [smallHouse] * int(houseAmount * 0.6)
    # reset tilemaps
    initialize_tilemaps()
    # i = amount of houses found
    i = 0
    error = False
    while i != houseAmount and not error:
        randomBuilding = buildingList.pop()
        attempt = 0
        while True:  # selects a random position and check if it's empty (grass).. loops until found empty spot, might be infinite if there's no valid location left
            randomRow = random.randint(buildingSizes[randomBuilding][2], mapHeight - 1 - int(math.ceil(buildingSizes[randomBuilding][1])) - buildingSizes[randomBuilding][2])
            randomColumn = random.randint(buildingSizes[randomBuilding][2], mapWidth - 1 - int(math.ceil(buildingSizes[randomBuilding][0])) - buildingSizes[randomBuilding][2])

            if check_valid_location(randomRow,randomColumn,randomBuilding, tileMap) is True:
                print("Empty plot found! placing building")
                place_building(randomRow,randomColumn,randomBuilding,tileMap)
                i += 1
                break
            else:
                attempt += 1
                print("Not empty! Attempt: ", attempt)
                # to avoid an infinite loop, reset the tileMap and start over at attempt 50000..
                if attempt > 50000:
                    tileMap = [[grass for w in range(mapWidth)] for h in range(mapHeight)]
                    error = True
                    placeRandomBuildings()
                    break
    getScore(tileMap)
    update_game_display()



# This function calculates the score based on the margin around and updates the score list

# deep copy the current tileMap and calculate the score
def getScore(map,update_margin = True):
    totalValue, totalScore = 0,0
    global scoreList


    global tilemap_required_margins
    global tilemap_extra_space
    # reset our global margin tilemaps if we want to update it
    if update_margin is True:
        scoreList = []
        tilemap_required_margins = [[None for w in range(mapWidth)] for h in range(mapHeight)]
        tilemap_extra_space = [[None for w in range(mapWidth)] for h in range(mapHeight)]

    mapBuffer = copy.deepcopy(map)
    while len(scoreList) < houseAmount:
        for row in range(mapHeight):
            # loop through each tile in the map
            for column in range(mapWidth):
                if mapBuffer[row][column] is None:
                    continue
                elif mapBuffer[row][column] > water:
                    # we've found a new building
                    foundBuilding = mapBuffer[row][column]
                    x = 0 # x is used to keep track of the margin that is build up around the house
                    found = False
                    # calculate increasingly margin around building in this while loop until hitting another building or end of map
                    while not found:
                        x += 1
                        # For each row in range of the size + x and - x
                        for marginRow in range(row - x, int(row + x + buildingSizes[foundBuilding][1])):
                            # End of map was found was found vertically
                            if marginRow < 0 or marginRow > (mapHeight - 1):
                                # print("MARGINROW end of map vertical at x=", x)
                                found = True
                                break
                            # end of map was found horizontally
                            elif column - x < 0 or column + x + buildingSizes[foundBuilding][0] > mapWidth:
                                # print("MARGINROW end of map horizontal at x=", x)
                                found = True
                                break
                            # Collision with a house found on the left side
                            elif mapBuffer[marginRow][column - x] not in (grass, grass2):
                                # print("MARGINROW object found left with x of ", x)
                                # tileMap[marginRow][column - x] = blue
                                found = True
                                break
                            # Collision with a house found on the right side (could be joined into 1 statement with left)
                            elif mapBuffer[marginRow][column + x - 1 + buildingSizes[foundBuilding][0]] not in (grass, grass2):
                                # print("MARGINROW object found right with x of ", x)
                                # tileMap[marginRow][column + x - 1 + buildingSizes[foundBuilding][0]] = blue
                                found = True
                                break
                            # If the surrounding tiles pass these tests, they are empty..
                            # Do we want to update the arrays storing margins?
                            elif update_margin is True:
                                # if the margin is within the required space..
                                if x <= buildingSizes[foundBuilding][2]:
                                    tilemap_required_margins[marginRow][column - x] = buildingColors[foundBuilding]
                                    tilemap_required_margins[marginRow][column + x - 1 + buildingSizes[foundBuilding][0]] = buildingColors[foundBuilding]
                                else:
                                    tilemap_extra_space[marginRow][column - x] = grass2
                                    tilemap_extra_space[marginRow][column + x - 1 + buildingSizes[foundBuilding][0]] = grass2
                                continue
                            # If not, just continue to check columns
                            else:
                                continue
                        if not found:
                            # column + 1 and - 1 because this tile was already checked in marginRows
                            for marginColumn in range(column - x + 1, int(column + x - 1 + buildingSizes[foundBuilding][0])):
                                if mapBuffer[row - x][marginColumn] not in (grass, grass2):
                                    # print("MARGINCOLUMN object collision found downwards at (",row - x, marginColumn)
                                    # tileMap[row - x][marginColumn] = blue
                                    found = True
                                    break
                                elif mapBuffer[row + x - 1 + int(buildingSizes[foundBuilding][1])][marginColumn] not in (grass, grass2):
                                    # tileMap[row + x - 1 + int(buildingSizes[foundBuilding][1])][marginColumn] = blue
                                    # print("MARGINCOLUMN object found upwards with x of ", x)
                                    found = True
                                    break
                                elif update_margin is True:
                                    if x <= buildingSizes[foundBuilding][2]:
                                        tilemap_required_margins[row + x - 1 + int(buildingSizes[foundBuilding][1])][marginColumn] = buildingColors[foundBuilding]
                                        tilemap_required_margins[row - x][marginColumn] = buildingColors[foundBuilding]
                                    else:
                                        tilemap_extra_space[row + x - 1 + int(buildingSizes[foundBuilding][1])][marginColumn] = grass2
                                        tilemap_extra_space[row - x][marginColumn] = grass2
                                    continue
                                else:
                                    continue
                    buildingScore = int(math.floor((x - buildingSizes[foundBuilding][2]) / tilesPerMetre))
                    totalValue += houseValues[foundBuilding][0] * (1 + (houseValues[foundBuilding][1] * buildingScore)) # formula to calculate building value here
                    # replace all tiles of the building with none so these will be skipped in the rest of our loop
                    for replaceRow in range(row, int(math.ceil(row + buildingSizes[foundBuilding][1])), 1):
                        for replaceColumn in range(column, int(column + math.ceil(buildingSizes[foundBuilding][0])), 1):
                            mapBuffer[replaceRow][replaceColumn] = None

                    textpos = ( column, row )
                    if update_margin is True:
                        scoreList.append([foundBuilding,buildingScore,textpos])

    return totalValue



# this function displays the tileMap onto the screen
def update_game_display():
    # loop through each row
    for row in range(mapHeight):
        # loop through each column in the row
        for column in range(mapWidth):
            # draw the resource at that position in the tileMap, using the correct image
            if tileMap[row][column] in textures:
                texture = pygame.transform.scale(textures[tileMap[row][column]],(tileSize,tileSize))
                display.blit(texture, (column * tileSize, row * tileSize))
            # if it's not a texture use a color
            elif tileMap[row][column] in colors:
                tile = pygame.Surface((tileSize,tileSize))
                tile.fill((255,255,255, 100))
                pygame.draw.rect(tile, colors[tileMap[row][column]], (0, 0, tileSize, tileSize))
                display.blit(tile,(column * tileSize, row * tileSize))

    # set up font displaying score and value
    font = pygame.font.Font("freesansbold.ttf",20)
    totalValue = 0
    totalScore = 0
    # draw a score on the center of each house and add it's value to total value
    for buildingType, score, position in scoreList:
        scoreText = font.render(str(score), 1, (10, 10, 10))
        totalScore += score
        textpos = scoreText.get_rect()
        centerX = buildingSizes[buildingType][0] / 2 * tileSize - textpos.width / 2
        centerY = buildingSizes[buildingType][1] / 2 * tileSize - textpos.height / 2
        buildingValue = houseValues[buildingType][0] * (1 + (houseValues[buildingType][1] * score)) # formula to calculate building value here
        display.blit(scoreText, ((position[0] * tileSize + centerX) , (position[1] * tileSize + centerY)))
        totalValue += buildingValue

    # Display the total calculated value and the total score (extra free space)
    totalValueText = font.render("Total value: " + str(totalValue) + "    ", 1, (250,250,250), (0,0,0))
    totalScoreText = font.render("Total (extra) free space: " + str(totalScore) + "    ", 1, (250,250,250),(0,0,0))
    display.blit(totalValueText, (mapWidth * tileSize + 50, (mapHeight * tileSize) / 2 - 50))
    display.blit(totalScoreText, (mapWidth * tileSize + 50, (mapHeight * tileSize) / 2))
    # update the display
    pygame.display.update()


def text_objects(msg,font):
    textSurface = font.render(msg, 1, (255,255,255))
    textRect = textSurface.get_rect()
    return textSurface, textRect


def button(msg,x,y,w,h,ic,ac,action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if x+w > mouse[0] > x and y+h > mouse[1] > y:
        pygame.draw.rect(display, ac,(x,y,w,h))
        if click[0] == 1 and action != None:
            action()
    else:
        pygame.draw.rect(display, ic,(x,y,w,h))

    smallText = pygame.font.Font("freesansbold.ttf",16)
    textSurf, textRect = text_objects(msg, smallText)
    textRect.center = ( (x+(w/2)), (y+(h/2)) )
    display.blit(textSurf, textRect)

show_margins = False
def toggle_margin_display():
    global show_margins
    show_margins = not show_margins
    global tilemap_required_margins
    global tileMap
    for row in range(mapHeight):
        for column in range(mapWidth):
            if show_margins is True and tilemap_required_margins[row][column] != None:
                tile = pygame.Surface((tileSize,tileSize))
                tile.fill((255,255,255, 100))
                pygame.draw.rect(tile, colors[tilemap_required_margins[row][column]], (0, 0, tileSize, tileSize))
                display.blit(tile,(column * tileSize, row * tileSize))
            elif tilemap_required_margins[row][column] != None:
                texture = pygame.transform.scale(textures[tileMap[row][column]],(tileSize,tileSize))
                display.blit(texture, (column * tileSize, row * tileSize))


show_extra_space = False
def toggle_extra_space_display():
    global show_extra_space
    show_extra_space = not show_extra_space
    global tilemap_extra_space
    global tileMap
    for row in range(mapHeight):
        for column in range(mapWidth):
            if show_extra_space is True and tilemap_extra_space[row][column] != None:
                texture = pygame.transform.scale(textures[tilemap_extra_space[row][column]],(tileSize,tileSize))
                display.blit(texture, (column * tileSize, row * tileSize))
            elif tilemap_extra_space[row][column] != None:
                if show_margins is True and tilemap_required_margins[row][column] != None:
                    tile = pygame.Surface((tileSize,tileSize))
                    tile.fill((255,255,255, 100))
                    pygame.draw.rect(tile, colors[tilemap_required_margins[row][column]], (0, 0, tileSize, tileSize))
                    display.blit(tile,(column * tileSize, row * tileSize))
                else:
                    texture = pygame.transform.scale(textures[tileMap[row][column]],(tileSize,tileSize))
                    display.blit(texture, (column * tileSize, row * tileSize))

placeRandomBuildings()


def stop_hillClimbing():
    global climbing
    climbing = False


climbing = False
def start_hillClimbing():
    global climbing
    global tileMap
    totalValue = getScore(tileMap, False)
    totalScore = 0
    iteration = 0
    climbing = True
    while climbing is True:
        pygame.event.get()


        iteration += 1
        # Display iteration
        font = pygame.font.Font("freesansbold.ttf",16)
        iteration_text = font.render("Iteration: " + str(iteration) + "               ", 1, (250,250,250), (0,0,0))
        display.blit(iteration_text, (mapWidth * tileSize + 50, (mapHeight * tileSize) / 2 - 100))
        print "ITERATION NUMBER: " , iteration

        # deep copy the tilemap as buffer
        new_tileMap = copy.deepcopy(tileMap)
        # Select a random building from the list..
        buildingType, score, position = scoreList[random.randint(0,len(scoreList) - 1)]
        # Clear it in the buffer so we can replace it and recalculate the score
        for row in range(position[1],position[1] + buildingSizes[buildingType][1]):
            for column in range(position[0],position[0] + buildingSizes[buildingType][0]):
                new_tileMap[row][column] = grass
        # try a random direction for now..
        move_direction = (random.randint(-2,2),random.randint(-2,2))
        # check if this is a valid position
        if check_valid_location(position[1] + move_direction[1], position[0] + move_direction[0],buildingType,new_tileMap) is True:
            # if it is, place the builing on our tilemap buffer
            place_building(position[1] + move_direction[1], position[0] + move_direction[0],buildingType,new_tileMap)
            new_value = getScore(new_tileMap, False)
            # if the new value is higher, update everything including the display
            if new_value >= totalValue:
                totalValue = new_value
                tileMap = new_tileMap
                getScore(tileMap)
                update_game_display()
        button("STOP",mapWidth * tileSize + 275, 25 ,100,100,(237,28,36),(191,15,23),stop_hillClimbing)
        pygame.display.flip()


running = True
switch_margin = True
while running:
    # get all the user events
    for event in pygame.event.get():
        # if the user wants to quit
        if event.type == QUIT:
            # and the game and close the window
            pygame.quit()
            sys.exit()
        # elif event.type == pygame.MOUSEBUTTONDOWN:
        #     # User clicks the mouse. Get the position
        #     pos = pygame.mouse.get_pos()
        #     # Change the x/y screen coordinates to grid coordinates
        #     column = pos[0] // (tileSize)
        #     row = pos[1] // (tileSize)
        #     print(row,column)
        #     # if the click was inside the displayed tilemap
        #     if column < mapWidth:
        #         if tileMap[row][column] > grass:
        #             clickedBuilding = tileMap[row][column]

    button("Reset",mapWidth * tileSize + 25, 25 ,100,25,(123,123,123),(50,50,50),placeRandomBuildings)
    button("Margins",mapWidth * tileSize + 150, 25 ,100,25,(123,123,123),(50,50,50),toggle_margin_display)
    button("Extra space",mapWidth * tileSize + 150, 75 ,100,25,(123,123,123),(50,50,50),toggle_extra_space_display)
    button("Hillclimbing",mapWidth * tileSize + 275, 25 ,100,25,(123,123,123),(50,50,50),start_hillClimbing)
    clock = pygame.time.Clock()
    # Limit to 60 fps
    clock.tick(60)
    pygame.display.update()