from player import Player
from agents import Agent, RandomAgent, HumanInputAgent
from ui import UI

from typing import List, Dict, Optional

if __name__ == "__main__":
    winner_map: Dict[str, int] = {}

    agents: List[Agent] = [
        RandomAgent(),
        RandomAgent(),
        RandomAgent()
    ]

    num_episodes: int = 1000
    for episode in range(num_episodes):
        player1 = Player(name="Stefan", agent=agents[0])
        player2 = Player(name="Hansel", agent=agents[1])
        player3 = Player(name="Yusuf", agent=agents[2])

        ui = UI(player1, player2, player3)
        winner: Optional[str] = ui.start_game()
        assert winner is not None
        if winner in winner_map:
            winner_map[winner] += 1
        else:
            winner_map[winner] = 1

        # for player in ui.players:
        #     if isinstance(player._agent, LearningAgent):
        #         player._agent.update_q_values()
                # use total rewards to update model and then reset

    player1 = Player(name="Stefan", agent=agents[0])
    player2 = Player(name="Hansel", agent=agents[1])
    player3 = Player(name="Yusuf", agent=agents[2])
    player4 = Player(name="Sebastian", agent=HumanInputAgent())

    ui = UI(player1, player2, player3, player4)
    winner: Optional[str] = ui.start_game()
    assert winner is not None
    if winner in winner_map:
        winner_map[winner] += 1
    else:
        winner_map[winner] = 1
    
    for name, win_c in winner_map.items():
        print(f"{name}: {win_c}")
