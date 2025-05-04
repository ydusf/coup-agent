from player import Player
from game import Game
from agents import RandomAgent

if __name__ == "__main__":
    game = Game()

    player1 = Player(name="Sebastian", agent=RandomAgent())
    player2 = Player(name="Hansel", agent=RandomAgent())
    player3 = Player(name="Yusuf", agent=RandomAgent())

    game.enter_players(player1, player2, player3)
    game.start_game()