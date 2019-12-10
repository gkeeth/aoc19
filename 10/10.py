#! /usr/bin/env python
from __future__ import print_function, division

class AsteroidMap(object):
    def __init__(self, inmap):
        self.map = [list(line.strip()) for line in inmap]

    def count_visible_asteroids(self, x0, y0):
        """count asteroids visible from the asteroid at location (x0, y0)."""
        hit_vectors = set()
        for y, row in enumerate(self.map):
            for x, col in enumerate(row):
                if self.map[y][x] == "#" and not (y == y0 and x == x0):
                    if x == x0:
                        # undefined slope
                        if y - y0 > 0:
                            vec = ("V", "U") # vertical up
                        else:
                            vec = ("V", "D") # vertical down
                    else:
                        vec = ((y - y0) / (x - x0), "R" if x - x0 > 0 else "L")
                    hit_vectors.add(vec)
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
