from bisect import bisect_right
from itertools import accumulate


def _nearest_boundary(lb, rb, c, p):
    """Find the boundary nearest to `c`. In case of a draw, the parameter `p`
    decides which one is chosen.

    :arg int lb: Left boundary.
    :arg int rb: Right boundary.
    :arg int c: Coordinate (`lb` <= `c` <= `rb`)).
    :arg int p: Preference in case of a draw: 0: left, 1: right.

    :returns int: Nearest boundary: 0: left, 1: right.
    """
    dl = c - lb + 1
    dr = rb - c

    if dl < dr:
        return 0
    if dl > dr:
        return 1
    return p

def nearest_location(ls, c, p=0):
    """Find the location nearest to `c`. In case of a draw, the parameter `p`
    decides which index is chosen.

    :arg list ls: List of locations.
    :arg int c: Coordinate.
    :arg int p: Preference in case of a draw: 0: left, 1: right.

    :returns int: Nearest location.
    """
    rb = len(ls) - 1
    lb = 0

    while lb <= rb:
        i = (lb + rb) // 2

        if c < ls[i][0]:     # `c` lies before this location.
            rb = i - 1
        elif c >= ls[i][1]:  # `c` lies after this location.
            lb = i + 1
        else:                # `c` lies in this location.
            return i

    if i and c < ls[i][0]:  # `c` lies before this location.
        return i - 1 + _nearest_boundary(ls[i - 1][1], ls[i][0], c, p)
    if i < len(ls) - 1:     # `c` lies after this location.
        return i + _nearest_boundary(ls[i][1], ls[i + 1][0], c, p)

    return i


def _offsets(locations, orientation):
    """For each location, calculate the length of the preceding locations.

    :arg list locations: List of locations.
    :arg int orientation: Direction of {locations}.

    :returns list: List of cumulative location lengths.
    """
    return [0] + list(accumulate(map(lambda x: x[1] - x[0], locations[::orientation][:-1])))


def multi_locus(locations, inverted=False):

    loci = [Locus(location, inverted) for location in locations]
    orientation = -1 if inverted else 1
    offsets = _offsets(locations, orientation)


 def multi_locus_direction(index, inverted, offsets):
        if inverted:
            return len(offsets) - index - 1
        return index

def multi_locus_outside(coordinate, loci):
        """Calculate the offset relative to this MultiLocus.

        :arg int coordinate: Coordinate.

        :returns int: Negative: upstream, 0: inside, positive: downstream.
        """
        if coordinate < loci[0].boundary[0]:
            return coordinate - loci[0].boundary[0]
        if coordinate > loci[-1].boundary[1]:
            return coordinate - loci[-1].boundary[1]
        return 0

def multi_locus_to_position(coordinate, offsets, orientation, locations, inverted, loci):
    """Convert a coordinate to a position.

    :arg int coordinate: Coordinate.

    :returns tuple: Position.
    """
    index = nearest_location(locations, coordinate, inverted)
    outside = orientation * multi_locus_outside(coordinate)
    location = loci[index].to_position(coordinate)

    return location[0] + _offsets[multi_locus_direction(index, inverted, offsets)] ,location[1], outside

def _coordinate_to_coding(coordinate):
    """Convert a coordinate to a coding position (c./r.).

    :arg int coordinate: Coordinate.

    :returns tuple: Coding position (c./r.).
    """
    pos = _noncoding.to_position(coordinate)

    if pos[0] < _coding[0]:
        return pos[0] - _coding[0], pos[1], -1, pos[2]
    elif pos[0] >= _coding[1]:
        return pos[0] - _coding[1] + 1, pos[1], 1, pos[2]
    return pos[0] - _coding[0] + 1, pos[1], 0, pos[2]


def coordinate_to_coding(coordinate, degenerate=False):
    """Convert a coordinate to a coding position (c./r.).

    :arg int coordinate: Coordinate.
    :arg bool degenerate: Return a degenerate position.

    :returns tuple: Coding position (c./r.).
    """
    pos = _coordinate_to_coding(coordinate)

    if degenerate and pos[3]:
        if pos[2] == 0:
            if pos[0] == 1 and pos[1] < 0:
                return pos[1], 0, -1, pos[3]
            if pos[0] == _cds_len and pos[1] > 0:
                return pos[0] + pos[1] - _cds_len, 0, 1, pos[3]
        return pos[0] + pos[1], 0, pos[2], pos[3]

    return pos