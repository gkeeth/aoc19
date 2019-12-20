#! /usr/bin/env python

from __future__ import division, print_function
from collections import defaultdict
from copy import copy, deepcopy
import random

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

def print_map(m, bot_location=None):
    # find extents of map
    xmin = 0
    xmax = 0
    ymin = 0
    ymax = 0
    for x, y in m:
        xmax = max(x, xmax)
        xmin = min(x, xmin)
        ymax = max(y, ymax)
        ymin = min(y, ymin)
    # plot map
    for y in range(ymin, ymax + 1):
        row = []
        for x in range(xmin, xmax + 1):
            if bot_location is not None and (x, y) == bot_location:
                row.append("D")
            elif (x, y) in m:
                row.append(m[(x, y)][0])
            else:
                row.append(" ")
        print("".join(row))


def next_location(current_location, direction):
    dir_step = {1: (0, -1),
                2: (0, 1),
                3: (1, 0),
                4: (-1, 0)
               }
    return (current_location[0] + dir_step[direction][0],
            current_location[1] + dir_step[direction][1])

def bfs(start_location=(0,0), goal=None):
    bot = IntcodeComputer(read_input("input.txt"))
    pos = tuple(start_location)
    # m maps (x, y) tuples to (content, intcode computer state, parent loc) tuples
    m = {pos: ("X", (bot.intcodes, bot.pc), None, 0)}
    q = [pos]
    while q:
        loc = q.pop()
        if goal is not None and m[loc][0] == goal:
            # found goal. tally steps backwards:
            print("found oxygen system at {}! (2)".format(loc))
            oxygen_location = loc
            steps = 0
            print_map(m, loc)
            while m[loc][2] is not None:
                loc = m[loc][2]
                # m[loc] = ("x", m[loc][1], m[loc][2])
                steps += 1
            print("reached oxygen system in {} steps".format(steps))
            # print_map(m, loc)
            return oxygen_location, steps, m
        for d in [1, 2, 3, 4]:
            # try each direction
            next_loc = next_location(loc, d)
            if next_loc not in m:
                # d goes in an unexplored direction; send the bot there
                # copying just the state that matters (pc and intcodes) because
                # deepcopying the entire computer is too expensive
                bot.intcodes = copy(m[loc][1][0])
                bot.pc = copy(m[loc][1][1])
                bot.add_to_input_queue([d])
                intcodes, pc = bot.run_program()
                result = bot.get_outputs().pop()
                if result == 0:
                    # wall
                    m[next_loc] = ("#", (intcodes, pc), loc, 0)
                elif result == 1:
                    # undiscovered, not oxygen
                    m[next_loc] = (".", (intcodes, pc), loc, 0)
                    q.append(next_loc)
                else:
                    # undiscovered, oxygen!
                    m[next_loc] = ("o", (intcodes, pc), loc, 0)
                    q.append(next_loc)

def flood(start_location, m):
    pos = tuple(start_location)
    q = [pos]
    while q:
        loc = q.pop()
        for d in [1, 2, 3, 4]:
            next_loc = next_location(loc, d)
            if next_loc not in m:
                m[next_loc] = ("0", None, loc, m[loc][3] + 1)
                q.append(next_loc)
            elif m[next_loc][0] not in ["O", "#"]:
                m[next_loc] = ("O", m[next_loc][1], m[next_loc][2], m[loc][3] + 1)
                q.append(next_loc)

    print_map(m)
    print("oxygen flooding complete in {} minutes".format(m[loc][3]))


if __name__ == "__main__":
    oxygen_location, steps, m = bfs(goal="o")
    # bfs(oxygen_location, goal=None)
    flood(oxygen_location, m)
