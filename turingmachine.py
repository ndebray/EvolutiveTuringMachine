import random
import time
import copy
from tape import Tape

import config

class TuringMachine:

    def __init__(self,
        nb_of_states = config.NB_OF_STATES,
        nb_of_symbols = config.NB_OF_SYMBOLS,
        init_state = 0,
        init_tape_length = config.TOTAL_ENCODING_LENGTH):

        self.nb_of_states = nb_of_states
        self.nb_of_symbols = nb_of_symbols

        self.init_state = init_state
        self.current_state = init_state
        self.tape = Tape(nb_of_symbols, init_tape_length)

        # [old_state][symbon_read] => ( symbol_to_write, movement, new_state )
        #self.action_table = [[ ( 0, '', 0 ) ] * nb_of_symbols ] * nb_of_states # Problem = works by reference
        self.action_table = []
        for old_state in range(nb_of_states):
            self.action_table.append([])
            for symbol_read in range(nb_of_symbols):
                self.action_table[old_state].append(( 0, '', 0 ))

    def __del__(self):

        del self.nb_of_states
        del self.nb_of_symbols
        del self.init_state
        del self.current_state
        del self.action_table
        del self.tape

    def next(self):

        symbol_read = self.tape.read()
        try:
            (symbol_to_write, movement, new_state) = self.action_table[self.current_state][symbol_read]
        except IndexError:
            print self.current_state, symbol_read
            self.debugConfiguration()
            self.debugState()

        # Write the new symbol
        self.tape.write(symbol_to_write)

        # Move the tape cursor
        if movement == 'l':
            self.tape.moveLeft()
        elif movement== 'r':
            self.tape.moveRight()

        # Set the new state
        self.current_state = new_state


    def reset(self):

        self.current_state = self.init_state
        self.tape.reset()

    def linearize(self): # Used for testing purposes

        for old_state in range(self.nb_of_states):
            for symbol_read in range(self.nb_of_symbols):

                symbol_to_write = (symbol_read + 1) % self.nb_of_symbols
                movement = 'r'
                new_state = (old_state + 1) % self.nb_of_states

                action = ( symbol_to_write, movement, new_state )
                self.action_table[old_state][symbol_read] = action

        self.tape.linearize()

        return self

    def randomize(self):

        for old_state in range(self.nb_of_states):
            for symbol_read in range(self.nb_of_symbols):
                self.randomizeRow(old_state, symbol_read)

        return self

    def randomizeRow(self, old_state, symbol_read):

        action = self.createRandomAction()
        self.action_table[old_state][symbol_read] = action

        return action

    def createRandomAction(self):

        symbol_to_write = random.randint(0, self.nb_of_symbols - 1)
        movement = random.choice([ 'l', 'r' ])
        new_state = random.randint(0, self.nb_of_states - 1)
        action = ( symbol_to_write, movement, new_state )

        return action

    def mutate(self):
        old_state = random.randint(0, self.nb_of_states - 1)
        symbol_read = random.randint(0, self.nb_of_symbols - 1)
        old_action = self.action_table[old_state][symbol_read]
        new_action = self.randomizeRow(old_state, symbol_read)

        #print "Mutation: ", (old_state, symbol_read), "=>", old_action, " is now ", new_action
        return self

    def addState(self):

        self.nb_of_states += 1
        new_state = []
        for i in range(self.nb_of_symbols):
            action = self.createRandomAction()
            new_state.append(action)
        self.action_table.append(new_state)

        return self

    def removeState(self): # Remove the last one

        if self.nb_of_states == 1: # Do nothing
            return self

        state_to_remove = self.nb_of_states - 1
        del self.action_table[state_to_remove]
        self.nb_of_states -= 1

        if self.current_state == state_to_remove:
            self.current_state -= 1

        # Reindex the action table
        for old_state in range(self.nb_of_states):
            for symbol_read in range(self.nb_of_symbols):
                (symbol_to_write, movement, new_state) = self.action_table[old_state][symbol_read]
                if new_state == state_to_remove:
                    new_state -= 1
                self.action_table[old_state][symbol_read] = (symbol_to_write, movement, new_state)

        return self

    def mate1(self, turing_machine):

        if self.nb_of_states != self.nb_of_states:
            raise ValueError('Mate: different number of states')
        if self.nb_of_symbols != self.nb_of_symbols:
            raise ValueError('Mate: different number of symbols')

        cut_state = random.randint(0, self.nb_of_states - 1)
        print "Cut state: ", cut_state

        action_table_1 = self.action_table[:cut_state] + turing_machine.action_table[cut_state:]
        action_table_2 = turing_machine.action_table[:cut_state] + self.action_table[cut_state:]

        self.action_table = action_table_1
        turing_machine.action_table = action_table_2

        return self, turing_machine

    def mate(self, turing_machine):

        # Copy the largest action table of the two parents
        if len(self.action_table) > len(turing_machine.action_table):
            child = copy.deepcopy(self)
            parent_2 = turing_machine
        else:
            child = copy.deepcopy(turing_machine)
            parent_2 = self

        for old_state in range(parent_2.nb_of_states):
            for symbol_read in range(parent_2.nb_of_symbols):
                if random.random() > config.MATE_PB:
                    new_action = parent_2.action_table[old_state][symbol_read]
                    child.action_table[old_state][symbol_read] = new_action

        child.reset()
        return child

    def debugConfiguration(self):

        print "Init state: ", self.init_state
        print "Number of states: ", len(self.action_table)
        print "Number of symbols: ", len(self.action_table[0])
        print "Action table: "
        for old_state, action_state in enumerate(self.action_table):
            for symbol_read, action in enumerate(action_state):
                print (old_state, symbol_read), "=>", action
        #self.tape.debugConfiguration()


    def debugState(self):

        symbol_read = self.tape.read()
        action = self.action_table[self.current_state][symbol_read]

        print "Current action:", (self.current_state, symbol_read), "=>", action
        #self.tape.debugState()

def test_create():

    print "Create ------------------------"
    tm = TuringMachine(5, 3, 0)
    tm.debugConfiguration()
    tm.debugState()

    print "Randomize ------------------------"
    tm.randomize()
    tm.debugConfiguration()
    tm.debugState()

    print "Linearize ------------------------"
    tm.linearize()
    tm.debugConfiguration()
    tm.debugState()

    return

def test_execute():

    print "Create and linearize ------------------------"
    tm = TuringMachine(nb_of_states = 5, nb_of_symbols = 3, init_tape_length = 10)
    tm.linearize()
    tm.debugConfiguration()
    tm.debugState()

    for i in range(20):
        tm.next()
        tm.debugState()

    return

def test_mutate():

    print "Create"
    tm = TuringMachine(nb_of_states = 5, nb_of_symbols = 3, init_tape_length = 10)
    tm.linearize()
    tm.debugConfiguration()

    for i in range(1):

        print "Mutate"
        tm.mutate()
        tm.debugConfiguration()

        print "Remove state"
        tm.removeState()
        tm.debugConfiguration()

        print "Add state"
        tm.addState()
        tm.debugConfiguration()

    return

def test_mate():

    print "------------------------"
    print "Mate"
    tm1 = TuringMachine(nb_of_states = 4, nb_of_symbols = 2).randomize()
    tm2 = TuringMachine(nb_of_states = 6, nb_of_symbols = 2).randomize()
    tm1.debugConfiguration()
    tm2.debugConfiguration()
    child = tm1.mate(tm2)
    child.debugConfiguration()

    return


if __name__ == "__main__":

    #random.seed(time.time())
    random.seed(1234)

    #test_create()
    #test_execute()
    #test_mutate()
    test_mate()
