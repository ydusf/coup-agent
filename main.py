from player import Player
from agents import Agent, RandomAgent, RuleBasedAgent
from ui import UI

from typing import List, Dict, Optional

if __name__ == "__main__":
    winner_map: Dict[str, int] = {}

    agents: List[Agent] = [
        RandomAgent(),
        RandomAgent(),
        RuleBasedAgent(),
        RuleBasedAgent(),
    ]

    player1 = Player(name="Sebastian", agent=agents[0])
    player2 = Player(name="Hansel", agent=agents[1])
    player3 = Player(name="Yusuf", agent=agents[2])
    player4 = Player(name="Stefan", agent=agents[3])

    ui = UI(player1, player2, player3, player4)
    winner: Optional[str] = ui.start_game()

    for player in ui.players:
        print(f"{player.name}: {player._agent._total_reward}")
