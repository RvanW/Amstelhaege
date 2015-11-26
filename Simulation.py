import copy
import math
import pygame, sys
import random
from pygame.locals import *
from Constants import *

# Buildings total, is not constant
houseAmount = 20

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

def clear_building(clear_row,clear_column,buildingType,map,replace_with):
    for row in range(clear_row, int(math.ceil(clear_row + buildingSizes[buildingType][1])), 1):
        for column in range(clear_column, int(clear_column + math.ceil(buildingSizes[buildingType][0])), 1):
            map[row][column] = replace_with

def pickup_building(buildingType,x,y):
    global tileMap
    # find the upper left corner
    while tileMap[y][x - 1] == buildingType:
        x -= 1
    while tileMap[y - 1][x] == buildingType:
        y -= 1

    # loop over the area and replace the tiles with grass
    for row in range(y, int(math.ceil(y + buildingSizes[buildingType][1])), 1):
        for column in range(x, int(x + math.ceil(buildingSizes[buildingType][0])), 1):
            tileMap[row][column] = grass

    # start
# add all required buildings to the tileMap at random positions for now
def place_random_buildings():
    global tileMap
    global tilemap_required_margins
    # build up an array with all the required buildings
    buildingList = [largeHouse] * int(houseAmount * 0.15) + [mediumHouse] * int(houseAmount * 0.25) + [smallHouse] * int(houseAmount * 0.6)
    # reset tilemaps
    initialize_tilemaps()
    # i = amount of houses found
    houses_found = 0
    error = False
    while houses_found != houseAmount and not error:
        randomBuilding = buildingList.pop()
        attempt = 0
        while True:  # selects a random position and check if it's empty (grass).. loops until found empty spot, might be infinite if there's no valid location left
            randomRow = random.randint(buildingSizes[randomBuilding][2], mapHeight - 1 - int(math.ceil(buildingSizes[randomBuilding][1])) - buildingSizes[randomBuilding][2])
            randomColumn = random.randint(buildingSizes[randomBuilding][2], mapWidth - 1 - int(math.ceil(buildingSizes[randomBuilding][0])) - buildingSizes[randomBuilding][2])

            if check_valid_location(randomRow,randomColumn,randomBuilding, tileMap) is True:
                print("Empty plot found! placing building")
                place_building(randomRow,randomColumn,randomBuilding,tileMap)
                houses_found += 1
                break
            else:
                attempt += 1
                print("Not empty! Attempt: ", attempt)
                # to avoid an infinite loop, reset the tileMap and start over at attempt 50000..
                if attempt > 50000:
                    initialize_tilemaps()
                    error = True
                    place_random_buildings()
                    break
    get_tilemap_score(tileMap)
    update_game_display()



# This function calculates the score based on the margin around and updates the score list

