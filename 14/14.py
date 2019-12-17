#! /usr/bin/env python

from __future__ import division, print_function
from collections import defaultdict
from copy import copy
from math import ceil

class Reaction(object):
    def __init__(self, reaction_string):
        self.reactants = {}
        r = reaction_string.split("=>")
        reactants = r[0].strip().split(", ")
        product = r[1].strip().split(" ")
        for reactant in reactants:
            split = reactant.split(" ")
            self.reactants[split[1]] = int(split[0])
        self.product_name = product[1]
        self.product_quantity = int(product[0])

def parse_reaction_list(reaction_list):
    reactions = {}
    for r in reaction_list:
        rxn = Reaction(r)
        reactions[rxn.product_name] = rxn
    return reactions


def balanced(banked_chemicals):
    """return true if all non-ore chemicals have non-negative amounts."""
    def _enough(chemical):
        return chemical == "ORE" or banked_chemicals[chemical] >= 0
    return all(map(_enough, banked_chemicals))

def react(reactions, chemicals, product, repeat):
    """do reaction to make chemical.
    reactants are taken from chemicals. products are added to chemicals.
    """
    rxn = reactions[product]
    for reactant in rxn.reactants:
        chemicals[reactant] -= repeat * rxn.reactants[reactant]
    chemicals[product] += repeat * rxn.product_quantity

def calculate_ore(reactions, product_name, product_quantity):
    chemicals = {chemical: 0 for chemical in reactions}
    chemicals["ORE"] = 0
    chemicals[product_name] = -1 * product_quantity

    while not balanced(chemicals):
        # print(chemicals["FUEL"])
        for chemical in chemicals:
            if chemical != "ORE" and chemicals[chemical] < 0:
                # do reactions multiple times
                debt = -1 * chemicals[chemical]
                product_per_rxn = reactions[chemical].product_quantity
                repeats = int(ceil(debt / product_per_rxn))
                # print("debt: {}, product_per_rxn: {}, repeats: {}".format(debt, product_per_rxn, repeats))
                react(reactions, chemicals, chemical, repeats)
    return -1 * chemicals["ORE"]

def calculate_fuel_per_ore(rlist):
    reactions = parse_reaction_list(rlist)
    ore_goal = int(1e12)
    ore_used = 0
    low = 0
    high = 100000000000
    while low < high - 1:
        mid = (high + low) // 2
        ore_used = calculate_ore(reactions, "FUEL", mid)
        if ore_used > ore_goal:
            high = mid
        else:
            low = mid
    if ore_used > ore_goal:
        return mid - 1, calculate_ore(reactions, "FUEL", mid - 1)
    else:
        return mid, ore_used

