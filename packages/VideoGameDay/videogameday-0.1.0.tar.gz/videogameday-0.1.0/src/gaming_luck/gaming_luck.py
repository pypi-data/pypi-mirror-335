import random
from .luck_data import GAME_TYPES, LUCK_MESSAGES

def gaming_luck_meter() -> str:
    
    game_type_map = {key.lower(): key for key in GAME_TYPES}
    
    # Choosing game type from GAME_TYPES
    print("🎮 Choose your game type today:")
    for key, value in GAME_TYPES.items():
        print(f"  [{key}] - {value}")

    chosen_game = None
    while chosen_game not in GAME_TYPES:
        user_input = input("Enter your choice: ").strip().lower()
        if user_input in game_type_map:
            chosen_game = game_type_map[user_input]
        else:
            print("❌ Invalid choice. Please select a valid game type.")

    # Higher probability for higher luck range
    luck_ranges = {
        "high": list(range(70, 101)),
        "mid": list(range(50, 70)),
        "low": list(range(0, 50)),
    }

    chosen_range = random.choices(
        population=["high", "mid", "low"],
        weights=[0.6, 0.35, 0.05], 
        k=1
    )[0]

    luck = random.choice(luck_ranges[chosen_range])

    if luck >= 70:
        luck_level = "high"
    elif luck >= 40:
        luck_level = "mid"
    else:
        luck_level = "low"

    # Print luck message
    message = LUCK_MESSAGES[chosen_game][luck_level]

    return f"\n🎮 You're playing「{GAME_TYPES[chosen_game]}」today! \n   Your gaming luck is「{luck}%」.\n{message}\n"

if __name__ == "__main__":
    print(gaming_luck_meter())
