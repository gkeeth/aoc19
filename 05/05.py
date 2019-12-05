#! /usr/bin/env python

from __future__ import print_function
import argparse

def intcodes_from_list(intcode_list):
    """generate a dict of index, intcode pairs from a list of intcodes.

    Note: this format was chosen because I didn't know if any operations would
    result in values being stored at addresses outside of the predefined
    "program space" and a dict would handle this situation gracefully. In
    retrospect, this was not necessary and a list would have worked and been
    simpler.
    """
    return {addr: int(code) for addr, code in enumerate(intcode_list)}

def read_input(filename):
    """read input file and split into dict of intcodes.

    Output dict is indexed by the codes' integer positions."""

    with open(args.input, "r") as infile:
        raw_intcodes = infile.readlines()[0].strip().split(",")
        intcodes = intcodes_from_list(raw_intcodes)

    return intcodes

def print_intcodes(intcodes):
    """print intcodes as a comma-separated list"""

    # does not handle sparse "programs"
    print(intcodes.values())

# def set_inputs(intcodes, noun, verb):
#     """update program with inputs.

#     sets address 1 of the program to "noun"
#     sets address 2 of the program to "verb"

#     returns the modified program
#     """
#     intcodes[1] = noun
#     intcodes[2] = verb
#     return intcodes

def run_program(intcodes):
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
            99: 0
            }

    def decode_intcode(intcode):
        """decode intcode into its operation and the parameter modes.

        returns tuple of op and list of the parameter modes, in order (mode for
        first parameter is first element in list)
        """
        op = intcode % 100
        param_modes = intcode / 100
        param_mode_list = []
        for _ in range(num_params[op]):
            param_mode_list.append(param_modes % 10)
            param_modes /= 10
        return op, param_mode_list

    def check_remaining_opcodes(last_opcode_addr, pc, number_of_params):
        if pc + number_of_params > last_opcode_addr:
            raise Exception("out of opcodes")

    def get_parameters():
        parameters = []
        for n in range(num_params[op]):
            if param_modes[n]:
                parameters.append(pc + n + 1)
            else:
                parameters.append(intcodes[pc + n + 1])
        return parameters

    pc = 0
    last = len(intcodes) - 1

    while pc <= last:
        op, param_modes = decode_intcode(intcodes[pc])
        if op == 1:
            # add
            check_remaining_opcodes(last, pc, num_params[op])
            args = get_parameters()
            intcodes[args[2]] = intcodes[args[0]] + intcodes[args[1]]
            pc += num_params[op] + 1
        elif op == 2:
            # multiply
            check_remaining_opcodes(last, pc, num_params[op])
            args = get_parameters()
            intcodes[args[2]] = intcodes[args[0]] * intcodes[args[1]]
            pc += num_params[op] + 1
        elif op == 3:
            # store input at address of parameter
            check_remaining_opcodes(last, pc, num_params[op])
            args = get_parameters()
            intcodes[args[0]] = int(raw_input("input a number: ")) # ew python2
            pc += num_params[op] + 1
        elif op == 4:
            # print value at address of parameter
            check_remaining_opcodes(last, pc, num_params[op])
            args = get_parameters()
            print(intcodes[args[0]])
            pc += num_params[op] + 1
        elif op == 99:
            # end program
            return intcodes
        else:
            # invalid
            raise Exception("invalid opcode: {}".format(intcodes[pc]))

    # should never reach this point (only if end is reached before program
    # stop instruction)
    raise Exception("ran out of intcodes before program stop reached")

def test():
    print("this test program should output the same number that is input")
    intcodes1 = intcodes_from_list([3, 0, 4, 0, 99])
    run_program(intcodes1)

    intcodes2 = intcodes_from_list([1002, 4, 3, 4, 33])
    result2 = intcodes_from_list([1002, 4, 3, 4, 99])
    if result2 == run_program(intcodes2):
        print("test2 passed")
    else:
        print("test2 failed. results:")
        print_intcodes(run_program(intcodes2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="input file containing intcodes")
    args = parser.parse_args()

    intcodes = read_input(args.input)
    run_program(intcodes)