def test():
    print("tests")
    # expected: 31 ORE
    rlist = ["10 ORE => 10 A",
             "1 ORE => 1 B",
             "7 A, 1 B => 1 C",
             "7 A, 1 C => 1 D",
             "7 A, 1 D => 1 E",
             "7 A, 1 E => 1 FUEL"
             ]
    reactions = parse_reaction_list(rlist)
    chemicals_needed = defaultdict(int)
    print(calculate_ore(reactions, "FUEL", 1))

    # expected: 165 ORE
    rlist = ["9 ORE => 2 A",
             "8 ORE => 3 B",
             "7 ORE => 5 C",
             "3 A, 4 B => 1 AB",
             "5 B, 7 C => 1 BC",
             "4 C, 1 A => 1 CA",
             "2 AB, 3 BC, 4 CA => 1 FUEL"
             ]
    reactions = parse_reaction_list(rlist)
    chemicals_needed = defaultdict(int)
    print(calculate_ore(reactions, "FUEL", 1))

    # expected: 13312 ORE
    rlist = ["157 ORE => 5 NZVS",
             "165 ORE => 6 DCFZ",
             "44 XJWVT, 5 KHKGT, 1 QDVJ, 29 NZVS, 9 GPVTF, 48 HKGWZ => 1 FUEL",
             "12 HKGWZ, 1 GPVTF, 8 PSHF => 9 QDVJ",
             "179 ORE => 7 PSHF",
             "177 ORE => 5 HKGWZ",
             "7 DCFZ, 7 PSHF => 2 XJWVT",
             "165 ORE => 2 GPVTF",
             "3 DCFZ, 7 NZVS, 5 HKGWZ, 10 PSHF => 8 KHKGT"
             ]
    reactions = parse_reaction_list(rlist)
    chemicals_needed = defaultdict(int)
    print(calculate_ore(reactions, "FUEL", 1))
    print("fuel generated: {}; ore used: {}".format(*calculate_fuel_per_ore(rlist)))

    # expected: 180697 ORE
    rlist = ["2 VPVL, 7 FWMGM, 2 CXFTF, 11 MNCFX => 1 STKFG",
             "17 NVRVD, 3 JNWZP => 8 VPVL",
             "53 STKFG, 6 MNCFX, 46 VJHF, 81 HVMC, 68 CXFTF, 25 GNMV => 1 FUEL",
             "22 VJHF, 37 MNCFX => 5 FWMGM",
             "139 ORE => 4 NVRVD",
             "144 ORE => 7 JNWZP",
             "5 MNCFX, 7 RFSQX, 2 FWMGM, 2 VPVL, 19 CXFTF => 3 HVMC",
             "5 VJHF, 7 MNCFX, 9 VPVL, 37 CXFTF => 6 GNMV",
             "145 ORE => 6 MNCFX",
             "1 NVRVD => 8 CXFTF",
             "1 VJHF, 6 MNCFX => 4 RFSQX",
             "176 ORE => 6 VJHF"
             ]
    reactions = parse_reaction_list(rlist)
    chemicals_needed = defaultdict(int)
    print(calculate_ore(reactions, "FUEL", 1))
    print("fuel generated: {}; ore used: {}".format(*calculate_fuel_per_ore(rlist)))

    # expected: 2210736 ORE
    rlist = ["171 ORE => 8 CNZTR",
             "7 ZLQW, 3 BMBT, 9 XCVML, 26 XMNCP, 1 WPTQ, 2 MZWV, 1 RJRHP => 4 PLWSL",
             "114 ORE => 4 BHXH",
             "14 VRPVC => 6 BMBT",
             "6 BHXH, 18 KTJDG, 12 WPTQ, 7 PLWSL, 31 FHTLT, 37 ZDVW => 1 FUEL",
             "6 WPTQ, 2 BMBT, 8 ZLQW, 18 KTJDG, 1 XMNCP, 6 MZWV, 1 RJRHP => 6 FHTLT",
             "15 XDBXC, 2 LTCX, 1 VRPVC => 6 ZLQW",
             "13 WPTQ, 10 LTCX, 3 RJRHP, 14 XMNCP, 2 MZWV, 1 ZLQW => 1 ZDVW",
             "5 BMBT => 4 WPTQ",
             "189 ORE => 9 KTJDG",
             "1 MZWV, 17 XDBXC, 3 XCVML => 2 XMNCP",
             "12 VRPVC, 27 CNZTR => 2 XDBXC",
             "15 KTJDG, 12 BHXH => 5 XCVML",
             "3 BHXH, 2 VRPVC => 7 MZWV",
             "121 ORE => 7 VRPVC",
             "7 XCVML => 6 RJRHP",
             "5 BHXH, 4 VRPVC => 5 LTCX"
             ]
    reactions = parse_reaction_list(rlist)
    chemicals_needed = defaultdict(int)
    print(calculate_ore(reactions, "FUEL", 1))
    print("fuel generated: {}; ore used: {}".format(*calculate_fuel_per_ore(rlist)))

if __name__ == "__main__":
    test()
    # part 1
    print("\npart 1")
    with open("input.txt", "r") as infile:
        rlist = infile.read().splitlines()

    reactions = parse_reaction_list(rlist)
    chemicals_needed = defaultdict(int)
    print(calculate_ore(reactions, "FUEL", 1))

    # part 2
    print("\npart 2")
    print("fuel generated: {}; ore used: {}".format(*calculate_fuel_per_ore(rlist)))

