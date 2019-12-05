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
            5: 2,
            6: 2,
            7: 3,
            8: 3,
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

    def check_remaining_opcodes():
        if pc + num_params[op] > last:
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
            check_remaining_opcodes()
            args = get_parameters()
            intcodes[args[2]] = intcodes[args[0]] + intcodes[args[1]]
            pc += num_params[op] + 1
        elif op == 2:
            # multiply
            check_remaining_opcodes()
            args = get_parameters()
            intcodes[args[2]] = intcodes[args[0]] * intcodes[args[1]]
            pc += num_params[op] + 1
        elif op == 3:
            # store input at address of parameter
            check_remaining_opcodes()
            args = get_parameters()
            intcodes[args[0]] = int(raw_input("input a number: ")) # ew python2
            pc += num_params[op] + 1
        elif op == 4:
            # print value at address of parameter
            check_remaining_opcodes()
            args = get_parameters()
            print(intcodes[args[0]])
            pc += num_params[op] + 1
        elif op == 5:
            # jump if true (jump address in 2nd parameter)
            check_remaining_opcodes()
            args = get_parameters()
            if intcodes[args[0]]:
                pc = intcodes[args[1]]
            else:
                pc += num_params[op] + 1
        elif op == 6:
            # jump if false (jump address in 2nd parameter)
            check_remaining_opcodes()
            args = get_parameters()
            if intcodes[args[0]]:
                pc += num_params[op] + 1
            else:
                pc = intcodes[args[1]]
        elif op == 7:
            # less than (arg1 < arg2 ? arg3 <- 1 : arg3 <- 0)
            check_remaining_opcodes()
            args = get_parameters()
            if intcodes[args[0]] < intcodes[args[1]]:
                intcodes[args[2]] = 1
            else:
                intcodes[args[2]] = 0
            pc += num_params[op] + 1
        elif op == 8:
            # equals (arg1 == arg2 ? arg3 <- 1 : arg3 <- 1
            check_remaining_opcodes()
            args = get_parameters()
            if intcodes[args[0]] == intcodes[args[1]]:
                intcodes[args[2]] = 1
            else:
                intcodes[args[2]] = 0
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
    print("test1: output the same number that is input")
    intcodes1 = intcodes_from_list([3, 0, 4, 0, 99])
    run_program(intcodes1)

    intcodes2 = intcodes_from_list([1002, 4, 3, 4, 33])
    result2 = intcodes_from_list([1002, 4, 3, 4, 99])
    if result2 == run_program(intcodes2):
        print("test2 passed")
    else:
        print("test2 failed. results:")
        print_intcodes(run_program(intcodes2))
    # input == 8 ? 1 : 0
    print("test3: output 1 if the input equals 8, and zero otherwise")
    intcodes3 = intcodes_from_list([3,9,8,9,10,9,4,9,99,-1,8])
    run_program(intcodes3)
    # input < 8 ? 1 : 0
    print("test4: output 1 if the input is less than 8, and zero otherwise")
    intcodes4 = intcodes_from_list([3,9,7,9,10,9,4,9,99,-1,8])
    run_program(intcodes4)
    # input == 8 ? 1 : 0
    print("test5: output 1 if the input equals 8, and zero otherwise")
    intcodes5 = intcodes_from_list([3,3,1108,-1,8,3,4,3,99])
    run_program(intcodes5) # TODO: fails
    # input < 8 ? 1 : 0
    print("test6: output 1 if the input is less than 8, and zero otherwise")
    intcodes6 = intcodes_from_list([3,3,1107,-1,8,3,4,3,99])
    run_program(intcodes6)

    print("test7: output 0 if input is 0, or 1 if input is non-zero")
    intcodes7 = intcodes_from_list([3,12,6,12,15,1,13,14,13,4,13,99,-1,0,1,9])
    run_program(intcodes7)

    print("test8: output 0 if input is 0, or 1 if input is non-zero")
    intcodes8 = intcodes_from_list([3,3,1105,-1,9,1101,0,0,12,4,12,99,1])
    run_program(intcodes8)

    print("test9: output 999 if input is below 8, 1000 if input equals 8, or 1001 if input is above 8")
    intcodes9 = intcodes_from_list([3,21,1008,21,8,20,1005,20,22,107,8,21,20,
        1006,20,31,1106,0,36,98,0,0,1002,21,125,20,4,20,1105,1,46,104,999,1105,
        1,46,1101,1000,1,20,4,20,1105,1,46,98,99])
    run_program(intcodes9)

if __name__ == "__main__":
    # test()
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="input file containing intcodes")
    args = parser.parse_args()

    intcodes = read_input(args.input)
    run_program(intcodes)
