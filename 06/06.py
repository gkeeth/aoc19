#! /usr/bin/env python

from __future__ import print_function
import argparse


class Body(object):
    """class representing an orbital body.

    Orbital bodies can orbit other orbital bodies as satellites.
    Each Body can only orbit one Body, but can be orbited by an unlimited
    number of Bodies.
    """

    def __init__(self, name, parent_name):
        self.name = name
        self.parent = parent_name


class OrbitalMap(object):
    """class representing a map of orbital bodies."""

    def __init__(self, textmap):
        self.bodies = {}
        for line in textmap:
            s = line.strip().split(")")
            name = s[1]
            parent_name = s[0]
            self.bodies[name] = Body(name, parent_name)

    def calculate_orbits(self):
        """calculate the number of direct and indirect orbits in the map."""
        def _calculate_orbits(body_name):
            body = self.bodies[body_name]
            if body.parent == "COM":
                return 1
            else:
                return 1 + _calculate_orbits(body.parent)

        orbits = 0
        for b in self.bodies:
            orbits += _calculate_orbits(b)
        print("total orbits: {}".format(orbits))

def test():
    input1 = ["COM)B\n",
            "B)C\n",
            "C)D\n",
            "D)E\n",
            "E)F\n",
            "B)G\n",
            "G)H\n",
            "D)I\n",
            "E)J\n",
            "J)K\n",
            "K)L\n"
            ]
    OrbitalMap(input1).calculate_orbits()


if __name__ == "__main__":
    # test()
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="input orbital map file")
    args = parser.parse_args()
    with open(args.input, "r") as infile:
        o = OrbitalMap(infile.readlines())
        o.calculate_orbits()
