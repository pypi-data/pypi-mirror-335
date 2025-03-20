import random
from .data.excusesData import sample_excuses

#returns n amount of randmon excuses from the sample_excuses
def get_excuse_list(n):
    return random.sample(sample_excuses, min(n, len(sample_excuses)))
