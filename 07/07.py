#! /usr/bin/env python
from __future__ import print_function
import argparse
from itertools import permutations
from copy import copy

def read_input(filename):
    """read input file and return list of raw intcodes."""

    with open(args.input, "r") as infile:
        raw_intcodes = infile.readlines()[0].strip().split(",")

    return raw_intcodes

class IntcodeComputer(object):
    def __init__(self, raw_intcode_list, initial_inputs=[]):
        self.pc = 0
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
        return {addr: int(code) for addr, code in enumerate(intcode_list)}

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
                if param_modes[n]:
                    parameters.append(self.pc + n + 1)
                else:
                    parameters.append(self.intcodes[self.pc + n + 1])
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
                # equals (arg1 == arg2 ? arg3 <- 1 : arg3 <- 1)
                check_remaining_opcodes()
                args = get_parameters()
                if self.intcodes[args[0]] == self.intcodes[args[1]]:
                    self.intcodes[args[2]] = 1
                else:
                    self.intcodes[args[2]] = 0
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

def generate_phase_combinations(feedback=False):
    if feedback:
        options = [5, 6, 7, 8, 9]
    else:
        options = [0, 1, 2, 3, 4]
    return permutations(options)

def find_optimal_phase_sequence(program, feedback=False):
    best_seq = None
    best_thrust = 0
    for seq in generate_phase_combinations(feedback):
        result = 0
        previous_outputs = []
        running_amps = []
        previous_outputs = [0]
        for phase_setting in seq:
            # set up initial states for each amplifier
            inputs = [phase_setting]
            running_amps.append(IntcodeComputer(copy(program), inputs))

        while running_amps:
            # run amps. When they stall waiting for input, store state and go
            # on to next amplifier
            amp = running_amps.pop(0)
            amp.add_to_input_queue(previous_outputs)

            intcodes, pc = amp.run_program()
            previous_outputs = amp.get_outputs()
            # if pc is none, amplifier has finished loop and halted.
            # if pc isn't none, amplifier has stalled waiting for input and
            # needs to resume when input is available.
            if pc is not None:
                running_amps.append(amp)

        result = previous_outputs.pop()
        if result > best_thrust:
            best_thrust = result
            best_seq = seq
    return best_thrust, best_seq

def test():
    prog = [3,15,3,16,1002,16,10,16,1,16,15,15,4,15,99,0,0]
    goal_thrust = 43210
    goal_seq = (4,3,2,1,0)
    thrust, seq = find_optimal_phase_sequence(prog)
    if thrust != goal_thrust or seq != goal_seq:
        print("test1 failed. goal thrust: {}, calculated thrust: {}, goal sequence: {}, calculated sequence: {}".format(goal_thrust, thrust, goal_seq, seq))
    else:
        print("test1 passed")
    prog = [3,23,3,24,1002,24,10,24,1002,23,-1,23,101,5,23,23,1,24,23,23,4,23,99,0,0]
    goal_thrust = 54321
    goal_seq = (0,1,2,3,4)
    thrust, seq = find_optimal_phase_sequence(prog)
    if thrust != goal_thrust or seq != goal_seq:
        print("test2 failed. goal thrust: {}, calculated thrust: {}, goal sequence: {}, calculated sequence: {}".format(goal_thrust, thrust, goal_seq, seq))
    else:
        print("test2 passed")
    prog = [3,31,3,32,1002,32,10,32,1001,31,-2,31,1007,31,0,33,1002,33,7,33,1,33,31,31,1,32,31,31,4,31,99,0,0,0]
    goal_thrust = 65210
    goal_seq = (1,0,4,3,2)
    thrust, seq = find_optimal_phase_sequence(prog)
    if thrust != goal_thrust or seq != goal_seq:
        print("test3 failed. goal thrust: {}, calculated thrust: {}, goal sequence: {}, calculated sequence: {}".format(goal_thrust, thrust, goal_seq, seq))
    else:
        print("test3 passed")

    # part 2
    prog = [3,26,1001,26,-4,26,3,27,1002,27,2,27,1,27,26,27,4,27,1001,28,-1,28,1005,28,6,99,0,0,5]
    goal_thrust = 139629729
    goal_seq = (9,8,7,6,5)
    thrust, seq = find_optimal_phase_sequence(prog, feedback=True)
    if thrust != goal_thrust or seq != goal_seq:
        print("test4 failed. goal thrust: {}, calculated thrust: {}, goal sequence: {}, calculated sequence: {}".format(goal_thrust, thrust, goal_seq, seq))
    else:
        print("test4 passed")
    prog = [3,52,1001,52,-5,52,3,53,1,52,56,54,1007,54,5,55,1005,55,26,1001,54,
            -5,54,1105,1,12,1,53,54,53,1008,54,0,55,1001,55,1,55,2,53,55,53,4,
            53,1001,56,-1,56,1005,56,6,99,0,0,0,0,10]
    goal_thrust = 18216
    goal_seq = (9,7,8,5,6)
    thrust, seq = find_optimal_phase_sequence(prog, feedback=True)
    if thrust != goal_thrust or seq != goal_seq:
        print("test5 failed. goal thrust: {}, calculated thrust: {}, goal sequence: {}, calculated sequence: {}".format(goal_thrust, thrust, goal_seq, seq))
    else:
        print("test5 passed")

if __name__ == "__main__":
    test()
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="input file containing intcodes")
    args = parser.parse_args()

    intcodes = read_input(args.input)
    print("PART 1")
    thrust, seq = find_optimal_phase_sequence(intcodes)
    print("thrust: {}".format(thrust))
    print("phase sequence: {}".format(seq))

    print("PART 2")
    thrust, seq = find_optimal_phase_sequence(intcodes, feedback=True)
    print("thrust: {}".format(thrust))
    print("phase sequence: {}".format(seq))

