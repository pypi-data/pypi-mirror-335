import unittest
from VideoGameDay.fun_fact_rand.fun_facts_db import DB  # ✅ Fixed
from VideoGameDay.fun_fact_rand.fun_facts import get_fun_facts  # ✅ Fixed

class TestFunFacts(unittest.TestCase):

    def test_valid_game_name(self):
        """Test if a known game name returns a fun fact."""
        game = "Elden Ring"
        fact = get_fun_facts(game)
        self.assertTrue(any(fact.endswith(fact_part) for fact_part in DB[game]))

    def test_case_insensitive_lookup(self):
        """Test if the function works regardless of casing in the game name."""
        game_variants = ["elden ring", "ELDEN RING", "ElDeN rInG"]
        expected_facts = DB["Elden Ring"]

        for variant in game_variants:
            fact = get_fun_facts(variant)
            self.assertTrue(any(fact.endswith(fact_part) for fact_part in expected_facts),
                            f"Fact '{fact}' is not in expected list: {expected_facts}")

    def test_invalid_game_name(self):
        """Test if an unknown game returns the correct error message."""
        game = "Unknown Game"
        fact = get_fun_facts(game)
        self.assertIn("❌ Sorry, I don't have fun facts for", fact)

if __name__ == "__main__":
    unittest.main()