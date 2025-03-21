"""This module provides data for recommend_game.py module"""

game_categories = {
    "RPG": [
        "The Witcher 3",
        "Skyrim",
        "Dark Souls",
        "Elden Ring",
        "Cyberpunk 2077",
        "Fallout",
        "Bloodborne",
    ],
    "Shooter": ["Halo", "Call of Duty", "Doom", "Half-Life"],
    "Horror": ["Resident Evil", "The Last of Us"],
    "Platformer": ["Sonic the Hedgehog", "Super Mario Bros"],
    "Open-World/Action-Adventure": [
        "The Legend of Zelda",
        "Red Dead Redemption 2",
        "Grand Theft Auto V",
    ],
    "Puzzle": ["Portal"],
    "Sandbox": ["Minecraft"],
}


def get_game_categories():
    """This function returns the keys of the game_categories dictionary as a list"""
    return list(game_categories.keys())


def get_game_dic():
    """This function returns the whole dictionary"""
    return game_categories
