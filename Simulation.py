import math
import sys
import random
import datetime
from Constants import *
from pygame.locals import QUIT
import csv

# The amount of houses can be adjusted in the simulation, so should not be constant, but default 20
houseAmount = 20

# build up array according to ratio's and house amount (20,40,60)
buildingList = [largeHouse] * int(houseAmount * 0.15) + [mediumHouse] * int(houseAmount * 0.25) + [smallHouse] * int(
    houseAmount * 0.6)

### SIMULATION MECHANICS ###

# Places the required water randomly in strokes of 1/4 width-height ratio
def place_water_random():
    # We need at least 1 body, and tops 4
    amount_of_bodies = random.randint(1,4)

    # So one body should compose these square metres
    single_body_square = mapWidth * mapHeight * 0.2 / amount_of_bodies

    # We take the square root, we can make a square with this value
    # if we divide the width/height by 2, we have 4 square building blocks..
    # putting these horizontally/vertically next to each other should compose our body of water with 1/4 ratio!
    smallest_square_side = int(math.sqrt(single_body_square)) / 2

    water_bodies = []

    # build up an efficient grid so water bodies won't block each other
    water_grid = [(x,y) for y in range(0,mapHeight - smallest_square_side, smallest_square_side) for x in range(0,mapWidth - smallest_square_side,smallest_square_side)]

    id = 60 # id is at least 61 to separate houses from water
    for i in range(1,amount_of_bodies + 1):
        id += 1
        # make strokes of atleast 1*4 ratio, either horizontal or vertical
        if random.random() < 0.5:
            width, height = smallest_square_side * 4, smallest_square_side
        else:
            width, height = smallest_square_side, smallest_square_side * 4

        x, y = water_grid[random.randint(0,len(water_grid) - 1)]
        # While this water body blocks another, try another location and orientation
        while check_if_in_water([id, x, y, width, height], water_bodies):
            x, y = water_grid[random.randint(0,len(water_grid) - 1)]
            # 50/50 chance for horizontal / vertical placement
            if random.random() < 0.5:
                width, height = smallest_square_side * 4, smallest_square_side
            else:
                width, height = smallest_square_side, smallest_square_side * 4
        water_bodies.append([id,x,y,width,height])

    return water_bodies


# returns True if target (house or water) intersects with any water
def check_if_in_water(target,water_list):
    # list indexes for water bodies
    id = 0
    x = 1
    y = 2
    width = 3
    height = 4

    # if id is bigger than house amount, target must be water
    if target[id] > houseAmount:
        target_x, target_y, target_width, target_height = target[x], target[y], target[width], target[height]
    # otherwise it is a house (which has different indexes and constant width/height)
    else:
        target_x, target_y, target_width, target_height = target[2], target[3], buildingSizes[target[1]][0], buildingSizes[target[1]][1]

    # return True if target is out of map (early catch increases performance)
    if target_x + target_width > mapWidth or target_y + target_height > mapHeight:
        return True

    # if there's no water and target is in map, no need to check for collision..
    if len(water_list) == 0:
        return False

    for water_body in [w for w in water_list if w[id] != target[id]]:
        # Same type of comparison as shortest distance function, adapted for water
        # Keep in mind that the UPPER LEFT corner of the map is position (0,0)

        # comparison water is above target if target's lowest Y coordinate > water body's highest Y coordinate
        if target_y >= water_body[y] + water_body[height]:
            y_distance = 1

        # water is below target if..
        elif target_y + target_height <= water_body[y]:
            y_distance = 1

        # otherwise it is horizontally next to target, so y = 0 because we only need horizontal distance
        else:
            y_distance = -1

        # do the same for the x axis
        if target_x >= water_body[x] + water_body[width]:
            x_distance = 1

        # comparison house is right of target if..
        elif target_x + target_width <= water_body[x]:
            x_distance = 1

        # otherwise it is vertically in the same column
        else:
            x_distance = -1

        # if they are in the same column and row, we have intersection
        if x_distance == -1 and y_distance == -1:
            return True
    return False

