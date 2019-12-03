#! /usr/bin/env python

from __future__ import division
import argparse

class Path(object):
    def _parse_path(self, pathlist):
        """parse a list of manhattan directions into a list of points.

        each coordinate that the path goes through are added to the list.
        """

        loc = [0, 0]
        self.points = []

        for step in pathlist:
            # get magnitude
            if step[1:].isdigit():
                magnitude = int(step[1:])
            else:
                raise Exception("malformed step (invalid distance): '{}'"
                        .format(step))
            # get direction
            direction = step[0].upper()
            if direction == "L":
                vector = (-1, 0)
            elif direction == "R":
                vector = (1, 0)
            elif direction == "U":
                vector = (0, 1)
            elif direction == "D":
                vector = (0, -1)
            else:
                raise Exception("malformed step (invalid direction): '{}'"
                        .format(step))

            for _ in range(magnitude):
                loc[0] += vector[0]
                loc[1] += vector[1]
                self.points.append(tuple(loc))


    def find_intersections(self, other_path):
        """find intersections between self and another Path object.

        finds intersections (common points) between self.points and
        other_path.points.

        Returns a list of intersections.
        """
        set_a = set(self.points)
        set_b = set(other_path.points)
        return list(set_a.intersection(set_b))

    def find_closest_intersection_distance(self, other_path):

        def mandist(coord):
            return abs(coord[0]) + abs(coord[1])

        intersections = self.find_intersections(other_path)
        distances = map(mandist, intersections)
        return min(distances)

    def find_shortest_intersection_distance(self, other_path):

        def sigdist(p):
            return self.points.index(p) + other_path.points.index(p) + 2

        intersections = self.find_intersections(other_path)
        distances = map(sigdist, intersections)
        return min(distances)

    def __init__(self, pathlist):
        self._parse_path(pathlist)


def parse_input(filename):
    with open(filename, "r") as infile:
        raw_wires = infile.readlines()
        path1 = Path(raw_wires[0].strip().split(","))
        path2 = Path(raw_wires[1].strip().split(","))

    return path1, path2

def test():
    # check path parsing
    path1a = Path(["R8", "U5", "L5", "D3"])
    path1b = Path(["U7", "R6", "D4", "L4"])
    if path1a.points[-1] != (3, 2):
        print(path1a.points)
        raise Exception("path1a not parsed correctly")
    if path1b.points[-1] != (2, 3):
        print(path1b.points)
        raise Exception("path1b not parsed correctly")

    # check intersection detection and distance/shortest path calculations
    path2a = Path(["R75", "D30", "R83", "U83", "L12", "D49", "R71", "U7",
        "L72"])
    path2b = Path(["U62", "R66", "U55", "R34", "D71", "R55", "D58", "R83"])
    path3a = Path(["R98", "U47", "R26", "D63", "R33", "U87", "L62", "D20",
        "R33", "U53", "R51"])
    path3b = Path(["U98", "R91", "D20", "R16", "D67", "R40", "U7", "R15",
        "U6","R7"])
    if path1a.find_closest_intersection_distance(path1b) != 6:
        print("path1 intersections wrong. incorrect result: {}"
                .format(path1a.find_closest_intersection_distance(path1b)))
    if path1a.find_shortest_intersection_distance(path1b) != 30:
        print("path1 shortest intersection wrong. incorrect result: {}"
                .format(path1a.find_shortest_intersection_distance(path1b)))
    if path2a.find_closest_intersection_distance(path2b) != 159:
        print("path2 intersections wrong. incorrect result: {}"
                .format(path2a.find_closest_intersection_distance(path2b)))
    if path2a.find_shortest_intersection_distance(path2b) != 610:
        print("path2 shortest intersection wrong. incorrect result: {}"
                .format(path2b.find_shortest_intersection_distance(path2b)))
    if path3a.find_closest_intersection_distance(path3b) != 135:
        print("path3 intersections wrong. incorrect result: {}"
                .format(path3a.find_closest_intersection_distance(path3b)))
    if path3a.find_shortest_intersection_distance(path3b) != 410:
        print("path3 shortest intersection wrong. incorrect result: {}"
                .format(path3a.find_shortest_intersection_distance(path3b)))

if __name__ == "__main__":
    test()
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="input file containing directions")
    args = parser.parse_args()

    path1, path2 = parse_input(args.input)

    print("closest intersection distance: {}".format(
        path1.find_closest_intersection_distance(path2)))
    print("shortest intersection distance: {}".format(
        path1.find_shortest_intersection_distance(path2)))

