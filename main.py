from player import Player
from game import Game
from agents import Agent

if __name__ == "__main__":
    game = Game()

    player1 = Player(name="Sebastian", agent=Agent())
    player2 = Player(name="Hansel", agent=Agent())
    player3 = Player(name="Yusuf", agent=Agent())
    player4 = Player(name="Stefan", agent=Agent())
    player5 = Player(name="Liam", agent=Agent())

    game.enter_players(player1, player2, player3)
    game.start_game()