# Puts houses in a random place of a grid-like x,y range, works much faster than just any random row/column
def place_houses_grid():
    building_locations = []
    id = 0
    tiles_apart = 5
    # Make a list of positions in a grid-like fashion
    grid = [(x,y) for y in range(tiles_apart/2,mapHeight,tiles_apart) for x in range(tiles_apart/2,mapWidth,tiles_apart)]
    # shuffle it so we can pop random positions
    random.shuffle(grid)
    for house in buildingList:
        id += 1
        while len(grid) > 0:
            x,y = grid.pop(0)
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
            print "No position left to place building!"

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


# this function gets the shortest distance between a given house_object and any other house
def get_shortest_distance(house_object, house_positions):
    id = 0
    type = 1
    x = 2
    y = 3
    shortest_distance = None

    # check if house does not stand in any water!
    if check_if_in_water(house_object,water_bodies_list):
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


### ALGORITHMS ###

# Stops any form of iterative algorithms
def stop_algorithm():
    global climbing
    climbing = False
climbing = False

# (non-stochastic) hillclimbing calculates every possible step, this value affects performance a lot!
# smaller max steps is faster, but less increase in result per iteration
# Test results of various max_steps values can be found in our report
max_steps = 5


# this function tries to move a house in every possible direction (between 1 and the max_steps), and accepts the highest VALUE
def start_hillClimbing():
    global climbing
    global house_positions

    start_position, total_extra_free_space, total_value = calculate_score(house_positions)

    # export data if needed
    file_date = datetime.datetime.now().strftime(r"%H;%M;%S %d-%m-%y")
    file_name = "norm hill " + file_date + ".csv"
    with open(file_name, "wb") as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow(["iteration","total_value","total_score", "score_list","water_list"])
        iteration = 0
        climbing = True
        while climbing is True:
            pygame.event.get()
            iteration += 1

            # Display iteration
            font = pygame.font.Font("freesansbold.ttf", 16)
            iteration_text = font.render("Iteration: " + str(iteration) + "               ", 1, (250, 250, 250), (0, 0, 0))
            display.blit(iteration_text, (mapWidth * tileSize + 50, (mapHeight * tileSize) / 2 - 50))
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
                for i in xrange(1, max_steps + 1):
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

            button("STOP", mapWidth * tileSize + 275, 175, 100, 25, (237, 28, 36), (191, 15, 23), stop_algorithm)
            writer.writerow([iteration,total_value,total_extra_free_space, house_positions, water_bodies_list])
            pygame.display.flip()


