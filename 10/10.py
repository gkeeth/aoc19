#! /usr/bin/env python
from __future__ import print_function, division
from math import atan2, pi, sqrt
from collections import defaultdict

class AsteroidMap(object):
    def __init__(self, inmap):
        self.map = [list(line.strip()) for line in inmap]

    def asteroid_angles(self, x0, y0):
        """generator to calculate sight angles to other asteroids.

        calculates angle from asteroid at (x0,y0) to other asteroids in the
        asteroid map.

        angles are flipped/rotated so up is an angle of 0, and right is pi/2.

        returns angle and the coordinates of the asteroid.
        """
        for y, row in enumerate(self.map):
            for x, col in enumerate(row):
                if self.map[y][x] == "#" and not (y == y0 and x == x0):
                    angle = atan2(y - y0, x - x0) + pi / 2
                    if angle < 0:
                        angle += 2*pi
                    yield angle, (x, y)

    def count_visible_asteroids(self, x0, y0):
        """count asteroids visible from the asteroid at location (x0, y0)."""
        return len(set([w for w, _ in self.asteroid_angles(x0, y0)]))

    def find_best_asteroid(self):
        """find the asteroid with best visibility of other asteroids.

        return the coordinates of the best asteroid and the number of other
        asteroids in its line-of-sight.
        """
        max_vis = 0
        max_x = 0
        max_y = 0
        for y, row in enumerate(self.map):
            for x, col in enumerate(row):
                if self.map[y][x] == "#":
                    vis = self.count_visible_asteroids(x, y)
                    if vis > max_vis:
                        max_vis = vis
                        max_x = x
                        max_y = y

        return (max_x, max_y), max_vis

class AsteroidDefenseLaser(object):
    def __init__(self, asteroid_map, x0, y0):
        self.location = (x0, y0)
        self.current_angle_index = -1

        # mapping of angles to list of asteroid coordinates along that vector
        self.angles_to_asteroids = defaultdict(list)
        for w, xy in asteroid_map.asteroid_angles(
                self.location[0], self.location[1]):
            self.angles_to_asteroids[w].append(xy)
        # sort asteroid coordinates by distance
        for w in self.angles_to_asteroids:
            self.angles_to_asteroids[w] = sorted(self.angles_to_asteroids[w], key=self.dist)
        # list of angles to sweep through in order
        self.angles = sorted(self.angles_to_asteroids.keys())

    def dist(self, coords):
        return sqrt((self.location[0] - coords[0])**2
                + (self.location[1] - coords[1])**2)

    def check_target_exists(self):
        if self.angles_to_asteroids[self.angles[self.current_angle_index]]:
            return True
        else:
            return False

    def pick_next_target(self):
        def next_angle_index():
            return (self.current_angle_index + 1) % len(self.angles)

        # increment target
        self.current_angle_index = next_angle_index()
        # check if any asteroids remain along that vector; if not, go to next target
        while not self.check_target_exists():
            self.current_angle_index = next_angle_index()

    def fire_lazer(self):
        # hello 2007
        self.pick_next_target()
        return self.angles_to_asteroids[self.angles[self.current_angle_index]].pop(0)

def test():
    inmaps = [
              [".#..#",
               ".....",
               "#####",
               "....#",
               "...##"
              ],
              ["......#.#.",
               "#..#.#....",
               "..#######.",
               ".#.#.###..",
               ".#..#.....",
               "..#....#.#",
               "#..#....#.",
               ".##.#..###",
               "##...#..#.",
               ".#....####"
              ],
              ["#.#...#.#.",
               ".###....#.",
               ".#....#...",
               "##.#.#.#.#",
               "....#.#.#.",
               ".##..###.#",
               "..#...##..",
               "..##....##",
               "......#...",
               ".####.###."
              ],
              [".#..#..###",
               "####.###.#",
               "....###.#.",
               "..###.##.#",
               "##.##.#.#.",
               "....###..#",
               "..#.#..#.#",
               "#..#.#.###",
               ".##...##.#",
               ".....#.#.."
              ],
              [".#..##.###...#######",
               "##.############..##.",
               ".#.######.########.#",
               ".###.#######.####.#.",
               "#####.##.#.##.###.##",
               "..#####..#.#########",
               "####################",
               "#.####....###.#.#.##",
               "##.#################",
               "#####.##.###..####..",
               "..######..##.#######",
               "####.##.####...##..#",
               ".#####..#.######.###",
               "##...#.##########...",
               "#.##########.#######",
               ".####.#.###.###.#.##",
               "....##.##.###..#####",
               ".#.#.###########.###",
               "#.#.#.#####.####.###",
               "###.##.####.##.#..##",
              ]
              ]
    goal_coords = [(3, 4),(5,8),(1,2),(6,3),(11,13)]
    goal_asteroids = [8,33,35,41,210]
    for n, inmap in enumerate(inmaps):
        amap = AsteroidMap(inmap)
        coords, asteroids = amap.find_best_asteroid()
        if goal_coords[n] == coords and goal_asteroids[n] == asteroids:
            print("test{} passed".format(n))
        else:
            print("test{} failed".format(n))
            print("calculated coords: {}".format(coords))
            print("expected coords: {}".format(goal_coords[n]))
            print("calculated max visible asteroids: {}".format(asteroids))
            print("expected visible asteroids: {}".format(goal_asteroids[n]))
            print("calculated visible asteroids at expected location: {}"
                    .format(amap.count_visible_asteroids(goal_coords[n][0],
                        goal_coords[n][1])))
    amap = AsteroidMap([".##",
                        ".##",
                        "#.."])
    adl = AsteroidDefenseLaser(amap,1,1)
    inmaps = [[".#....#####...#..",
               "##...##.#####..##",
               "##...#...#.#####.",
               "..#.....#...###..",
               "..#.#.....#....##",
              ],
             ]
    targetmaps = [[(8,1), (9,0), (9,1), (10,0), (9,2)]]
    for n, inmap in enumerate(inmaps):
        adl = AsteroidDefenseLaser(AsteroidMap(inmap), 8, 3)
        for target in targetmaps[n]:
            hit = adl.fire_lazer()
            if hit != target:
                print("test {} failed, destroyed {} instead of {}".format(n, hit, target))

if __name__ == "__main__":
    test()
    with open("input.txt", "r") as infile:
        m = infile.readlines()
    # part 1
    amap = AsteroidMap(m)
    coords, asteroids = amap.find_best_asteroid()
    print("best asteroid is at {}; {} asteroids visible".format(coords, asteroids))
    # part 2
    adl = AsteroidDefenseLaser(amap, coords[0], coords[1])
    for _ in range(200):
        hit = adl.fire_lazer()
    print("200th asteroid hit: {}; code: {}".format(hit, hit[0] * 100 + hit[1]))