# deep copy the given tileMap and calculate the score
def get_tilemap_score(map):
    totalValue, totalScore = 0,0

    global tilemap_required_margins
    global tilemap_extra_space
    # reset our global margin tilemaps if we want to update it
    global scoreList
    scoreList = []
    tilemap_required_margins = [[None for w in range(mapWidth)] for h in range(mapHeight)]
    tilemap_extra_space = [[None for w in range(mapWidth)] for h in range(mapHeight)]

    # This is much faster than copy.deepcopy
    mapBuffer = [row[:] for row in map]

    while len(scoreList) < houseAmount:
        for row in range(mapHeight):
            # loop through each tile in the map
            for column in range(mapWidth):
                # skip tiles with the value None
                if mapBuffer[row][column] is None:
                    continue

                # otherwise we've found a new building
                elif mapBuffer[row][column] > water:
                    foundBuilding = mapBuffer[row][column]
                    current_margin = 0 # this is used to keep track of the margin that is build up around the house
                    found = False
                    # calculate increasingly margin around building in this while loop until hitting another building or end of map
                    while not found:
                        current_margin += 1
                        # For each row in range of the size + x and - x
                        for marginRow in range(row - current_margin, int(row + current_margin + buildingSizes[foundBuilding][1])):
                            # End of map was found was found vertically
                            if marginRow < 0 or marginRow > (mapHeight - 1):
                                # print("MARGINROW end of map vertical at x=", x)
                                found = True
                                break
                            # end of map was found horizontally
                            elif column - current_margin < 0 or column + current_margin + buildingSizes[foundBuilding][0] > mapWidth:
                                # print("MARGINROW end of map horizontal at x=", x)
                                found = True
                                break
                            # Collision with a house found on the left side
                            elif mapBuffer[marginRow][column - current_margin] not in (grass, grass2):
                                # print("MARGINROW object found left with x of ", x)
                                # tileMap[marginRow][column - x] = blue
                                found = True
                                break
                            # Collision with a house found on the right side (could be joined into 1 statement with left)
                            elif mapBuffer[marginRow][column + current_margin - 1 + buildingSizes[foundBuilding][0]] not in (grass, grass2):
                                # print("MARGINROW object found right with x of ", x)
                                # tileMap[marginRow][column + x - 1 + buildingSizes[foundBuilding][0]] = blue
                                found = True
                                break
                            # If the surrounding tiles pass these tests, they are empty..
                            # Do we want to update the arrays storing margins?
                            else:
                                # if the margin is within the required space..
                                if current_margin <= buildingSizes[foundBuilding][2]:
                                    tilemap_required_margins[marginRow][column - current_margin] = buildingColors[foundBuilding]
                                    tilemap_required_margins[marginRow][column + current_margin - 1 + buildingSizes[foundBuilding][0]] = buildingColors[foundBuilding]
                                else:
                                    tilemap_extra_space[marginRow][column - current_margin] = grass2
                                    tilemap_extra_space[marginRow][column + current_margin - 1 + buildingSizes[foundBuilding][0]] = grass2
                                continue

                        if not found:
                            # column + 1 and - 1 because this tile was already checked in marginRows
                            for marginColumn in range(column - current_margin + 1, int(column + current_margin - 1 + buildingSizes[foundBuilding][0])):
                                if mapBuffer[row - current_margin][marginColumn] not in (grass, grass2):
                                    # print("MARGINCOLUMN object collision found downwards at (",row - x, marginColumn)
                                    # tileMap[row - x][marginColumn] = blue
                                    found = True
                                    break
                                elif mapBuffer[row + current_margin - 1 + int(buildingSizes[foundBuilding][1])][marginColumn] not in (grass, grass2):
                                    # tileMap[row + x - 1 + int(buildingSizes[foundBuilding][1])][marginColumn] = blue
                                    # print("MARGINCOLUMN object found upwards with x of ", x)
                                    found = True
                                    break
                                else:
                                    if current_margin <= buildingSizes[foundBuilding][2]:
                                        tilemap_required_margins[row + current_margin - 1 + int(buildingSizes[foundBuilding][1])][marginColumn] = buildingColors[foundBuilding]
                                        tilemap_required_margins[row - current_margin][marginColumn] = buildingColors[foundBuilding]
                                    else:
                                        tilemap_extra_space[row + current_margin - 1 + int(buildingSizes[foundBuilding][1])][marginColumn] = grass2
                                        tilemap_extra_space[row - current_margin][marginColumn] = grass2
                                    continue

                    # (found margin - required margin) / 2 = extra free space in metres
                    buildingScore = int(math.floor((current_margin - buildingSizes[foundBuilding][2]) / tilesPerMetre))
                    # If the buildingscore is lower than 0, it means the required space has been violated, return false
                    if buildingScore < 0:
                        print "Required margin was overwritten at (" + str(column) + ", " + str(row) + ")"
                        return False

                    # formula to calculate building value here
                    totalValue += houseValues[foundBuilding][0] * (1 + (houseValues[foundBuilding][1] * buildingScore))

                    # replace all tiles of the building with none so these will be skipped in the rest of our loop
                    clear_building(row,column,foundBuilding,mapBuffer,None)

                    textpos = ( column, row )
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

