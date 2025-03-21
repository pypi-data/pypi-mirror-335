# Import all functions from submodules
from .guess_game import *
from .gaming_luck import *
from .recommend_game import *
from .fun_fact_rand import *

# Define what gets imported when using `from VideoGameDay import *`
__all__ = [
    # guess_game functions
    "guess_the_game",
    "find_closest_match",

    # gaming_luck functions
    "gaming_luck_meter",

    # recommend_game functions
    "recommend_game",
    "print_menu",
    "validate_input",

    # fun_facts functions
    "get_fun_facts",
]
