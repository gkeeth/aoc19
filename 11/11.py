#! /usr/bin/env python

from __future__ import print_function, division
from collections import defaultdict
from copy import copy

"""
1. input color of current tile (0 = black, 1 = white) (all tiles start black)
2. program outputs color to paint tile (0 = black, 1 = white)
3. program outputs direction to turn (0 = 90deg left, 1 = 90deg right)
4. move forward one panel after turning (starts facing up)
"""

next_direction = {
        "up": {0: "left", 1: "right"},
        "left": {0: "down", 1: "up"},
        "down": {0: "right", 1: "left"},
        "right": {0: "up", 1: "down"}
        }

direction_vector = {
        "up": (0, -1),
        "down": (0, 1),
        "left": (-1, 0),
        "right": (1, 0)
        }

class PaintingRobot(object):
    def __init__(self, raw_intcodes):
        self.computer = IntcodeComputer(raw_intcodes)
        self.location = (0, 0)
        self.direction = "up"
        self.painted_tiles = defaultdict(int) # default 0 (black)

    def count_painted_tiles(self):
        """return number of tiles painted at least once"""
        return len(self.painted_tiles)

    def step(self):
        # add appropriate inputs
        self.computer.add_to_input_queue([self.painted_tiles[self.location]])
        _, pc = self.computer.run_program()

        # read outputs
        outputs = self.computer.get_outputs()
        color = outputs[0]
        turn = outputs[1]

        # update internal state
        self.painted_tiles[self.location] = color
        self.direction = next_direction[self.direction][turn]
        self.location = (self.location[0] + direction_vector[self.direction][0],
                         self.location[1] + direction_vector[self.direction][1])

        # if pc is None, program halted and painting is complete
        return pc is not None

    def run(self, start_on_white=False):
        if start_on_white:
            self.painted_tiles[self.location] = 1
        while self.step():
            pass
        print("finished painting {} tiles".format(self.count_painted_tiles()))

    def display(self):
        # determine dimensions of painted area
        xmin = xmax = ymin = ymax = 0
        for x, y in self.painted_tiles:
            xmin = min(x, xmin)
            xmax = max(x, xmax)
            ymin = min(y, ymin)
            ymax = max(y, ymax)

        for y in range(ymin, ymax + 1):
            row = []
            for x in range(xmin, xmax + 1):
                if ((x, y) in self.painted_tiles
                        and self.painted_tiles[(x, y)] == 1): # white
                    row.append("o")
                else:
                    row.append(" ")
            print("".join(row))


