from player import Player
from agents import Agent, HumanInputAgent, RandomAgent, RuleBasedAgent

from ui import UI

from typing import List, Optional

if __name__ == "__main__":
    agents: List[Agent] = [HumanInputAgent(),
                           RandomAgent(),
                           RuleBasedAgent(),
                           RuleBasedAgent()]

    player1 = Player(name="Sebastian", agent=agents[0])
    player2 = Player(name="Hansel", agent=agents[1])
    player3 = Player(name="Yusuf", agent=agents[2])
    player4 = Player(name="Stefan", agent=agents[3])

    ui = UI(player1, player2, player3, player4)
    winner: Optional[Player] = ui.start_game()



