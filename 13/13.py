#! /usr/bin/env python

from __future__ import print_function, division
from collections import defaultdict
from copy import copy
import sys


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

class ArcadeCabinet(object):
    def __init__(self, game_program, patch_quarters=False):
        self.computer = IntcodeComputer(game_program)
        self.sb = defaultdict(int)
        if patch_quarters:
            # cheat the elves out of their quarter
            print("initial quarter value: {}".format(self.computer.intcodes[0]))
            self.computer.intcodes[0] = 2

    def run_game(self):
        print("starting new game. move paddle with j, k, l keys.")

        # joystick values: 0 = neutral, -1 = left, 1 = right
        while True:
            # keep paddle directly under ball
            # get ball location and paddle location
            paddle_col = 0
            ball_col = 0
            for key, value in self.sb.items():
                if value == 3:
                    paddle_col = key[0]
                elif value == 4:
                    ball_col = key[0]

            if ball_col == paddle_col:
                inval = 0
            elif ball_col > paddle_col:
                inval = 1
            else:
                inval = -1
            self.computer.add_to_input_queue([inval])

            intcodes, pc = self.computer.run_program()
            self.build_screenbuffer()
            self.draw_screen()
            if pc == None:
                # game is over
                self.get_score()
                break

    def build_screenbuffer(self):
        output = self.computer.get_outputs()
        score = self.sb[(-1, 0)]
        self.sb[(-1, 0)] = score
        for n in range(len(output) // 3):
            x = int(output[3*n])
            y = int(output[3*n + 1])
            tile = int(output[3*n + 2])
            self.sb[(x, y)] = tile

    def draw_screen(self):
        lookup = {
                0: " ",
                1: "X",
                2: "#",
                3: "_",
                4: "o"
                }
        w = 36
        h = 22
        for y in range(h):
            row = []
            for x in range(h):
                row.append(lookup[self.sb[(x, y)]])
            print("".join(row))

    def get_score(self):
        print("score: {}".format(self.sb[(-1, 0)]))
        return self.sb[(-1, 0)]

    def count_tile_types(self):
        print("blanks: {}".format(self.sb.values().count(0)))
        print("walls: {}".format(self.sb.values().count(1)))
        print("blocks: {}".format(self.sb.values().count(2)))
        print("horiz paddles: {}".format(self.sb.values().count(3)))
        print("balls: {}".format(self.sb.values().count(4)))
        self.get_score()

def test():
    out = ["1", "2", "3", "6", "5", "4"]
    print("test")
    game = ArcadeCabinet([])
    game.build_screenbuffer()
    game.count_tile_types()

if __name__ == "__main__":
    test()

    print("\npart 1")
    game = ArcadeCabinet(read_input("input.txt"))
    outs = game.run_game()

    print("\npart 2")
    game = ArcadeCabinet(read_input("input.txt"), patch_quarters=True)
    outs = game.run_game()
