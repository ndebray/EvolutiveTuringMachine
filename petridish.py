import numpy as np
import random
import copy
import time
import signal

import config
from cell import Cell

class PetriDish:

    def __init__(self,
        width = config.WIDTH,
        height = config.HEIGHT,
        init_food_level = config.INIT_FOOD_LEVEL,
        init_population = config.INIT_POPULATION):

        self.width = width
        self.height = height
        self.init_food_level = init_food_level
        self.init_population = init_population

        self.food_map = np.full((width, height), init_food_level)

        self.cells = []
        self.new_cells = []

        self.nb_of_divisions = 0
        self.nb_of_matings = 0
        self.nb_of_mutations = 0

        self.generation = 0

        for i in range(init_population):

            is_spot_busy = True
            while is_spot_busy == True:
                x = random.randint(0, self.width - 1)
                y = random.randint(0, self.height - 1)
                is_spot_busy = self.isSpotBusyOrOutside(x,y)

            direction = random.randint(0, 3)
            cell = Cell()
            self.cells.append((x, y, direction, cell))

    def findCell(self, x, y):

        for (x_, y_, direction_, cell_) in self.cells + self.new_cells:
            if x == x_ and y == y_:
                return (x_, y_, direction_, cell_)

        return (None, None, None, None)

    def isSpotBusyOrOutside(self, x, y):

        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return True

        (x_, y_, direction_, cell_) = self.findCell(x, y)
        return cell_ != None

    def cellOrWallDistance(self, index):

        (x_1, y_1, direction_1, cell_1) = self.cells[index]

        if direction_1 == 0: # North
            for (x_2, y_2, direction_2, cell_2) in self.cells:
                if x_1 == x_2 and y_1 < y_2:
                    return y_2 - y_1
            return self.height - y_1

        elif direction_1 == 1: # East
            for (x_2, y_2, direction_2, cell_2) in self.cells:
                if x_1 < x_2 and y_1 == y_2:
                    return x_2 - x_1
            return self.width - x_1

        elif direction_1 == 2: # South
            for (x_2, y_2, direction_2, cell_2) in self.cells:
                if x_1 == x_2 and y_1 > y_2:
                    return y_1 - y_2
            return y_1

        elif direction_1 == 3: # West
            for (x_2, y_2, direction_2, cell_2) in self.cells:
                if x_1 > x_2 and y_1 == y_2:
                    return x_1 - x_2
            return x_1

    def spreadFood(self, food):

        self.food_map += food / (self.width * self.height)
        return

    def rotateCell(self, index):

        (x, y, direction, cell) = self.cells[index]
        direction = (direction + 1) % 4
        self.cells[index] = (x, y, direction, cell)
        return

    def getCoordInFront(self, x, y, direction):

        if direction == 0: # North
            new_x = x
            new_y = y + 1
        elif direction == 1: # East
            new_x = x + 1
            new_y = y
        elif direction == 2: # South
            new_x = x
            new_y = y - 1
        elif direction == 3: # West
            new_x = x - 1
            new_y = y
        return new_x, new_y

    def moveCell(self, index):

        #print "Cell #", index, "is moving"

        (x, y, direction, cell) = self.cells[index]
        (new_x, new_y) = self.getCoordInFront(x, y, direction)

        if self.isSpotBusyOrOutside(new_x, new_y) == True:
            return False

        self.cells[index] = (new_x, new_y, direction, cell)
        return True

    def makeCellEat(self, index, food_eat_rate = config.FOOD_EAT_RATE):

        #print "Cell #", index, "is eating"

        (x, y, direction, cell) = self.cells[index]
        food_level_in_spot = self.food_map[x][y]

        food_eaten = min(food_eat_rate, config.ENERGY_LEVEL_VALUE_MAX - cell.energy_level) # The cell can't eat more than its energy level max
        food_eaten = min(food_level_in_spot, food_eaten) # Only eat the food available

        cell.energy_level += food_eaten
        self.food_map[x][y] -= food_eaten

        return food_eaten

    def makeCellLoseEnergy(self, index, energy_lose_rate = config.ENERGY_LOSS_RATE):

        (x, y, direction, cell) = self.cells[index]
        energy_lost = cell.loseEnergy()
        self.spreadFood(energy_lost)

        return energy_lost

    def divideCell(self, index):

        if config.ENABLE_DIVISION == False:
            return False

        # Limit the number of cells in the petri dish
        nb_of_cells = len(self.cells) + len(self.new_cells)
        if config.MAX_NB_OF_CELLS >= 0 and nb_of_cells >= config.MAX_NB_OF_CELLS:
            return False

        # Check if the cell has enough energy to divide
        (x, y, direction, cell) = self.cells[index]
        if cell.energy_level < config.DIVISION_ENERGY:
            return False

        # Check if the spot in front of the cell in free to create the new cell
        (new_x, new_y) = self.getCoordInFront(x, y, direction)
        if self.isSpotBusyOrOutside(new_x, new_y) == True:
            return False

        # Make the cell lose energy and spread it
        cell.energy_level -= config.DIVISION_ENERGY
        self.spreadFood(config.DIVISION_ENERGY)

        # Deep copy the cell
        new_cell = copy.deepcopy(cell)
        new_cell.turing_machine.reset()

        # Divide the energy of the parent cell between the two cells
        cell.energy_level /= 2
        new_cell.energy_level /= 2

        self.new_cells.append((new_x, new_y, direction, new_cell))
        self.nb_of_divisions += 1

        return True

    def mateCells(self, index):
        # Mate with the cell in front (second parent) and create the child in front of the second parent

        if config.ENABLE_MATE == False:
            return False

        # Limit the number of cells in the petri dish
        nb_of_cells = len(self.cells) + len(self.new_cells)
        if config.MAX_NB_OF_CELLS >= 0 and nb_of_cells >= config.MAX_NB_OF_CELLS:
            return False

        # Check if the mating cell has enough energy to mate
        (parent_1_x, parent_1_y, parent_1_direction, parent_1_cell) = self.cells[index]
        if parent_1_cell.energy_level < config.MATE_ENERGY:
            return False

        # Find the cell in front of the mating cell
        (parent_2_x, parent_2_y) = self.getCoordInFront(parent_1_x, parent_1_y, parent_1_direction)
        (parent_2_x, parent_2_y, parent_2_direction, parent_2_cell) = self.findCell(parent_2_x, parent_2_y)
        if parent_2_cell == None:
            return False

        # Check if the spot in front of parent 2 cell is free to create the child
        (child_x, child_y) = self.getCoordInFront(parent_2_x, parent_2_y, parent_2_direction)
        if self.isSpotBusyOrOutside(child_x, child_y) == True:
            return False

        child_cell = Cell()
        child_cell.turing_machine = parent_1_cell.turing_machine.mate(parent_2_cell.turing_machine)

        parent_1_cell.energy_level /= 2
        parent_2_cell.energy_level /= 2
        child_cell.energy_level = parent_1_cell.energy_level + parent_2_cell.energy_level

        self.new_cells.append((child_x, child_y, parent_1_direction, child_cell))
        #print "Mate!!!"
        self.nb_of_matings += 1

        return True

    def mutateCell(self, cell):

        pb = random.random()
        if pb < config.MUTATION_PB:
            cell.turing_machine.mutate()
            self.nb_of_mutations += 1

        pb = random.random()
        if pb < config.INCREASE_PB:
            cell.turing_machine.addState()
            self.nb_of_mutations += 1

        pb = random.random()
        if pb < config.DECREASE_PB:
            cell.turing_machine.removeState()
            self.nb_of_mutations += 1

        return cell

    def loop(self, loop = True):

        if loop == True and len(self.cells) == 0:
            self.__init__(
                self.width,
                self.height,
                self.init_food_level,
                self.init_population
            )

        self.nb_of_divisions = 0
        self.nb_of_matings = 0
        self.nb_of_mutations = 0

        self.new_cells = []
        for index, (x, y, direction, cell) in enumerate(self.cells):

            # Set the input of the turing machines with the environment state
            energy_level = cell.energy_level
            food_level = self.food_map[x][y]
            distance = self.cellOrWallDistance(index)
            cell.writeEnvironment(energy_level, food_level, distance)

            # Execute the turing machine
            for i in range(config.NB_OF_LOOPS):
                cell.turing_machine.next()

            # Read the resulting tape and execute the action
            rotate_action = cell.turing_machine.tape.read(0)
            if rotate_action == 1:
                self.rotateCell(index)

            move_action = cell.turing_machine.tape.read(1)
            if move_action == 1:
                self.moveCell(index)

            eat_action = cell.turing_machine.tape.read(2)
            if eat_action == 1:
                self.makeCellEat(index)

            divide_action = cell.turing_machine.tape.read(3)
            if divide_action == 1:
                self.divideCell(index)

            mate_action = cell.turing_machine.tape.read(4)
            if mate_action == 1:
                self.mateCells(index)

            for i in range(4):
                cell.turing_machine.tape.writeArray([0]*5, 0) # Reinit the output

            # Mutate
            self.mutateCell(cell)

            # Lose energy
            self.makeCellLoseEnergy(index)
            if cell.energy_level <= 0:
                del cell
                del self.cells[index]

        # Merge the new cells with the current array
        self.cells = self.cells + self.new_cells

        self.generation += 1

        return len(self.cells)

    def debug(self):

        print "Width: ", self.width
        print "Height: ", self.height
        print "Food level: "
        print self.food_map

    def debugCells(self):

        print "index", "x", "y", "direction", "energy level"
        for index, (x, y, direction, cell) in enumerate(self.cells):
            print index, x, y, direction, cell.energy_level

    def getTotalFood(self):

        total_food_level = np.sum(self.food_map)
        return total_food_level

    def getTotalEnergy(self):

        total_energy_level = 0
        for (x, y, direction, cell) in self.cells:
            total_energy_level += cell.energy_level

        return total_energy_level

    def getTotalFoodAndEnergy(self):

        return self.getTotalFood() + self.getTotalEnergy()

