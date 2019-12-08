from __future__ import print_function

class SpaceImage(object):
    def __init__(self, image_data, xdim, ydim):
        self.num_layers = len(image_data) // (xdim * ydim)
        self.image = []
        for l in range(self.num_layers):
            layer = []
            for y in range(ydim):
                start = l * xdim * ydim + y * xdim
                end = start + xdim
                layer.append(list(image_data[start:end]))
            self.image.append(layer)

    def count_pixels_in_layer(self, layer, pixel_value):
        matches = 0
        for line in self.image[layer]:
            matches += line.count(pixel_value)
        return matches

    def find_layer_with_fewest_zeroes(self):
        least_zeroes_layer = 0
        least_zeroes = -1
        for l in range(len(self.image)):
            zeroes = self.count_pixels_in_layer(l, "0")
            if least_zeroes == -1:
                least_zeroes = zeroes
                # least_zeroes_layer already set to 0
            elif zeroes < least_zeroes:
                least_zeroes = zeroes
                least_zeroes_layer = l
        return least_zeroes_layer

    def flatten_image(self):
        def _get_pixel_value(x, y):
            for layer in self.image:
                if layer[y][x] != "2":
                    return layer[y][x]

        flat = self.image[0]
        for y, line in enumerate(flat):
            for x, pixel in enumerate(line):
                flat[y][x] = _get_pixel_value(x, y)
        return flat

    def print_image(self):
        """render image as ascii art.

        2 -> transparent (" ")
        1 -> white (" ")
        0 -> black ("X")
        """
        flat = self.flatten_image()
        for line in flat:
            print("".join(line).replace("2", " ").replace("1", ".").replace("0", "X"))



def test():
    img = SpaceImage("123456789012", 3, 2)
    fewest_zeroes_layer = img.find_layer_with_fewest_zeroes()
    if (img.image != [[["1", "2", "3"], ["4", "5", "6"]], [["7", "8", "9"], ["0", "1", "2"]]]
            and fewest_zeroes_layer == 0):
        print("test1 failed")
    else:
        print("test1 passed")
    img = SpaceImage("0222112222120000", 2, 2)
    if img.flatten_image() == [["0", "1"], ["1", "0"]]:
        img.print_image()
        print("test2 passed")
    else:
        print("test2 failed")
if __name__ == "__main__":
    test()
    with open("input.txt", "r") as infile:
        image_data = infile.read()
        img = SpaceImage(image_data, 25, 6)
        fewest_zeroes_layer = img.find_layer_with_fewest_zeroes()
        ones = img.count_pixels_in_layer(fewest_zeroes_layer, "1")
        twos = img.count_pixels_in_layer(fewest_zeroes_layer, "2")
        print("part 1:")
        print("layer with fewest zeroes: {}".format(fewest_zeroes_layer))
        print("ones x twos: {}".format(ones * twos))

        print("part 2:")
        img.print_image()

