"""Module providing a recommend game after inputting a genre"""

import random
from .game_data import get_game_categories, get_game_dic


def recommend_game():
    """Print out the genre of games
    Get the input of the user
    Output corresponding games
    """
    valid = 0
    genre = None
    while not valid:
        print_menu()
        in_str = input("Enter your choice: ").strip().lower()
        genre, valid = validate_input(in_str)
        if not valid:
            print("Try again: invalid input!")

    game_dict = get_game_dic()
    games = game_dict[genre]
    game = random.choice(games)
    print(f"You should play {game}!")


def print_menu():
    """Print out the genre of games"""
    print("What kind of games would you like to play?")
    genres = get_game_categories()
    for i in range(len(genres)):
        print(f"{i}. {genres[i]}")
    print(f"{i+1}. Random")


def validate_input(in_str: str):
    """Validate input
    The first return is a string
    The second return is 1 if input is valid
    0 otherwise
    """
    genres = get_game_categories()
    if in_str.isnumeric():
        in_str = int(in_str)
        if in_str == len(genres):
            return random.choice(genres), 1
        elif in_str > -1 and in_str < len(genres):
            return genres[in_str], 1
    elif in_str.isalpha():
        in_str = in_str.lower()
        if in_str == "random":
            return random.choice(genres), 1
        for genre in genres:
            if in_str == genre.lower():
                return genre, 1
    return None, 0
