
import math
import sys
import random
from Constants import *
from pygame.locals import QUIT
import csv
import cProfile

# Buildings total, is not constant
houseAmount = 20

# keep track of positions of building
buildingList = [largeHouse] * int(houseAmount * 0.15) + [mediumHouse] * int(houseAmount * 0.25) + [smallHouse] * int(
    houseAmount * 0.6)


def place_water():
    # random water bodies..
    amount_of_bodies = random.randint(1,4)
    single_body_square = mapWidth * mapHeight * 0.2 / amount_of_bodies
    square_side = int(math.sqrt(single_body_square))

    water_bodies = []
    water_coords = []
    water_grid = [(x,y) for y in range(square_side,mapHeight - square_side,square_side) for x in range(square_side,mapWidth - square_side,square_side)]
    random.shuffle(water_grid)
    for i in range(1,amount_of_bodies + 1):
        width, height = square_side, square_side
        x, y = water_grid.pop()
        water_coords += [(x1,y1) for y1 in range(y,y + height) for x1 in range(x, x + width)]
        water_bodies.append([x,y,width,height])

    return water_bodies, water_coords

def place_close_together():
    building_locations = []
    id = 0
    tiles_apart = 5

    grid = [(x,y) for y in range(tiles_apart/2,mapHeight,tiles_apart) for x in range(tiles_apart/2,mapWidth,tiles_apart)]
    random.shuffle(grid)
    for house in buildingList:
        id += 1
        while len(grid) > 0:
            x,y = grid.pop(0)
            print x,y
            house_object = [id, house, x, y]
            temp_locations = building_locations + [house_object]
            valid = True
            for house_comparison in temp_locations:
                if get_shortest_distance(house_comparison, temp_locations) < 0:
                    valid = False
                    break
            if valid:
                building_locations.append([id, house, x, y])
                break
        else:
            print "ERROR PLACING BUILDING!!"

    return building_locations


# add all required buildings to the array at random valid locations
def place_random_buildings():
    # build up an array keeping track of positions
    building_locations = []

    # keep track of amount of houses placed, give each a unique id
    id = 0
    for chosen_building in reversed(buildingList):
        attempt = 0
        id += 1
        while True:  # selects a random position and check if it's empty.. loops until found empty spot, might be infinite if there's no valid location left
            randomRow = random.randint(buildingSizes[chosen_building][2],
                                       mapHeight - 1 - int(math.ceil(buildingSizes[chosen_building][1])) -
                                       buildingSizes[chosen_building][2])
            randomColumn = random.randint(buildingSizes[chosen_building][2],
                                          mapWidth - 1 - int(math.ceil(buildingSizes[chosen_building][0])) -
                                          buildingSizes[chosen_building][2])

            house_object = [id, chosen_building, randomColumn, randomRow]
            temp_locations = building_locations + [house_object]
            valid = True
            for house in temp_locations:
                if get_shortest_distance(house, temp_locations) < 0:
                    valid = False
                    break
            if valid:
                building_locations.append([id, chosen_building, randomColumn, randomRow])
                break
            else:
                attempt += 1
                print attempt
                # to avoid an infinite loop, reset this function and start over at attempt 50000..
                if attempt > 50000:
                    return place_random_buildings()


    return building_locations


# this function calculates the score by using house coordinates
def calculate_score(house_array):
    id = 0
    type = 1
    x = 2
    y = 3
    house_score_list = []
    for house_object in house_array:

        # calculate the shortest distance ( and subtract the required margin and floor to metric meters)
        house_score = get_shortest_distance(house_object, house_array)

        # hard constrain so the required margin of any house can never be overwritten
        if house_score < 0:
            return False, False, False
        house_score_list.append(house_object[0:4] + [house_score])

    total_extra_free_space = sum([o[4] for o in house_score_list])
    total_value = int(sum([(1 + o[4] * houseValues[o[type]][1]) * houseValues[o[type]][0] for o in house_score_list]))
    return house_score_list, total_extra_free_space, total_value


