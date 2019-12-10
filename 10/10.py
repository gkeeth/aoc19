#! /usr/bin/env python
from __future__ import print_function, division
from math import atan2, pi

class AsteroidMap(object):
    def __init__(self, inmap):
        self.map = [list(line.strip()) for line in inmap]

    def count_visible_asteroids(self, x0, y0):
        """count asteroids visible from the asteroid at location (x0, y0)."""
        hit_vectors = set()
        for y, row in enumerate(self.map):
            for x, col in enumerate(row):
                if self.map[y][x] == "#" and not (y == y0 and x == x0):
                    hit_vectors.add(atan2(y-y0, x-x0))
        return len(hit_vectors)


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
        self.asteroid_map = asteroid_map
        self.location = (x0, y0)
        self.target = (x0-1, 0) # aim 1 step behind top dead center
        self.shots = 0
        angles = []
        for y, row in enumerate(asteroid_map.map):
            for x, col in enumerate(row):
                angles.append(atan2(y - y0, x - x0) - pi / 2)
        self.angles = sorted(angles)

    def pick_next_target(self):
        # increment self.target appropriately
        current_angle = atan2(self.target[1], self.target[0])
        # 1. pick next vector (angle)
        # TODO

        # 2. target asteroid along that vector that is closest to laser
        # TODO

        # 3. if no target exists along vector, pick a new vector (go to 1)
        # TODO


    def fire_lazer(self):
        # hello 2007
        self.pick_next_target()
        self.shots += 1
        self.asteroid_map.map[target[1]][target[0]] = str(self.shots)
        return target


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

if __name__ == "__main__":
    test()
    with open("input.txt", "r") as infile:
        m = infile.readlines()
    amap = AsteroidMap(m)
    coords, asteroids = amap.find_best_asteroid()
    print("best asteroid is at {}; {} asteroids visible".format(coords, asteroids))
