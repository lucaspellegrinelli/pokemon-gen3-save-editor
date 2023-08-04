def get_growth_chunk(order):
    if order in [0, 1, 2, 3, 4, 5]:
        return 0
    if order in [6, 7, 12, 13, 18, 19]:
        return 1
    if order in [8, 10, 14, 16, 20, 22]:
        return 2
    return 3


def get_evs_chunk(order):
    if order in [12, 13, 14, 15, 16, 17]:
        return 0
    if order in [2, 3, 8, 9, 22, 23]:
        return 1
    if order in [0, 5, 6, 11, 19, 21]:
        return 2
    return 3


def get_misc_chunk(order):
    if order in [18, 19, 20, 21, 22, 23]:
        return 0
    if order in [4, 5, 10, 11, 16, 17]:
        return 1
    if order in [1, 3, 7, 9, 13, 15]:
        return 2
    return 3
