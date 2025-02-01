__author__ = "Lorenzo Argentieri"

import math


def repart_function(x, l=15):
    """
    Repartition function.

    This function takes a value x and returns a value between 0 and 1.
    The function is defined as 1 - e^(-lx).

    Args:
        x (float): The input value.
        l (float, optional): The lambda value. Defaults to 15.

    Returns:
        float: The output value.
    """
    e = math.e
    y = 1 - e ** (-1 * (l * x))
    return y


def laplace_distribution(x, beta=0.5, mu=0.5):
    """
    Laplace distribution function.

    This function takes a value x and returns a value between 0 and 1.
    The function is defined as (1 / (2 * beta)) * e^(-|x - mu| / beta).

    Args:
        x (float): The input value.
        beta (float, optional): The beta value. Defaults to 0.5.
        mu (float, optional): The mean value. Defaults to 0.5.

    Returns:
        float: The output value.
    """
    if x >= mu:
        tmp = x - mu
    else:
        tmp = mu - x

    core = -1 * (tmp / beta)
    y = (math.e * core) / (2 * beta)
    return y


def laplace_distribution2(x, beta=0.5, mu=5):
    """
    Laplace distribution function.

    This function takes a value x and returns a value between 0 and 1.
    The function is defined as (1 / (2 * beta)) * e^(-|x - mu| / beta).

    Args:
        x (float): The input value.
        beta (float, optional): The beta value. Defaults to 0.5.
        mu (float, optional): The mean value. Defaults to 5.

    Returns:
        float: The output value.
    """
    x = x * 10
    core = math.e ** (-1 * abs(x - mu) / beta)
    y = core / (2 * beta)
    return y
