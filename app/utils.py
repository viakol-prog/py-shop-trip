import math


def get_distance(loc1, loc2):
    return math.hypot(loc1[0] - loc2[0], loc1[1] - loc2[1])