# stochastic hillclimber just generates a random movement and accepts if this improves or equals the original value
def start_stochastic_hillClimbing(favor_free_space = False):
    global climbing
    global house_positions
    global water_bodies_list

    start_position, total_extra_free_space, total_value = calculate_score(house_positions)

    # export data if needed
    file_date = datetime.datetime.now().strftime(r"%H;%M;%S %d-%m-%y")
    file_name = "stoch hill " + file_date + ".csv"
    with open(file_name, "wb") as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow(["iteration","total_value","total_score", "score_list","water_list"])
        iteration = 0
        climbing = True
        while climbing is True:
            iteration += 1
            # Display iteration
            font = pygame.font.Font("freesansbold.ttf", 16)
            iteration_text = font.render("Iteration: " + str(iteration) + "               ", 1, (250, 250, 250), (0, 0, 0))
            display.blit(iteration_text, (mapWidth * tileSize + 50, (mapHeight * tileSize) / 2 - 50))
            print "ITERATION NUMBER: ", iteration

            # Select a random building from the list..
            id, buildingType, x, y, score = house_positions[random.randint(0, len(house_positions) - 1)]

            # implement a chance to swap two houses
            new_value = False
            if random.random() < 0.2:
                # to make sure we're not swapping the same house (type) which would obviously be inefficient
                efficient_swaps = [o for o in house_positions if o[1] != buildingType]
                print "Trying to swap.."

                # select another random building from this list
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
                # generate a random direction (8 possible directions with equal chance)
                move_magnitude = random.randint(1, max_steps)
                d = 1/8.0
                rand_d = random.random()

                if rand_d < d: # direction is up
                    move_direction = (0,-move_magnitude)
                elif rand_d < d * 2: # up right
                    move_direction = (move_magnitude,-move_magnitude)
                elif rand_d < d * 3: # right
                    move_direction = (move_magnitude,0)
                elif rand_d < d * 4: # down right
                    move_direction = (move_magnitude,move_magnitude)
                elif rand_d < d * 5: # down
                    move_direction = (0,move_magnitude)
                elif rand_d < d * 6: # down left
                    move_direction = (-move_magnitude,move_magnitude)
                elif rand_d < d * 7: # left
                    move_direction = (-move_magnitude,0)
                elif rand_d <= d * 8: # up left
                    move_direction = (-move_magnitude,-move_magnitude)

                temp_score_list = [house if house[0] != id
                                   else [id, buildingType, x + move_direction[0], y + move_direction[1]]
                                   for house in house_positions]
                new_score_list, new_score, new_value = calculate_score(temp_score_list)

            # check if we need to update the highest (or equal) value
            if new_score_list and new_score and new_value:
                if not favor_free_space and new_value >= total_value \
                        or favor_free_space and new_score >= total_extra_free_space:
                    house_positions = new_score_list
                    total_value = new_value
                    total_extra_free_space = new_score
                    print "Higher or equal value found: " + str(new_value)
                    update_game_display(new_score_list)

            button("STOP", mapWidth * tileSize + 275, 175, 100, 25, (237, 28, 36), (191, 15, 23), stop_algorithm)
            # Write row of data to csv file
            writer.writerow([iteration,total_value,total_extra_free_space, house_positions, water_bodies_list])
            # flip display and get events (clicks)
            pygame.display.flip()
            pygame.event.get()


