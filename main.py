from player import Player
from game import Game
from agents import RandomAgent, LearningAgent

import sys
import os

if __name__ == "__main__":

    sys.stdout = open(os.devnull, 'w')
    for i in range(20000):
        game = Game()
        player1 = Player(name="Sebastian", agent=RandomAgent())
        player2 = Player(name="Hansel", agent=RandomAgent())
        player3 = Player(name="Yusuf", agent=RandomAgent())
        player4 = Player(name="Stefan", agent=RandomAgent())
        player5 = Player(name="Liam", agent=RandomAgent())
        player6 = Player(name="James", agent=RandomAgent())

        game.enter_players(player1, player2, player3, player4, player5, player6)
        winner: Player = game.start_game()
        
        for player in game._players:
            if player == winner:
                player.propogate_result(True)
            else:
                player.propogate_result(False)

    sys.stdout = sys.__stdout__

    game = Game()
    player1 = Player(name="Sebastian", agent=RandomAgent())
    player2 = Player(name="Hansel", agent=RandomAgent())
    player3 = Player(name="Yusuf", agent=RandomAgent())
    player4 = Player(name="Stefan", agent=RandomAgent())
    player5 = Player(name="Liam", agent=RandomAgent())
    player6 = Player(name="James", agent=RandomAgent())

    game.enter_players(player1, player2, player3, player4, player5, player6)
    game.start_game()
