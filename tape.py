import encode

class Tape:

    def __init__(self, nb_of_symbols, init_length = 1, init_symbol = 0):

        self.nb_of_symbols = nb_of_symbols
        self.init_length = init_length
        self.init_symbol = init_symbol
        self.reset()

    def __del__(self):

        del self.nb_of_symbols
        del self.init_symbol
        del self.tape
        del self.tape_index
        del self.tape_offset

    def reset(self):
        self.tape = [ self.init_symbol ] * self.init_length
        self.tape_index = 0 # Can be < 0
        self.tape_offset = 0 # Always > 0

    def linearize(self):
        for i in range(len(self.tape)):
            self.tape[i] = i % self.nb_of_symbols

    def addLeft(self):

        self.tape.insert(0, 0)
        self.tape_offset += 1

    def addRight(self):

        self.tape.append(0)

    def moveLeft(self):

        real_index = self.tape_index + self.tape_offset
        if real_index == 0:
            self.addLeft()

        self.tape_index -= 1

    def moveRight(self):

        real_index = self.tape_index + self.tape_offset
        if real_index == len(self.tape) - 1:
            self.addRight()

        self.tape_index += 1

    def read(self, index = None):

        if index == None:
            index = self.tape_index

        real_index = index + self.tape_offset
        result = self.tape[real_index]

        return result

    def readArray(self, index = None, length = 0):

        if index == None:
            index = self.tape_index

        real_index = index + self.tape_offset
        result = self.tape[real_index:real_index + length]

        return result

    def write(self, symbol, index = None):

        if index == None:
            index = self.tape_index

        real_index = index + self.tape_offset
        self.tape[real_index] = symbol

        return

    def writeArray(self, array, index = None):

        if index == None:
            index = self.tape_index

        for i, symbol in enumerate(array):
            self.write(symbol, index + i)

        return

    def debugConfiguration(self):

        print "Number of symbols: ", self.nb_of_symbols
        print "Init length: ", self.init_length
        print "Init symbol: ", self.init_symbol

    def debugState(self):

        print "Tape length: ", len(self.tape)
        print "Tape index: ", self.tape_index
        print "Tape offset: ", self.tape_offset
        print "Tape real index: ", self.tape_index + self.tape_offset
        print "Tape: ", self.tape

    # Other functions ##############################

    def read_(self, index = None, length = None):

        if index == None or length == None:
            index = self.tape_index
            length = 1

        real_index = max(0, index + self.tape_offset)
        result = self.tape[real_index : real_index + length]

        # Add padding in case the asked length is higher than the tape's length
        padding_before = abs(min(0, index + self.tape_offset))
        padding_after = max(0, length - padding_before - len(result))
        result = [0] * padding_before + result + [0] * padding_after

        return result

    def write_(self, symbol, index = None):

        if symbol < 0 or symbol >= self.nb_of_symbols:
            raise ValueError('The symbol is not in the alphabet.')

        if index == None:
            index = self.tape_index

        real_index = index + self.tape_offset
        for i in range(abs(min(0, real_index))):
            self.addLeft()
        for i in range(max(0, real_index - len(self.tape) + 1)):
            self.addRight()

        real_index = index + self.tape_offset
        self.tape[real_index] = symbol

        return

def test_create():

    tape = Tape(nb_of_symbols = 3)
    tape.debugState()

    tape = Tape(nb_of_symbols = 4, init_length = 5)
    tape.debugState()

    tape = Tape(nb_of_symbols = 5, init_length = 10, init_symbol = 3)
    tape.debugState()

def test_reset():

    tape = Tape(nb_of_symbols = 3, init_length = 5, init_symbol = 2)
    tape.tape = [ i for i in range(10) ]
    for i in range(3):
        tape.moveLeft()

    tape.debugConfiguration()
    tape.debugState()

    tape.reset()
    tape.debugState()

def test_move():

    tape = Tape(nb_of_symbols = 3)
    tape.debugState()

    print "moveRight"
    for i in range(3):
        tape.moveRight()
        tape.debugState()

    print "moveLeft"
    for i in range(6):
        tape.moveLeft()
        tape.debugState()

def test_read():

    tape = Tape(nb_of_symbols = 3)
    tape.tape = [ i for i in range(10) ]
    tape.debugState()

    for i in range(10):
        symbol = tape.read()
        print "Symbol:", symbol
        tape.moveRight()

    for i in range(10):
        symbol = tape.read(i)
        print "Symbol:", symbol

def test_read_array():

    tape = Tape(nb_of_symbols = 3)
    tape.tape = [ i for i in range(10) ]
    tape.debugState()

    symbols = tape.readArray(3, 3)
    print "symbols:", symbols

def test_write():

    tape = Tape(nb_of_symbols = 3, init_length = 10)
    tape.debugState()

    for i in range(10):
        symbol = tape.write(i)
        tape.debugState()
        tape.moveRight()

    for i in range(10):
        symbol = tape.write(i, 9 - i)
        tape.debugState()

def test_write_array():

    tape = Tape(nb_of_symbols = 3, init_length = 10)
    tape.debugState()

    tape.writeArray([ i for i in range(5) ], 5)
    tape.debugState()

if __name__ == "__main__":

    #test_create()
    #test_reset()
    #test_move()
    #test_read()
    test_read_array()
    #test_write()
    #test_write_array()
