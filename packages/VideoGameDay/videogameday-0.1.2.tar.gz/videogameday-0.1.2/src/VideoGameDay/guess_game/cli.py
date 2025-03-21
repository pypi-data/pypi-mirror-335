import argparse
from .guesser import guess_the_game

def main():
    parser = argparse.ArgumentParser(description="Guess the video game from a cryptic description.")
    parser.add_argument("description", type=str, help="Enter a cryptic game description to guess the game.")
    args = parser.parse_args()

    print(guess_the_game(args.description))

if __name__ == "__main__":
    main()
