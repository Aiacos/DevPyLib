__author__ = 'Lorenzo Argentieri'

import math

def repartFunction(x, l=5):
    e = math.e
    y = 1 - e ^ (-1*(l * x))
    return y

def laplaceDistribution(x, beta=0.5, mu=0.5):
    if x >= mu:
        tmp = x - mu
    else:
        tmp = mu - x

    core = -1 * (tmp / beta)
    y = (math.e * core) / (2 * beta)
    return y
