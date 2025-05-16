from player import Player
from game import Game
from agents import Agent, HumanInputAgent, RandomAgent, RuleBasedAgent

import sys
import os
from typing import List

if __name__ == "__main__":
    winner_map = {}

    agents: List[Agent] = [HumanInputAgent(),
                                   RandomAgent(),
                                   RuleBasedAgent()]

    for i in range(1):
        game = Game()
        player1 = Player(name="Sebastian", agent=agents[0])
        player2 = Player(name="Hansel", agent=agents[1])
        player3 = Player(name="Yusuf", agent=agents[2])

        game.enter_players(player1, player2, player3)
        winner: Player = game.start_game()
        if winner.name in winner_map:
            winner_map[winner.name] += 1
        else:
            winner_map[winner.name] = 1

    # for name, wins in winner_map.items():
    #     print(f"{name}: {wins}")


