import pytest
from VideoGameDay.recommend_game.recommend_game import validate_input, print_menu
from VideoGameDay.recommend_game.game_data import get_game_categories

def test_validate_input_numeric_valid():
    """Test numeric input corresponding to a valid genre index"""
    genres = get_game_categories()
    genre, valid = validate_input("0")  # Should match the first genre
    assert valid == 1
    assert genre == genres[0]

def test_validate_input_text_valid():
    """Test text input corresponding to a valid genre"""
    genres = get_game_categories()
    genre, valid = validate_input(genres[1].lower())  # Second genre in lowercase
    assert valid == 1
    assert genre == genres[1]

def test_validate_input_invalid():
    """Test invalid input (out of range index and incorrect string)"""
    genre, valid = validate_input("100")  # Out of range index
    assert valid == 0
    assert genre is None

    genre, valid = validate_input("invalid_genre")  # Non-existing genre
    assert valid == 0
    assert genre is None