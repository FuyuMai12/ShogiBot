from math import exp
from random import Random
from typing import List

EPSILON = 10.0 ** (-9)

def softmax(vals: List[float]) -> List[float]:
    """
    Calculate softmax for a list of values

    Arguments:
    - vals (List[float]):
        List of values before softmax

    Returns:
        List[float]:
            List of softmax results. It should have the sum at approximately 1.0.
    """
    exp_vals = [exp(val) for val in vals]
    return [exp_val / sum(exp_vals) for exp_val in exp_vals]

    # end softmax()

def choose_from_probability_list(probability_list: List[float],
                                 rng: Random) -> int:
    """
    Return the index of the chosen option in a list, given that list's
    probability distribution

    Arguments:
    - probability_list (List[float]):
        List of options' probabilities - they should sum up at approximately 1
    - rng (random.Random):
        A random number generator

    Returns:
        int:
            Index of the chosen option, in accordance to the given list's order
    """
    randomized_number = rng.random()
    chosen_index = 0
    accumulated_probability = 0
    for probability in probability_list:
        accumulated_probability += probability
        if accumulated_probability >= randomized_number - EPSILON:
            break
        chosen_index += 1

    return chosen_index

    # end choose_from_probability_list()