# Simulated Annealing, pretty much a copy of hillclimbing apart from a chance to accept lower values..
def start_simulated_annealing(favor_free_space = False):
    global climbing
    global house_positions

    start_position, total_extra_free_space, total_value = calculate_score(house_positions)
    highest_position,highest_extra_free_space, highest_value = start_position, total_extra_free_space, total_value
    iteration = 0
    # export data if needed
    file_date = datetime.datetime.now().strftime(r"%H;%M;%S %d-%m-%y")
    file_name = "sim anneal " + file_date + ".csv"
    with open(file_name, "wb") as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow(["iteration","total_value","total_score", "score_list","water_list"])
        # initial temperature for Boltzmann distribution, this will cool down approaching zero
        if favor_free_space:
            # if algorithms favors free space, the initial temperature is..
            temp = total_extra_free_space / float(houseAmount)
        else:
            # if algorithms favors value, the initial temperature is..
            temp = total_value / houseAmount / 1000
        climbing = True
        while climbing is True:
            pygame.event.get()
            iteration += 1
            # Select a random building from the list..
            id, buildingType, x, y, score = house_positions[random.randint(0, len(house_positions) - 1)]

            # A chance of 20% to swap two houses
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

                # calculate the new score..
                new_score_list, new_score, new_value = calculate_score(
                    temp_score_list + [new_house] + [new_house_comparison])

            # otherwise move in a random direction
            else:
                # generate a random direction (8 possible directions with equal chance)
                move_magnitude = random.randint(1, max_steps)
                d = 1/8.0
                rand_d = random.random()

                if rand_d < d: # direction is up
                    move_direction = (0,-move_magnitude)
                elif rand_d < d * 2: # up right
                    move_direction = (move_magnitude,-move_magnitude)
                elif rand_d < d * 3: # right
                    move_direction = (move_magnitude,0)
                elif rand_d < d * 4: # down right
                    move_direction = (move_magnitude,move_magnitude)
                elif rand_d < d * 5: # down
                    move_direction = (0,move_magnitude)
                elif rand_d < d * 6: # down left
                    move_direction = (-move_magnitude,move_magnitude)
                elif rand_d < d * 7: # left
                    move_direction = (-move_magnitude,0)
                elif rand_d <= d * 8: # up left
                    move_direction = (-move_magnitude,-move_magnitude)

                temp_score_list = [house if house[0] != id else [id, buildingType, x + move_direction[0], y + move_direction[1]] for house in house_positions]
                new_score_list, new_score, new_value = calculate_score(temp_score_list)

            # check if we need to update the highest (or equal) value
            if new_score_list and new_score and new_value:
                if not favor_free_space and new_value >= total_value \
                        or favor_free_space and new_score >= total_extra_free_space:
                    house_positions = new_score_list
                    total_value = new_value
                    total_extra_free_space = new_score
                    print "Higher or equal value found: " + str(new_value)
                    highest_position, highest_extra_free_space, highest_value = new_score_list, new_score, new_value
                    update_game_display(new_score_list)

                # also a chance to accept lower values..
                elif new_score_list:
                    if not favor_free_space:
                        # if difference is based on total value (which will be high numbers), we need to scale this value down
                        value_difference = (total_value - new_value) / 1000

                    else:
                        value_difference = total_extra_free_space - new_score

                    # Important math here deciding the acceptance chance
                    acceptance_chance = math.exp(-value_difference / temp) / 2 # chance between 0.5 and eventually 0
                    probability = random.random()
                    print "acceptance chance: " + str(acceptance_chance), "difference: -" + str(value_difference)

                    if probability < acceptance_chance:
                        house_positions = new_score_list
                        total_value = new_value
                        total_extra_free_space = new_score
                        print "Accepting lower value..: " + str(new_value)
                        update_game_display(new_score_list)

            # adjust the temperature either way..
            temp *= 0.999

            # Display iteration
            font = pygame.font.Font("freesansbold.ttf", 16)
            iteration_text = font.render("Iteration: " + str(iteration) + "  Temp:" + str(temp) + "              ", 1, (250, 250, 250), (0, 0, 0))
            display.blit(iteration_text, (mapWidth * tileSize + 50, (mapHeight * tileSize) / 2 - 50))

            # write the new row of data to the csv file
            writer.writerow([iteration,total_value,total_extra_free_space, house_positions, water_bodies_list])

            # Spawn the stop button, quite important
            button("STOP", mapWidth * tileSize + 275, 175, 100, 25, (237, 28, 36), (191, 15, 23), stop_algorithm)
            pygame.display.flip()


### END OF ALGORITHMS ###

### USER INTERFACE ###

# this function updates the display given a list of house positions and scores
# house_scores contains arrays representing houses
def update_game_display(house_scores):
    if not house_scores:
        house_scores = []

    # display the raster-like background
    texture = pygame.transform.scale(textures[grass], (mapWidth * tileSize,mapHeight * tileSize))
    display.blit(texture, (0,0))

    # draw water if any
    global water_bodies_list
    if not water_bodies_list:
        water_bodies_list = []

    for id, x, y,width,height in water_bodies_list:
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
        buildingValue = houseValues[buildingType][0] * (1 + (houseValues[buildingType][1] * score))
        display.blit(scoreText, ((x * tileSize + centerX), (y * tileSize + centerY)))
        totalValue += buildingValue

    # Display the total calculated value and the total score (extra free space)
    totalValueText = font.render("Total value: " + str(totalValue) + "    ", 1, (250, 250, 250), (0, 0, 0))
    totalScoreText = font.render("Total (extra) free space: " + str(totalScore) + "    ", 1, (250, 250, 250), (0, 0, 0))
    display.blit(totalValueText, (mapWidth * tileSize + 50, (mapHeight * tileSize) / 2))
    display.blit(totalScoreText, (mapWidth * tileSize + 50, (mapHeight * tileSize) / 2 + 50))
    # update the display
    pygame.display.update()


# converting text objects to a surface and rectangle..
def text_objects(msg, font):
    textSurface = font.render(msg, 1, (255, 255, 255))
    textRect = textSurface.get_rect()
    return textSurface, textRect


# function to spawn buttons
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


# function to place houses random according to place_grid function, and update
def place_grid_and_update():
    global house_positions
    house_positions = place_houses_grid()
    house_positions, total_score, total_value = calculate_score(house_positions)
    update_game_display(house_positions)


