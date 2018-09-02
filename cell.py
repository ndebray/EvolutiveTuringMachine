import config
import encode
from turingmachine import TuringMachine


class Cell:

    def __init__(self,
        init_energy_level = config.INIT_ENERGY_LEVEL,
        randomize = True):

        self.energy_level = init_energy_level
        self.turing_machine = TuringMachine()
        if randomize == True:
            self.turing_machine.randomize()

    def __del__(self):

        del self.energy_level
        del self.turing_machine

    def loseEnergy(self,
        energy_lose_rate = config.ENERGY_LOSS_RATE):

        energy_lost = energy_lose_rate * len(self.turing_machine.tape.tape) * self.turing_machine.nb_of_states * self.turing_machine.nb_of_symbols
        energy_lost = min(energy_lost, self.energy_level)
        self.energy_level -= energy_lost

        return energy_lost

    def writeEnvironment(self, energy_level, food_level, distance):

        tape = self.turing_machine.tape

        index = config.OUTPUT_ENCODING_LENGTH # Output + Input + Rest of the tape
        energy_level_normalized = energy_level / config.ENERGY_LEVEL_VALUE_MAX
        energy_level_encoded = encode.encode2_8(energy_level_normalized)
        tape.writeArray(energy_level_encoded, index)

        index += config.ENERGY_LEVEL_ENCODING_LENGTH
        food_level_normalized = food_level / config.FOOD_LEVEL_VALUE_MAX
        food_level_encoded = encode.encode2_8(food_level_normalized)
        tape.writeArray(food_level_encoded, index)

        index += config.FOOD_LEVEL_ENCODING_LENGTH
        distance_normalized = distance / config.DISTANCE_VALUE_MAX
        distance_encoded = encode.encode2_8(distance_normalized)
        tape.writeArray(distance_encoded, index)

    def debug(self):

        print "Energy level: ", self.energy_level

def test_energy():

    cell = Cell(100.0)
    cell.debug()
    cell.turing_machine.debugConfiguration()
    cell.turing_machine.tape.debug()

    cell.loseEnergy(1.0)
    cell.debug()

    return

if __name__ == "__main__":

    test_energy()
