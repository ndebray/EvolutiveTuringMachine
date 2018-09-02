# Turing machine
NB_OF_STATES = 100
NB_OF_SYMBOLS = 2

# Encoding of the inputs and outputs
OUTPUT_ENCODING_LENGTH = 5 # Move + Rotate + Eat + Divide + Mate
ENERGY_LEVEL_ENCODING_LENGTH = 8
ENERGY_LEVEL_VALUE_MAX = 200.0
FOOD_LEVEL_ENCODING_LENGTH = 8
FOOD_LEVEL_VALUE_MAX = 200.0
DISTANCE_ENCODING_LENGTH = 8
DISTANCE_VALUE_MAX = 500
TOTAL_ENCODING_LENGTH = OUTPUT_ENCODING_LENGTH + ENERGY_LEVEL_ENCODING_LENGTH + FOOD_LEVEL_ENCODING_LENGTH + DISTANCE_ENCODING_LENGTH

# Cell
INIT_ENERGY_LEVEL = 200.0
ENERGY_LOSS_RATE = 0.001 # The cell lost 3*8 = 24 just with the inputs
FOOD_EAT_RATE = 10.0 # The food a cel will eat in one round
NB_OF_LOOPS = 100

# Division
ENABLE_DIVISION = True
DIVISION_ENERGY = 5.0 # The energy needed before and lost by a cell after division

# Mate
ENABLE_MATE = True
MATE_ENERGY = 0.0
MATE_PB = 0.5 # The child cell will have half of the genome of each parent

# Mutation
MUTATION_PB = 0.001
INCREASE_PB = 0.0001 # Extend the action table with a new state
DECREASE_PB = 0.0001 # Delete the last state of the action table

# Petri dish
INIT_FOOD_LEVEL = 100.0
INIT_POPULATION = 500
WIDTH = 100
HEIGHT = 100
MAX_NB_OF_CELLS = 1000 # -1 = no limit

# GUI
IMAGE_RESIZE = 6
FRAME_RATE = 5
FILENAME = "data.bin"
