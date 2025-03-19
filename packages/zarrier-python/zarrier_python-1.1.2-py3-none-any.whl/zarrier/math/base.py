import math

def in_region(a, p1, p2, include_end=True):
    if include_end:
        return (p1 >= a >= p2) or (p2 >= a >= p1)
    else:
        return (p1 > a > p2) or (p2 > a > p1)

def equal_rect(c, area):
    """
    a + b = c/2
    a * b = area
    a >= b
    return a , b
    """

    A = -1
    B = c/2
    C = -area

    sqdelta = math.sqrt(B * B - 4 * A * C)

    x1 =(-B + sqdelta) / (2 * A)
    x2 =(-B - sqdelta) / (2 * A)
    return x2, x1