from player import Player
from agents import HumanInputAgent, RandomAgent
from game import Game
from logger import Logger

if __name__ == "__main__":
    players = [
        Player("Sebastian", RandomAgent()),
        Player("Stefan", RandomAgent()),
        Player("Yusuf", RandomAgent()),
        Player("Hansel", HumanInputAgent())
    ]

    # Play a game
    game = Game()
    game.enter_players(*players)
    game.initialise_game()
    logger = Logger()

    while game.game_is_active():
        game.handle_action(logger)
        game.goto_next_player()

        if game.get_players_left() <= 1:
            game.declare_winner(logger)
            break

    print(f"Game finished! Winner: {game._winner.name if game._winner else 'No winner'}")