def get_shortest_distance(house_object, house_positions):
    id = 0
    type = 1
    x = 2
    y = 3
    shortest_distance = None
    house_corners = [(house_object[x],house_object[y]),(house_object[x] + buildingSizes[house_object[type]][0],house_object[y]),
                     (house_object[x],house_object[y] + buildingSizes[house_object[type]][1]), (house_object[x] + buildingSizes[house_object[type]][0], house_object[y] + buildingSizes[house_object[type]][1]) ]

    # check if house does not stand in any water!
    S1,S2 = set(house_corners), set(water_coords)
    if len(S2.intersection(S1)) > 0:
        return -99


    for house_comparison in [o for o in house_positions if o[id] != house_object[id]]:
        # Basically we determine in which of the 8 possible directions the comparison house lies.
        # Directions are: up, left, right, down, up-left, up-right, down-left, down-right
        # This is important because we need to determine from which corner of the houses we measure the distance
        # Keep in mind that the UPPER LEFT corner of the map is position (0,0)

        # comparison house is above house_object if house_object's highest Y is beneath house_comparison's lowest Y
        if house_object[y] > house_comparison[y] + buildingSizes[house_comparison[type]][1]:
            y_distance = house_object[y] - (house_comparison[y] + buildingSizes[house_comparison[type]][1])

        # comparison house is below house_object if..
        elif house_object[y] + buildingSizes[house_object[type]][1] < house_comparison[y]:
            y_distance = house_comparison[y] - (house_object[y] + buildingSizes[house_object[type]][1])

        # otherwise it is horizontally next to house_object, so y = 0 because we only need horizontal distance
        else:
            y_distance = 0

        # do the same for the x axis
        if house_object[x] > house_comparison[x] + buildingSizes[house_comparison[type]][0]:
            x_distance = house_object[x] - (house_comparison[x] + buildingSizes[house_comparison[type]][0])

        # comparison house is right of house_object if..
        elif house_object[x] + buildingSizes[house_object[type]][0] < house_comparison[x]:
            x_distance = house_comparison[x] - (house_object[x] + buildingSizes[house_object[type]][0])

        # otherwise it is vertically next to house_object, measure only the Y distance
        else:
            x_distance = 0

        total_distance = math.sqrt(x_distance ** 2 + y_distance ** 2)
        if total_distance == 0:  # intersection!
            return -99
        if shortest_distance is None or total_distance < shortest_distance:
            shortest_distance = total_distance

    # if the smallest distance to the end of the map is smaller than the smallest distance between any other house..
    map_distance = min([house_object[y], mapHeight - house_object[y] - buildingSizes[house_object[type]][1],
                        house_object[x], mapWidth - house_object[x] - buildingSizes[house_object[type]][0]])
    if not shortest_distance or shortest_distance > map_distance:
        shortest_distance = map_distance
    # calculate the score (subtract the required margin and floor to metric meters)
    house_score = int(math.floor((shortest_distance - buildingSizes[house_object[type]][2]) / tilesPerMetre))
    return house_score


# this function updates the display given a list of house positions and scores
def update_game_display(house_scores):
    if not house_scores:
        house_scores = []

    # display the gridlike background
    texture = pygame.transform.scale(textures[grass2], (mapWidth * tileSize,mapHeight * tileSize))
    display.blit(texture, (0,0))

    # draw water if any
    for x, y,width,height in water_bodies_list:
        print x,y, width,height
        water_texture = pygame.transform.scale(textures[water], (tileSize * width, tileSize * height))
        display.blit(water_texture, (tileSize * x, tileSize * y))

    # set up font displaying score and value
    font = pygame.font.Font("freesansbold.ttf", 20)
    totalValue = 0
    totalScore = 0
    # draw a score on the center of each house and add it's value to total value
    for id, buildingType, x, y, score in house_scores:
        # draw required margin per house
        margin_texture = pygame.transform.scale(margin_textures[buildingType], (
        tileSize * (buildingSizes[buildingType][0] + buildingSizes[buildingType][2] * 2),
        tileSize * (buildingSizes[buildingType][1] + buildingSizes[buildingType][2] * 2)))
        display.blit(margin_texture, (
        (x - buildingSizes[buildingType][2]) * tileSize, (y - buildingSizes[buildingType][2]) * tileSize))

        # draw building
        texture = pygame.transform.scale(textures[buildingType], (
        tileSize * buildingSizes[buildingType][0], tileSize * buildingSizes[buildingType][1]))
        display.blit(texture, (x * tileSize, y * tileSize))

        # draw score and add to total
        scoreText = font.render(str(score), 1, (10, 10, 10))
        totalScore += score
        textpos = scoreText.get_rect()
        centerX = buildingSizes[buildingType][0] / 2 * tileSize - textpos.width / 2
        centerY = buildingSizes[buildingType][1] / 2 * tileSize - textpos.height / 2
        buildingValue = houseValues[buildingType][0] * (
        1 + (houseValues[buildingType][1] * score))  # formula to calculate building value here
        display.blit(scoreText, ((x * tileSize + centerX), (y * tileSize + centerY)))
        totalValue += buildingValue

    # Display the total calculated value and the total score (extra free space)
    totalValueText = font.render("Total value: " + str(totalValue) + "    ", 1, (250, 250, 250), (0, 0, 0))
    totalScoreText = font.render("Total (extra) free space: " + str(totalScore) + "    ", 1, (250, 250, 250), (0, 0, 0))
    display.blit(totalValueText, (mapWidth * tileSize + 50, (mapHeight * tileSize) / 2 - 50))
    display.blit(totalScoreText, (mapWidth * tileSize + 50, (mapHeight * tileSize) / 2))
    # update the display
    pygame.display.update()


