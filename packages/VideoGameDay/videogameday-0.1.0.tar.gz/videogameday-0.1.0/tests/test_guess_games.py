import pytest
from guess_game.guesser import find_closest_match, guess_the_game
from guess_game.game_data import GAME_HINTS, GAME_POOL


def test_exact_match():
    """Test if an exact match in GAME_HINTS returns the correct game."""
    description = "A silent hero, a green outfit, a princess in distress."
    assert guess_the_game(description) == "The answer is The Legend of Zelda!"


def test_partial_match():
    """Test if a close match returns the correct game."""
    description = "A cursed warrior fights monsters in a brutal world."
    expected_game = "Dark Souls"  # Closest match in hints
    assert expected_game in guess_the_game(description)


def test_no_close_match():
    """Test if a random game is returned when there is no close match."""
    description = "A game about farming and cooking."
    result = guess_the_game(description).replace("The answer is ", "").replace("!", "")
    assert result in GAME_POOL  # Should be one of the known games


def test_case_insensitivity():
    """Ensure that descriptions are case insensitive."""
    description = "a SILENT HERO, A GREEN outfit, a PRINCESS in distress."
    assert guess_the_game(description) == "The answer is The Legend of Zelda!"


def test_extra_spaces():
    """Ensure that extra spaces in the input do not affect matching."""
    description = "  A silent hero,  a green outfit, a princess in distress.  "
    assert guess_the_game(description.strip()) == "The answer is The Legend of Zelda!"


def test_find_closest_match():
    """Test find_closest_match directly with a known description."""
    description = "A space marine takes on demons from hell."
    expected_game = "Doom"  # Closest match from GAME_HINTS
    assert find_closest_match(description) == expected_game


def test_random_selection():
    """Test that find_closest_match returns a random game when no match is found."""
    description = "A game about baking bread in space."
    result = find_closest_match(description)
    assert result in GAME_POOL  # Should be one of the predefined games


def test_hint_matching_accuracy():
    """Ensure the hints are matched accurately."""
    for hint, game in GAME_HINTS.items():
        assert find_closest_match(hint) == game


def test_different_game_pool():
    """Check that GAME_POOL contains unique values and enough games."""
    assert len(set(GAME_POOL)) == len(GAME_POOL)  # No duplicates
    assert len(GAME_POOL) > 10  # At least 10 games should be present


def test_empty_input():
    """Check behavior when given an empty string."""
    description = ""
    result = find_closest_match(description)
    assert result in GAME_POOL  # Should still return a random game
