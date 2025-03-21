import random
from difflib import get_close_matches
from .fun_facts_db import DB

def get_fun_facts(game_name: str):
    """
    Returns a random fun fact about a given video game.
    
    :param game_name: Name of the game.
    :return: A string containing a fun fact about the game.
    """

    game_name = game_name.strip().title()

    # Try exact match first
    if game_name in DB:
        fact = random.choice(DB[game_name])
        return f"🎮 Fun fact about {game_name}: {fact}"

    # Attempt fuzzy matching if exact match fails
    close_matches = get_close_matches(game_name, DB.keys(), n=1, cutoff=0.6)
    if close_matches:
        best_match = close_matches[0]
        fact = random.choice(DB[best_match])
        return f"Did you mean '{best_match}'?\n🎮 Fun fact: {fact}"

    # If no match found
    return f"❌ Sorry, I don't have fun facts for '{game_name}'. Try another game!"


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Retrieve fun facts about a video game.")
    parser.add_argument("game_name", type=str, help="The name of the game to get fun facts about.")
    args = parser.parse_args()

    print(get_fun_facts(args.game_name))