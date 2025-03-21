"""Test module for recommend_game.py using pytest and mocking."""

import pytest
from unittest.mock import patch
from VideoGameDay.recommend_game.recommend_game import recommend_game, print_menu


# Mock data for testing
TEST_GENRES = ["RPG", "Shooter", "Horror"]
TEST_GAMES = {
    "RPG": ["The Witcher 3", "Final Fantasy"],
    "Shooter": ["DOOM", "Halo"],
    "Horror": ["Resident Evil", "Silent Hill"],
}


def test_print_menu(capsys):
    """Test the print_menu function."""
    with patch(
        "VideoGameDay.recommend_game.recommend_game.get_game_categories",
        return_value=TEST_GENRES,
    ):
        print_menu()
        captured = capsys.readouterr()
        assert "What kind of games would you like to play?" in captured.out
        for i, genre in enumerate(TEST_GENRES):
            assert f"{i}. {genre}" in captured.out
        assert f"{len(TEST_GENRES)}. Random" in captured.out


@patch(
    "VideoGameDay.recommend_game.recommend_game.get_game_categories",
    return_value=TEST_GENRES,
)
@patch(
    "VideoGameDay.recommend_game.recommend_game.get_game_dic", return_value=TEST_GAMES
)
def test_recommend_game_valid_input(mock_dict, mock_cat, capsys):
    """Test the recommend_game function with valid input."""
    with patch("builtins.input", return_value="0"):
        recommend_game()
        captured = capsys.readouterr()
        assert "You should play" in captured.out
        assert any(game in captured.out for game in TEST_GAMES["RPG"])


@patch(
    "VideoGameDay.recommend_game.recommend_game.get_game_categories",
    return_value=TEST_GENRES,
)
@patch(
    "VideoGameDay.recommend_game.recommend_game.get_game_dic", return_value=TEST_GAMES
)
def test_recommend_game_invalid_then_valid_input(mock_dict, mock_cat, capsys):
    """Test recovery from invalid input."""
    with patch("builtins.input", side_effect=["invalid", "1"]):
        recommend_game()
        captured = capsys.readouterr()
        assert "Try again: invalid input!" in captured.out
        assert "You should play" in captured.out
        assert any(game in captured.out for game in TEST_GAMES["Shooter"])


if __name__ == "__main__":
    pytest.main(["-v", "test_recommend_game.py"])
