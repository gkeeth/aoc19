#! /usr/bin/env python

from __future__ import print_function, division
from itertools import combinations
from math import copysign
import re

class Moon(object):
    def __init__(self, position):
        self.position = list(position)
        self.velocity = [0, 0, 0]

    def print_state(self):
        s = ("pos=<x={}, y={}, z={}> vel=<x={}, y={}, z={}>, pot = {}, kin = {}, tot = {}"
                .format(self.position[0], self.position[1], self.position[2],
                        self.velocity[0], self.velocity[1], self.velocity[2],
                        self.calculate_potential_energy(),
                        self.calculate_kinetic_energy(),
                        self.calculate_total_energy()))
        print(s)

    def _calculate_energy(self, prop):
        return abs(prop[0]) + abs(prop[1]) + abs(prop[2])
    def calculate_potential_energy(self):
        return self._calculate_energy(self.position)
    def calculate_kinetic_energy(self):
        return self._calculate_energy(self.velocity)
    def calculate_total_energy(self):
        return self.calculate_potential_energy() * self.calculate_kinetic_energy()

def parse_input_into_moons(input_lines):
    moons = []
    prog = re.compile(r"\<x=(-*\d+), y=(-*\d+), z=(-*\d+)\>")
    for line in input_lines.splitlines():
        result = prog.match(line)
        moons.append(Moon([int(result.group(n)) for n in range(1, 4)]))
    return moons

def apply_gravity(moonlist):
    pairs = combinations(moonlist, 2)
    for pair in pairs:
        for n in range(3):
            # if a > b, va decreases while vb increases, and vice versa.
            d = pair[1].position[n] - pair[0].position[n]
            if d < 0:
                change = -1
            elif d > 0:
                change = 1
            else:
                change = 0
            pair[0].velocity[n] += change
            pair[1].velocity[n] -= change

def apply_velocity(moonlist):
    for moon in moonlist:
        for n in range(3):
            moon.position[n] += moon.velocity[n]

def timestep(moonlist):
    apply_gravity(moonlist)
    apply_velocity(moonlist)

def total_energy(moonlist):
    energy = 0
    for m in moonlist:
        m.print_state()
        energy += m.calculate_total_energy()
    return energy

def get_current_state(moonlist):
    positions = []
    velocities = []
    for moon in moonlist:
        positions.append(tuple(moon.position))
        velocities.append(tuple(moon.velocity))
    return (tuple(positions), tuple(velocities))

def save_state(moonlist, states, step):
    state = get_current_state(moonlist)
    if state in states:
        print("repeating state found; timesteps {} and {}".format(states[state], step))
        return True
    else:
        states[state] = step
        return False

def find_repeated_state(moonlist):
    print("searching for repeating states...")
    step = 0
    states = {}
    while not save_state(moonlist, states, step):
        timestep(moonlist)
        step += 1

def test():
    intext = "<x=-1, y=0, z=2>\n\
<x=2, y=-10, z=-7>\n\
<x=4, y=-8, z=8>\n\
<x=3, y=5, z=-1>"
    moonlist = parse_input_into_moons(intext)
    for n in range(10):
        print("\nat timestep {}".format(n))
        for m in moonlist:
            m.print_state()
        timestep(moonlist)

    print("\nafter timestep 10")
    energy = total_energy(moonlist)
    print(energy)

    find_repeated_state(parse_input_into_moons(intext))

if __name__ == "__main__":
    test()
    with open("input.txt", "r") as infile:
        inlines = infile.read()
    # part 1
    moons = parse_input_into_moons(inlines)
    for n in range(1000):
        timestep(moons)
    print("total energy: {}".format(total_energy(moons)))

    # part 2
    moons = parse_input_into_moons(inlines)
    find_repeated_state(moons)