def text_objects(msg, font):
    textSurface = font.render(msg, 1, (255, 255, 255))
    textRect = textSurface.get_rect()
    return textSurface, textRect


def button(msg, x, y, w, h, ic, ac, action=None, params=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        pygame.draw.rect(display, ac, (x, y, w, h))
        if click[0] == 1 and action != None:
            if params == None:
                action()
            else:
                action(params)
    else:
        pygame.draw.rect(display, ic, (x, y, w, h))

    smallText = pygame.font.Font("freesansbold.ttf", 16)
    textSurf, textRect = text_objects(msg, smallText)
    textRect.center = ((x + (w / 2)), (y + (h / 2)))
    display.blit(textSurf, textRect)


house_positions = []
def place_random_and_update():
    pr = cProfile.Profile()
    pr.enable()
    global house_positions
    house_positions = place_random_buildings()
    house_positions, total_score, total_value = calculate_score(house_positions)
    update_game_display(house_positions)
    pr.disable()
    # after your program ends
    pr.print_stats(sort="calls")

def place_setting1_and_update():
    pr = cProfile.Profile()
    pr.enable()
    global house_positions
    house_positions = place_close_together()
    house_positions, total_score, total_value = calculate_score(house_positions)
    update_game_display(house_positions)
    pr.disable()
    # after your program ends
    pr.print_stats(sort="calls")



def random_sample():
    global house_positions
    with open('randomsample.csv', "wb") as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow(["total_value","total_score", "score_list"])
        highest_value = 0
        font = pygame.font.Font("freesansbold.ttf", 16)
        for i in range(1000):
            # Display iteration
            iteration_text = font.render("Writing row: " + str(i) + "               ", 1, (250, 250, 250), (0, 0, 0))
            display.blit(iteration_text, (mapWidth * tileSize + 50, (mapHeight * tileSize) / 2 - 100))
            pygame.display.flip()

            scoreList, totalScore, totalValue = calculate_score(place_random_buildings())
            writer.writerow([totalValue,totalScore,scoreList])
            if highest_value < totalValue:
                highest_value = totalValue
                highest_scoreList = scoreList

    house_positions = highest_scoreList
    update_game_display(highest_scoreList)

def stop_hillClimbing():
    global climbing
    climbing = False
climbing = False


# (non-stochastic) hillclimbing calculates every possible step, this value affects performance a lot! (smaller steps is faster, but less result)
hillClimbing_max_steps = 2

# this function tries to move a house in every possible direction (between 1 and the max_steps), and accepts the highest VALUE
def start_hillClimbing():
    global climbing
    global house_positions

    start_position, total_extra_free_space, total_value = calculate_score(house_positions)
    iteration = 0
    climbing = True
    while climbing is True:
        pygame.event.get()
        iteration += 1

        # Display iteration
        font = pygame.font.Font("freesansbold.ttf", 16)
        iteration_text = font.render("Iteration: " + str(iteration) + "               ", 1, (250, 250, 250), (0, 0, 0))
        display.blit(iteration_text, (mapWidth * tileSize + 50, (mapHeight * tileSize) / 2 - 100))
        print "ITERATION NUMBER: ", iteration

        # Select a random building from the list..
        id, buildingType, x, y, score = house_positions[random.randint(0, len(house_positions) - 1)]

        # implement a chance to swap two houses
        swap_chance = random.randint(0, 10)
        if swap_chance > 8:
            # to make sure we're not swapping the same house (type) which would obviously be inefficient
            efficient_swaps = [o for o in house_positions if o[1] != buildingType]
            print "Trying to swap.."
            new_value = False
            for swap_id, swap_buildingType, swap_x, swap_y, swap_score in efficient_swaps:

                # temporary list to re-calculate scores (storing all the positions that will not change)
                temp_pos_list = [house for house in house_positions if house[0] not in (id, swap_id)]

                # anchor point (position) is the upper left corner of a house, convert it to center both houses on their new spots
                center_correction_x = int(buildingSizes[buildingType][0] - buildingSizes[swap_buildingType][0]) / 2
                center_correction_y = int(buildingSizes[buildingType][1] - buildingSizes[swap_buildingType][1]) / 2
                new_house = [id, buildingType, swap_x + (center_correction_x * -1), swap_y + (center_correction_y * -1)]
                new_house_comparison = [swap_id, swap_buildingType, x + center_correction_x, y + center_correction_y]

                temp_score_list, temp_score, temp_value = calculate_score(
                    temp_pos_list + [new_house] + [new_house_comparison])
                if not new_value or temp_value > new_value:
                    new_score_list, new_score, new_value = temp_score_list, temp_score, temp_value
            print "Highest possible swap value: " + str(new_value)
        # otherwise move in a random direction
        else:
            move_range = []  # put every direction in a range (including diagonally)
            for i in xrange(1, hillClimbing_max_steps + 1):
                strength_range = [(-i, -i), (+i, -i), (-i, +i), (+i, +i), (0, -i), (-i, 0), (0, +i), (+i, 0)]
                random.shuffle(strength_range)
                move_range.append(strength_range)

            possible_values = []
            for strength in reversed(move_range):
                for move_direction in strength:
                    if get_shortest_distance([id, buildingType, x + move_direction[0], y + move_direction[1]],
                                             house_positions) >= 0:
                        temp_score_list = [house if house[0] != id else [id, buildingType, x + move_direction[0],
                                                                         y + move_direction[1]] for house in
                                           house_positions]
                        temp_score_list, temp_score, temp_value = calculate_score(temp_score_list)
                        if temp_score_list:
                            possible_values.append([temp_score_list, temp_score, temp_value])

            # check if we need to update the highest (or equal) value, based on total price (x[1] = highest free space)
            if len(possible_values) != 0:
                new_score_list, new_score, new_value = max(possible_values, key=lambda x: x[2])
            else:
                new_score_list = False

        # check if we need to update the highest (or equal) value
        if new_score_list and new_value >= total_value and new_score_list:  # not in saved_score_lists:
            house_positions = new_score_list
            # saved_score_lists.append(new_score_list)
            total_value = new_value
            print "Higher or equal value found: " + str(new_value)
            update_game_display(new_score_list)

        button("STOP", mapWidth * tileSize + 275, 125, 100, 25, (237, 28, 36), (191, 15, 23), stop_hillClimbing)
        pygame.display.flip()


# stochastic hillclimber just generates a random movement and accepts if this improves or equals the original value
def start_stochastic_hillClimbing():
    global climbing
    global house_positions

    start_position, total_extra_free_space, total_value = calculate_score(house_positions)

    iteration = 0
    climbing = True
    while climbing is True:

        iteration += 1
        # Display iteration
        font = pygame.font.Font("freesansbold.ttf", 16)
        iteration_text = font.render("Iteration: " + str(iteration) + "               ", 1, (250, 250, 250), (0, 0, 0))
        display.blit(iteration_text, (mapWidth * tileSize + 50, (mapHeight * tileSize) / 2 - 100))
        print "ITERATION NUMBER: ", iteration

        # Select a random building from the list..
        id, buildingType, x, y, score = house_positions[random.randint(0, len(house_positions) - 1)]

        # implement a chance to swap two houses
        swap_chance = random.randint(0, 10)
        new_value = False
        if swap_chance > 8:
            # to make sure we're not swapping the same house (type) which would obviously be inefficient
            efficient_swaps = [o for o in house_positions if o[1] != buildingType]
            print "Trying to swap.."
            swap_id, swap_buildingType, swap_x, swap_y, swap_score = efficient_swaps[
                random.randint(0, len(efficient_swaps) - 1)]

            # temporary list to re-calculate scores (storing all the positions that will not change)
            temp_score_list = [house for house in house_positions if house[0] not in (id, swap_id)]

            # anchor point (position) is the upper left corner of a house, convert it to center both houses on their new spots
            center_correction_x = int(buildingSizes[buildingType][0] - buildingSizes[swap_buildingType][0]) / 2
            center_correction_y = int(buildingSizes[buildingType][1] - buildingSizes[swap_buildingType][1]) / 2
            new_house = [id, buildingType, swap_x + (center_correction_x * -1), swap_y + (center_correction_y * -1)]
            new_house_comparison = [swap_id, swap_buildingType, x + center_correction_x, y + center_correction_y]


            temp_score_list, temp_score, temp_value = calculate_score(
                temp_score_list + [new_house] + [new_house_comparison])
            if not new_value or temp_value > new_value:
                new_score_list, new_score, new_value = temp_score_list, temp_score, temp_value

        # otherwise move in a random direction
        else:
            # generate a random direction
            move_direction = (random.randint(-hillClimbing_max_steps, hillClimbing_max_steps),
                              random.randint(-hillClimbing_max_steps, hillClimbing_max_steps))
            while move_direction == (0, 0):
                move_direction = (random.randint(-hillClimbing_max_steps, hillClimbing_max_steps),
                                  random.randint(-hillClimbing_max_steps, hillClimbing_max_steps))

            temp_score_list = [
                house if house[0] != id else [id, buildingType, x + move_direction[0], y + move_direction[1]] for house
                in house_positions]
            new_score_list, new_score, new_value = calculate_score(temp_score_list)

        # check if we need to update the highest (or equal) value
        if new_score_list and new_value >= total_value:
            house_positions = new_score_list
            total_value = new_value
            print "Higher or equal value found: " + str(new_value)
            update_game_display(new_score_list)

        button("STOP", mapWidth * tileSize + 275, 125, 100, 25, (237, 28, 36), (191, 15, 23), stop_hillClimbing)
        pygame.event.get()

# Simulated Annealing, pretty much a copy of hillclimbing apart from a chance to accept lower values.. (write as one function?)
def start_simulated_annealing():
    global climbing
    global house_positions

    start_position, total_extra_free_space, total_value = calculate_score(house_positions)
    highest_position,highest_extra_free_space, highest_value = start_position, total_extra_free_space, total_value
    iteration = 0
    # initial temperature for Boltzman distribution
    temp = total_value / 10 / houseAmount
    climbing = True
    while climbing is True:
        pygame.event.get()
        iteration += 1


        # Select a random building from the list..
        id, buildingType, x, y, score = house_positions[random.randint(0, len(house_positions) - 1)]

        # implement a chance to swap two houses
        swap_chance = random.randint(0, 10)
        if swap_chance > 8:
            # to make sure we're not swapping the same house (type) which would obviously be inefficient
            efficient_swaps = [o for o in house_positions if o[1] != buildingType]
            print "Trying to swap.."
            swap_id, swap_buildingType, swap_x, swap_y, swap_score = efficient_swaps[
                random.randint(0, len(efficient_swaps) - 1)]

            # temporary list to re-calculate scores (storing all the positions that will not change)
            temp_score_list = [house for house in house_positions if house[0] not in (id, swap_id)]

            # anchor point (position) is the upper left corner of a house, convert it to center both houses on their new spots
            center_correction_x = int(buildingSizes[buildingType][0] - buildingSizes[swap_buildingType][0]) / 2
            center_correction_y = int(buildingSizes[buildingType][1] - buildingSizes[swap_buildingType][1]) / 2
            new_house = [id, buildingType, swap_x + (center_correction_x * -1), swap_y + (center_correction_y * -1)]
            new_house_comparison = [swap_id, swap_buildingType, x + center_correction_x, y + center_correction_y]

            new_score_list, new_score, new_value = calculate_score(
                temp_score_list + [new_house] + [new_house_comparison])

        # otherwise move in a random direction
        else:
            # generate a random direction
            move_direction = (random.randint(-hillClimbing_max_steps, hillClimbing_max_steps),
                              random.randint(-hillClimbing_max_steps, hillClimbing_max_steps))
            while move_direction == (0, 0):
                move_direction = (random.randint(-hillClimbing_max_steps, hillClimbing_max_steps),
                                  random.randint(-hillClimbing_max_steps, hillClimbing_max_steps))

            temp_score_list = [house if house[0] != id else [id, buildingType, x + move_direction[0], y + move_direction[1]] for house in house_positions]
            new_score_list, new_score, new_value = calculate_score(temp_score_list)

        # check if we need to update the highest (or equal) value
        if new_score_list and new_value >= total_value:
            house_positions = new_score_list
            total_value = new_value
            print "Higher or equal value found: " + str(new_value)
            highest_position, highest_extra_free_space, highest_value = new_score_list, new_score, new_value
            update_game_display(new_score_list)

        # also a chance to accept lower values..
        elif new_score_list:
            temp *= 0.9999
            # TODO Create a good acceptance chance formula based on difference between scores and iteration number
            acceptance_chance = math.exp(-(total_value - new_value) / temp) / 2
            probability = random.random()
            print probability, acceptance_chance, total_value - new_value
            if probability < acceptance_chance:
                house_positions = new_score_list
                total_value = new_value
                print "Accepting lower value..: " + str(new_value)
                update_game_display(new_score_list)
        # Display iteration
        font = pygame.font.Font("freesansbold.ttf", 16)
        iteration_text = font.render("Iteration: " + str(iteration) + "  Temp:" + str(temp) + "              ", 1, (250, 250, 250), (0, 0, 0))
        display.blit(iteration_text, (mapWidth * tileSize + 50, (mapHeight * tileSize) / 2 - 100))
        print "ITERATION NUMBER: ", iteration
        button("STOP", mapWidth * tileSize + 275, 125, 100, 25, (237, 28, 36), (191, 15, 23), stop_hillClimbing)
        pygame.display.flip()

def setHouseAmount(amount):
    global houseAmount
    houseAmount = amount
    global buildingList
    # keep track of positions of building
    buildingList = [largeHouse] * int(houseAmount * 0.15) + [mediumHouse] * int(houseAmount * 0.25) + [smallHouse] * int(
    houseAmount * 0.6)

    place_setting1_and_update()


water_bodies_list, water_coords = place_water()
print water_coords
# draws the map without houses
update_game_display(False)

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

    button("Random", mapWidth * tileSize + 25, 25, 100, 25, colors["lightgrey"], colors["darkgrey"], place_random_and_update)
    button("R. Sample", mapWidth * tileSize + 25, 75, 100, 25, colors["lightgrey"], colors["darkgrey"], random_sample)
    button("Setting 1", mapWidth * tileSize + 25, 125, 100, 25, colors["lightgrey"], colors["darkgrey"], place_setting1_and_update)
    # button("Margins", mapWidth * tileSize + 150, 25, 100, 25, colors["lightgrey"], colors["darkgrey"], toggle_margin_display)

    # hide these buttons if map is empty
    if len(house_positions) > 0:
        button("Sim Anneal", mapWidth * tileSize + 150, 25, 100, 25, colors["lightgrey"], colors["darkgrey"], start_simulated_annealing)
        button("Hillclimbing", mapWidth * tileSize + 275, 25, 100, 25, colors["lightgrey"], colors["darkgrey"], start_hillClimbing)
        button("Stoch. Hill", mapWidth * tileSize + 275, 75, 100, 25, colors["lightgrey"], colors["darkgrey"], start_stochastic_hillClimbing)

    # Buttons to adjust amount of houses
    if houseAmount == 20:
        button("20", mapWidth * tileSize + 25, mapHeight * tileSize - 25, 100, 25, colors["green"], colors["green"])
        button("40", mapWidth * tileSize + 150, mapHeight * tileSize - 25, 100, 25, colors["lightgrey"], colors["darkgrey"],setHouseAmount,40)
        button("60", mapWidth * tileSize + 275, mapHeight * tileSize - 25, 100, 25, colors["lightgrey"], colors["darkgrey"],setHouseAmount,60)
    elif houseAmount == 40:
        button("20", mapWidth * tileSize + 25, mapHeight * tileSize - 25, 100, 25, colors["lightgrey"], colors["darkgrey"],setHouseAmount,20)
        button("40", mapWidth * tileSize + 150, mapHeight * tileSize - 25, 100, 25, colors["green"], colors["green"])
        button("60", mapWidth * tileSize + 275, mapHeight * tileSize - 25, 100, 25, colors["lightgrey"], colors["darkgrey"],setHouseAmount,60)
    elif houseAmount == 60:
        button("20", mapWidth * tileSize + 25, mapHeight * tileSize - 25, 100, 25, colors["lightgrey"], colors["darkgrey"],setHouseAmount,20)
        button("40", mapWidth * tileSize + 150, mapHeight * tileSize - 25, 100, 25, colors["lightgrey"], colors["darkgrey"],setHouseAmount,40)
        button("60", mapWidth * tileSize + 275, mapHeight * tileSize - 25, 100, 25, colors["green"], colors["green"])
    pygame.display.update()