# Reset water and houses in random positions
def reset_water_random():
    global water_bodies_list
    water_bodies_list = place_water_random()
    place_grid_and_update()


# Put water in a specific position (see report) and spawn houses random
def place_water_1():
    global water_bodies_list
    water_bodies_list = [[61, 80, 45, 160, 40], [62, 80, 130, 160, 40], [63, 80, 215, 160, 40]]
    place_grid_and_update()


# writes a sample of 1000 randomly placed solutions, and shows the highest VALUE found among those at the end
def random_sample(function = place_houses_grid):
    global house_positions
    file_date = datetime.datetime.now().strftime(r"%H;%M;%S %d-%m-%y")
    file_name = "randomsample "+str(houseAmount)+"houses "+file_date + ".csv"
    with open(file_name, "wb") as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow(["total_value","total_score", "score_list","water_list"])
        highest_value = 0
        font = pygame.font.Font("freesansbold.ttf", 16)
        for i in range(1000):
            # Display iteration
            iteration_text = font.render("Writing row: " + str(i) + "               ", 1, (250, 250, 250), (0, 0, 0))
            display.blit(iteration_text, (mapWidth * tileSize + 50, (mapHeight * tileSize) / 2 - 50))
            # calculate score based on placing function
            scoreList, totalScore, totalValue = calculate_score(function())
            writer.writerow([totalValue,totalScore,scoreList,water_bodies_list])
            if highest_value < totalValue:
                highest_value = totalValue
                highest_scoreList = scoreList
            pygame.event.get()
            pygame.display.flip()
    house_positions = highest_scoreList
    update_game_display(highest_scoreList)
    # save a screenshot of the highest value
    pygame.image.save(display, "screenshot "+ file_date +".jpeg")


# changes amount of houses that will be placed
def setHouseAmount(amount):
    global houseAmount
    houseAmount = amount
    global buildingList
    # Rebuild the buildinglist according to new houseAmount
    buildingList = [largeHouse] * int(houseAmount * 0.15) + [mediumHouse] * int(houseAmount * 0.25) + [smallHouse] * int(
    houseAmount * 0.6)
    # Replace the houses..
    place_grid_and_update()


# Spawn random water and houses if the simulation opens
water_bodies_list = place_water_random()
house_positions, total_value, total_score = calculate_score(place_houses_grid())
update_game_display(house_positions)

# The main "game" loop of pygame, running until program exits
running = True
clock = pygame.time.Clock()
while running:
    # get all the user events
    for event in pygame.event.get():
        # if the user wants to quit
        if event.type == QUIT:
            # end the game and close the window
            pygame.quit()
            sys.exit()

    # Spawn all the buttons on screen..
    button("Random", mapWidth * tileSize + 25, 25, 100, 25, colors["lightgrey"], colors["darkgrey"], place_grid_and_update)
    button("R. Sample", mapWidth * tileSize + 25, 75, 100, 25, colors["lightgrey"], colors["darkgrey"], random_sample)

    button("Rand water", mapWidth * tileSize + 25, mapHeight * tileSize - 75, 100, 25, colors["blue"], colors["darkblue"], reset_water_random)
    button("water 1", mapWidth * tileSize + 150, mapHeight * tileSize - 75, 100, 25, colors["blue"], colors["darkblue"], place_water_1)
    # hide these buttons if map is empty
    if len(house_positions) > 0:
        button("Sim Anneal", mapWidth * tileSize + 275, 125, 100, 25, colors["lightgrey"], colors["darkgrey"], start_simulated_annealing, False)
        button("Hillclimbing", mapWidth * tileSize + 275, 25, 100, 25, colors["lightgrey"], colors["darkgrey"], start_hillClimbing)
        button("Stoch. Hill", mapWidth * tileSize + 275, 75, 100, 25, colors["lightgrey"], colors["darkgrey"], start_stochastic_hillClimbing, False)

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
    # limit to 60 fps while in this game loop
    clock.tick(60)
