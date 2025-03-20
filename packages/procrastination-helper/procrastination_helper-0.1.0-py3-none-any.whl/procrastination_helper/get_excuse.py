import random
from .data.excusesData import sample_excuses
def get_excuse():
    return random.choice(sample_excuses)