class IntcodeComputer(object):
    def __init__(self, raw_intcode_list, initial_inputs=[]):
        self.pc = 0 # program counter
        self.rb = 0 # relative base
        self.input_queue = initial_inputs
        self.output_queue = []
        self.intcodes = self.intcodes_from_list(raw_intcode_list)

    def intcodes_from_list(self, intcode_list):
        """generate a dict of index, intcode pairs from a list of intcodes.

        Note: this format was chosen because I didn't know if any operations
        would result in values being stored at addresses outside of the
        predefined "program space" and a dict would handle this situation
        gracefully. In retrospect, this was not necessary and a list would have
        worked and been simpler.
        """
        intcodes = defaultdict(int) # return 0 by default
        for addr, code in enumerate(intcode_list):
            intcodes[addr] = int(code)
        return intcodes

    def print_intcodes(self):
        """print intcodes as a comma-separated list"""

        # does not handle sparse "programs"
        print(self.intcodes.values())

    def add_to_input_queue(self, inlist):
        self.input_queue += inlist

    def get_outputs(self):
        outlist = copy(self.output_queue)
        self.output_queue = []
        return outlist

    def run_program(self):
        """run intcodes, which are stored as a dict of step: intcode pairs

        intcodes encode the operation as well as the parameter mode. The two least
        significant digits are the operation. The most significant digit(s) are the
        parameter mode, one digit per parameter, read right-to-left (hundreds place
        is 1st parameter, thousands place is 2nd parameter, etc.)
        parameter mode 0: parameters is a position (an address)
        parameter mode 1: parameter is immediate (a literal value)
        """

        num_params = {
                1: 3,
                2: 3,
                3: 1,
                4: 1,
                5: 2,
                6: 2,
                7: 3,
                8: 3,
                9: 1,
                98: 0,
                99: 0
                }

        def decode_intcode(intcode):
            """decode intcode into its operation and the parameter modes.

            returns tuple of op and list of the parameter modes, in order (mode for
            first parameter is first element in list)
            """
            op = intcode % 100
            param_modes = intcode // 100
            param_mode_list = []
            for _ in range(num_params[op]):
                param_mode_list.append(param_modes % 10)
                param_modes //= 10
            return op, param_mode_list

        def check_remaining_opcodes():
            if self.pc + num_params[op] > last:
                raise Exception("out of opcodes")

        def get_parameters():
            parameters = []
            for n in range(num_params[op]):
                if param_modes[n] == 0:
                    # position mode
                    parameters.append(self.intcodes[self.pc + n + 1])
                elif param_modes[n] == 1:
                    # absolute (literal) mode
                    parameters.append(self.pc + n + 1)
                elif param_modes[n] == 2:
                    # relative mode
                    parameters.append(self.rb + self.intcodes[self.pc + n + 1])
                else:
                    raise Exception("invalid parameter mode: {}"
                            .format(param_modes[n]))
            return parameters

        last = len(self.intcodes) - 1

        while self.pc <= last:
            op, param_modes = decode_intcode(self.intcodes[self.pc])
            if op == 1:
                # add
                check_remaining_opcodes()
                args = get_parameters()
                self.intcodes[args[2]] = self.intcodes[args[0]] + self.intcodes[args[1]]
                self.pc += num_params[op] + 1
            elif op == 2:
                # multiply
                check_remaining_opcodes()
                args = get_parameters()
                self.intcodes[args[2]] = self.intcodes[args[0]] * self.intcodes[args[1]]
                self.pc += num_params[op] + 1
            elif op == 3:
                # store input at address of parameter
                check_remaining_opcodes()
                args = get_parameters()
                # if no input is available, return
                if len(self.input_queue) == 0:
                    return self.intcodes, self.pc
                self.intcodes[args[0]] = int(self.input_queue.pop(0))
                self.pc += num_params[op] + 1
            elif op == 4:
                # print value at address of parameter
                check_remaining_opcodes()
                args = get_parameters()
                self.output_queue.append(self.intcodes[args[0]])
                self.pc += num_params[op] + 1
            elif op == 5:
                # jump if true (jump address in 2nd parameter)
                check_remaining_opcodes()
                args = get_parameters()
                if self.intcodes[args[0]]:
                    self.pc = self.intcodes[args[1]]
                else:
                    self.pc += num_params[op] + 1
            elif op == 6:
                # jump if false (jump address in 2nd parameter)
                check_remaining_opcodes()
                args = get_parameters()
                if self.intcodes[args[0]]:
                    self.pc += num_params[op] + 1
                else:
                    self.pc = self.intcodes[args[1]]
            elif op == 7:
                # less than (arg1 < arg2 ? arg3 <- 1 : arg3 <- 0)
                check_remaining_opcodes()
                args = get_parameters()
                if self.intcodes[args[0]] < self.intcodes[args[1]]:
                    self.intcodes[args[2]] = 1
                else:
                    self.intcodes[args[2]] = 0
                self.pc += num_params[op] + 1
            elif op == 8:
                # equals (arg1 == arg2 ? arg3 <- 1 : arg3 <- 0)
                check_remaining_opcodes()
                args = get_parameters()
                if self.intcodes[args[0]] == self.intcodes[args[1]]:
                    self.intcodes[args[2]] = 1
                else:
                    self.intcodes[args[2]] = 0
                self.pc += num_params[op] + 1
            elif op == 9:
                # adjust rb by parameter
                check_remaining_opcodes()
                args = get_parameters()
                self.rb += self.intcodes[args[0]]
                self.pc += num_params[op] + 1
            elif op == 98:
                # print entire program
                check_remaining_opcodes()
                print("program counter: {}".format(self.pc))
                print("program:")
                print(self.intcodes)
                self.pc += num_params[op] + 1
            elif op == 99:
                # end program
                return self.intcodes, None
            else:
                # invalid
                raise Exception("invalid opcode: {}".format(self.intcodes[self.pc]))

        # should never reach this point (only if end is reached before program
        # stop instruction)
        raise Exception("ran out of intcodes before program stop reached")

def read_input(filename):
    """read input file and return list of raw intcodes."""

    with open(filename, "r") as infile:
        raw_intcodes = infile.readlines()[0].strip().split(",")

    return raw_intcodes

if __name__ == "__main__":
    robot = PaintingRobot(read_input("input.txt"))
    print("part 1")
    robot.run()
    print("part 2")
    robot = PaintingRobot(read_input("input.txt"))
    robot.run(start_on_white=True)
    robot.display()
