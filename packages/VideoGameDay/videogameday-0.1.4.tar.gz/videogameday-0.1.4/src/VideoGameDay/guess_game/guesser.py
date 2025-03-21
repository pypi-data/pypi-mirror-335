import difflib
import random
from .game_data import GAME_POOL, GAME_HINTS

def find_closest_match(description: str) -> str:
    """
    Find the closest matching game based on description similarity.
    If no close match is found, return a random game from the answer pool.
    """
    closest_match = difflib.get_close_matches(description, GAME_HINTS.keys(), n=1, cutoff=0.4)
    if closest_match:
        return GAME_HINTS[closest_match[0]]
    else:
        return random.choice(GAME_POOL)

def guess_the_game(description: str) -> str:
    """
    Takes a cryptic game description and returns the best-matching game.
    """
    return f"The answer is {find_closest_match(description)}!"
