from player import Player
from game import Game
from agents import RandomAgent, RuleBasedAgent, LearningAgent

import sys
import os

if __name__ == "__main__":
    # winner_map = {}

    # learning_agent: LearningAgent = LearningAgent("Sebastian")

    # sys.stdout = open(os.devnull, 'w')
    # for i in range(10000):
    #     game = Game()
    #     player1 = Player(name="Sebastian", agent=learning_agent)
    #     player2 = Player(name="Hansel", agent=RandomAgent("Hansel"))
    #     player3 = Player(name="Yusuf", agent=RandomAgent("Yusuf"))
    #     player4 = Player(name="Stefan", agent=RandomAgent("Stefan"))
    #     player5 = Player(name="Liam", agent=RandomAgent("Liam"))
    #     player6 = Player(name="James", agent=RandomAgent("James"))

    #     game.enter_players(player1, player2, player3, player4, player5, player6)
    #     winner: Player = game.start_game()
    #     if winner.name in winner_map:
    #         winner_map[winner.name] += 1
    #     else:
    #         winner_map[winner.name] = 0

    # sys.stdout = sys.__stdout__

    # for name, wins in winner_map.items():
    #     print(f"{name}: {wins}")

    # print(learning_agent)


    game = Game()
    player1 = Player(name="Sebastian", agent=RandomAgent("Sebastian"))
    player2 = Player(name="Hansel", agent=RandomAgent("Hansel"))
    player3 = Player(name="Yusuf", agent=RandomAgent("Yusuf"))
    player4 = Player(name="Stefan", agent=RandomAgent("Stefan"))
    player5 = Player(name="Liam", agent=RandomAgent("Liam"))
    player6 = Player(name="James", agent=RandomAgent("James"))

    game.enter_players(player1, player2, player3, player4, player5, player6)
    winner: Player = game.start_game()
