#! /usr/bin/env python

from __future__ import print_function
from collections import OrderedDict
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
        self.bodies = {"COM": Body("COM", None)}
        for line in textmap:
            s = line.strip().split(")")
            name = s[1]
            parent_name = s[0]
            self.bodies[name] = Body(name, parent_name)

    def _calculate_orbits(self, body_name, root_name="COM"):
        """count number of orbits of a body back to a root body"""
        body = self.bodies[body_name]
        if body.name == root_name:
            return 0
        else:
            return 1 + self._calculate_orbits(body.parent)

    def calculate_all_orbits(self):
        """calculate the number of direct and indirect orbits in the map."""

        orbits = 0
        for b in self.bodies:
            orbits += self._calculate_orbits(b)
        return orbits

    def _build_orbit_chain(self, body_name):
        """build a chain of bodies, from body_name back to COM.

        the chain is indexed by the body name, with the value being the number
        of transfers required to get there."""

        chain = OrderedDict()
        transfers = 0
        current = self.bodies[body_name]
        while current.parent != "COM":
            chain[current.parent] = transfers
            current = self.bodies[current.parent]
            transfers += 1
        chain["COM"] = transfers
        return chain

    def calculate_transfers_to_santa(self):
        """count number of transfers needed to orbit the same body as santa.

        The transfers needed to get from YOU to SAN is the sum of the transfers
        to get from each to the outermost common body.
        """
        you = self._build_orbit_chain("YOU")
        san = self._build_orbit_chain("SAN")
        # search for first (outermost) body in common
        for b in you:
            if b in san:
                return you[b] + san[b]

def test():
    # test1: orbit parsing and counting
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
    if OrbitalMap(input1).calculate_all_orbits() != 42:
        raise Exception("test1 failed")

    # test2: transfer orbits to santa
    input2 = ["COM)B",
            "B)C",
            "C)D",
            "D)E",
            "E)F",
            "B)G",
            "G)H",
            "D)I",
            "E)J",
            "J)K",
            "K)L",
            "K)YOU",
            "I)SAN"
            ]
    if OrbitalMap(input2).calculate_transfers_to_santa() != 4:
            raise Exception("test2 failed")


if __name__ == "__main__":
    test()
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="input orbital map file")
    args = parser.parse_args()
    with open(args.input, "r") as infile:
        o = OrbitalMap(infile.readlines())
        print("orbits in input file: {}".format(o.calculate_all_orbits()))
        print("transfers to get to santa: {}".format(o.calculate_transfers_to_santa()))
