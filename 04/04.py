#! /usr/bin/env python

from __future__ import print_function
import argparse

# 6 digit number
# input range: 402328 - 864247
# two adjacent digits are the same
# left to right, digits never decrease
# how many such passwords exist?

def check_range(num):
    if num < 402328:
        raise Exception("invalid number: too low")
    elif num > 864247:
        # too big
        return False
    else:
        # in the proper range
        return True

def check_adjacent_digits(num):
    s = str(num)
    # brute forcing the check is easy for 6 digits...
    if (s[0] == s[1] != s[2]
            or s[0] != s[1] == s[2] != s[3]
            or s[1] != s[2] == s[3] != s[4]
            or s[2] != s[3] == s[4] != s[5]
            or s[3] != s[4] == s[5]):
        return True
    else:
        return False

def check_valid(num):
    # doesn't check that digits monotonically increase (handled by loop)
    return check_range(num) and check_adjacent_digits(num)

def main():
    valid_nums = []
    for d1 in range(4, 10):
        for d2 in range(d1, 10):
            for d3 in range(d2, 10):
                for d4 in range(d3, 10):
                    for d5 in range(d4, 10):
                        for d6 in range(d5, 10):
                            # check and add to list if it works
                            num = int(d6 + 1e1*d5 + 1e2*d4 + 1e3*d3 + 1e4*d2 + 1e5*d1)
                            if check_valid(num):
                                valid_nums.append(num)
    print(len(valid_nums))

if __name__ == "__main__":
    main()