place_random_buildings()


def stop_hillClimbing():
    global climbing
    climbing = False


climbing = False
def start_hillClimbing():
    global climbing
    global tileMap
    totalValue = get_tilemap_score(tileMap)
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
        new_tileMap = [row[:] for row in tileMap]

        # Select a random building from the list..
        buildingType, score, position = scoreList[random.randint(0,len(scoreList) - 1)]
        # Clear it in the buffer so we can replace it and recalculate the score
        for row in range(position[1],position[1] + buildingSizes[buildingType][1]):
            for column in range(position[0],position[0] + buildingSizes[buildingType][0]):
                new_tileMap[row][column] = grass

        # implement a chance to swap two houses
        swap_chance = random.randint(0,10)
        if swap_chance > 8:
            print "Trying to swap.."
            swap_buildingType, swap_score, swap_position = scoreList[random.randint(0,len(scoreList) - 1)]
            # to make sure we're not swapping the same house (type) which would obviously be inefficient
            while swap_position == position or swap_buildingType == buildingType:
                swap_buildingType, swap_score, swap_position = scoreList[random.randint(0,len(scoreList) - 1)]
            clear_building(swap_position[1],swap_position[0],swap_buildingType,new_tileMap,grass)
            # anchor point (position) is the upper left corner, convert it to center both buildings
            center_correction_x = int(buildingSizes[buildingType][0] - buildingSizes[swap_buildingType][0]) / 2
            center_correction_y = int(buildingSizes[buildingType][1] - buildingSizes[swap_buildingType][1]) / 2
            place_building(swap_position[1] + (center_correction_x * -1), swap_position[0] + (center_correction_y * -1), buildingType, new_tileMap)
            place_building(position[1] + center_correction_x, position[0] + center_correction_y, swap_buildingType, new_tileMap)

        # otherwise move in a random direction
        else:
            # try a random direction for, either vertical or horizontal (not diagonal, would be inefficient)
            if random.randint(0,1) == 0:
                move_direction = (0,random.randint(-2,2))
            else:
                move_direction = (random.randint(-2,2),0)
            # to avoid list out of range check the position first
            if position[1] + buildingSizes[buildingType][0] + move_direction[1] < mapWidth and position[0] + buildingSizes[buildingType][1] + move_direction[0] < mapHeight:
                place_building(position[1] + move_direction[1], position[0] + move_direction[0],buildingType,new_tileMap)
            else:
                print "Went out of map at", position
                place_building(position[1], position[0], buildingType, new_tileMap)

        new_value = get_tilemap_score(new_tileMap)
        # check if this is a valid position and it is higher or equal to current value
        if new_value and new_value >= totalValue:
                totalValue = new_value
                print "Higher value found: " + str(new_value)
                tileMap = new_tileMap
                update_game_display()

        else:
            get_tilemap_score(tileMap)
        button("STOP",mapWidth * tileSize + 275, 25 ,100,100,(237,28,36),(191,15,23),stop_hillClimbing)



running = True
clock = pygame.time.Clock()
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
        #             pickup_building(clickedBuilding,column,row)
        #             update_game_display()
    button("Reset",mapWidth * tileSize + 25, 25 ,100,25,(123,123,123),(50,50,50),place_random_buildings)
    button("Margins",mapWidth * tileSize + 150, 25 ,100,25,(123,123,123),(50,50,50),toggle_margin_display)
    button("Extra space",mapWidth * tileSize + 150, 75 ,100,25,(123,123,123),(50,50,50),toggle_extra_space_display)
    button("Hillclimbing",mapWidth * tileSize + 275, 25 ,100,25,(123,123,123),(50,50,50),start_hillClimbing)

    # Limit to 60 fps
    clock.tick(60)
    pygame.display.update()