def test_food():

    pd = PetriDish(width = 10, height = 10, init_population = 1)
    (x, y, direction, cell) = pd.cells[0]
    pd.cells[0] = (0, 0, 0, cell)
    pd.debug()

    pd.spreadFood(1000.0)
    pd.debug()

    pd.makeCellEat(0, 40.0)
    pd.debug()

    return

def test_move():

    pd = PetriDish(width = 10, height = 10, init_population = 2)

    (x, y, direction, cell) = pd.cells[0]
    x = 0
    y = 0
    direction = 3
    pd.cells[0] = (x, y, direction, cell)

    (x, y, direction, cell) = pd.cells[1]
    x = 0
    y = 5
    direction = 3
    pd.cells[1] = (x, y, direction, cell)

    pd.debugCells()

    for i in range(4):

        print "move"
        print pd.moveCell(0)
        pd.debugCells()
        print "Distance: ", pd.cellOrWallDistance(0)

        for i in range(2):

            print "rotate"
            pd.rotateCell(0)
            pd.debugCells()
            print "Distance: ", pd.cellOrWallDistance(0)

    return

def test_divide():

    pd = PetriDish(width = 10, height = 10, init_population = 1)
    (x, y, direction, cell) = pd.cells[0]
    x = 0
    y = 0
    direction = 3
    pd.cells[0] = (x, y, direction, cell)

    pd.debugCells()
    print "Division: ", pd.divideCell(0)
    pd.debugCells()

    pd.rotateCell(0)
    print "Division: ", pd.divideCell(0)
    pd.debugCells()

    return

def test_execute():

    pd = PetriDish(width = 10, height = 10, init_population = 10)
    for i in range(10):
        pd.loop()
        print "Total food and energy:", pd.getTotalEnergy() + pd.getTotalFood()

    #for (x, y, direction, cell) in pd.cells:
    #    cell.turing_machine.debugConfiguration()
    #    cell.turing_machine.tape.debugState()

_stop = False

def stop(signal, frame):

    global _stop
    print "Stop"
    _stop = True

def test_performance():

    random.seed(123)

    pd = PetriDish(width = 200, height = 200, init_population = 1000)
    loop = 0
    while _stop == False:
        print "Loop #", loop, "------------------------------"
        print "Number of cells:", len(pd.cells)
        loop += 1
        start = time.time()
        pd.loop(debug_time = True)
        end = time.time()
        elapsed_time = end - start
        print "Total execution time:", elapsed_time

if __name__ == "__main__":

    signal.signal(signal.SIGINT, stop)

    #test_food()
    #test_move()
    #test_divide()
    test_execute()
    #test_performance()
