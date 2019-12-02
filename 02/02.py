#! /usr/bin/env python

from __future__ import print_function
import argparse

def intcodes_from_list(intcode_list):
    """generate a dict of index, intcode pairs from a list of intcodes"""
    return {pos: int(code) for pos, code in enumerate(intcode_list)}

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
    """run intcodes, which are stored as a dict of step: intcode pairs"""
    pc = 0
    last = len(intcodes) - 1

    while pc <= last:
        if intcodes[pc] == 1:
            # add
            if pc + 3 > last:
                raise Exception("out of opcodes")
            arg1 = intcodes[pc + 1]
            arg2 = intcodes[pc + 2]
            dest = intcodes[pc + 3]
            intcodes[dest] = intcodes[arg1] + intcodes[arg2]
            pc += 4
        elif intcodes[pc] == 2:
            # multiply
            if pc + 3 > last:
                raise Exception("out of opcodes")
            arg1 = intcodes[pc + 1]
            arg2 = intcodes[pc + 2]
            dest = intcodes[pc + 3]
            intcodes[dest] = intcodes[arg1] * intcodes[arg2]
            pc += 4
        elif intcodes[pc] == 99:
            # end program
            return intcodes
        else:
            # invalid
            raise Exception("invalid opcode: {}".format(intcodes[pc]))

    # should never reach this point (only if end is reached before program
    # stop instruction)
    raise Exception("ran out of intcodes before program stop reached")

def test():
    """run examples from the problem to make sure it works"""

    intcodes1 = intcodes_from_list([1, 0, 0, 0, 99])
    result1 = intcodes_from_list([2, 0, 0, 0, 99])
    intcodes2 = intcodes_from_list([2, 3, 0, 3, 99])
    result2 = intcodes_from_list([2, 3, 0, 6, 99])
    intcodes3 = intcodes_from_list([2, 4, 4, 5, 99, 0])
    result3 = intcodes_from_list([2, 4, 4, 5, 99, 9801])
    intcodes4 = intcodes_from_list([1, 1, 1, 4, 99, 5, 6, 0, 99])
    result4 = intcodes_from_list([30, 1, 1, 4, 2, 5, 6, 0, 99])

    if (result1 == run_program(intcodes1)
            and result2 == run_program(intcodes2)
            and result3 == run_program(intcodes3)
            and result4 == run_program(intcodes4)):
        print("tests passed")
    else:
        print("tests failed. Results:")
        print_intcodes(run_program(intcodes1))
        print_intcodes(run_program(intcodes2))
        print_intcodes(run_program(intcodes3))
        print_intcodes(run_program(intcodes4))

if __name__ == "__main__":
    test()
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="input file containing intcodes")
    args = parser.parse_args()

    intcodes = read_input(args.input)
    print("before running:")
    print_intcodes(intcodes)

    # set position 1 to 12, and position 2 with 2 (as stated in problem)
    intcodes[1] = 12
    intcodes[2] = 2

    result = run_program(intcodes)
    print("after running:")
    print(result)

