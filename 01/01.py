#! /usr/bin/env python

from __future__ import print_function
import argparse

def get_module_masses(massfile):
    """Parse input file to get masses of each module.

    Input file has the mass of each module on its own line.

    Return list of module masses.
    """

    module_masses = []
    with open(massfile, "r") as infile:
        module_masses = [int(line) for line in infile]

    return module_masses

def calculate_module_fuel(module_mass):
    """calculate fuel required for module, based on module's mass.

    Also calculates the additional fuel required for the fuel itself."""

    def fuel_by_mass(mass):
        return (mass // 3) - 2 # // is floor division

    # calculate fuel required by the module itself
    module_fuel = fuel_by_mass(module_mass)

    # calculate additional fuel required to launch the fuel
    total_fuel = module_fuel
    additional_fuel = fuel_by_mass(module_fuel)
    while additional_fuel > 0:
        total_fuel += additional_fuel
        additional_fuel = fuel_by_mass(additional_fuel)

    return total_fuel

def calculate_total_fuel(module_fuels):
    """sum up module fuels."""

    total_fuel = sum(module_fuels)
    return total_fuel

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="input file containing module masses")
    args = parser.parse_args()

    module_masses = get_module_masses(args.input)
    module_fuels = [calculate_module_fuel(mass) for mass in module_masses]
    total_fuel = calculate_total_fuel(module_fuels)

    print(total_fuel)
