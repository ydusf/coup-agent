from utils import GameState, Action

from typing import Optional

class Logger:
    def __init__(self) -> None:
        pass

    def log_turn_start(self, player_name: str, game_state: Optional[GameState]) -> None:
        print(f"{player_name}'s turn")

    def log_action(self, instigator: str, action: Action, target: Optional[str], game_state: Optional[GameState]) -> None:
        if target is not None:
            print(f"{instigator} claimed {action} against {target}")
        else:
            print(f"{instigator} claimed {action}")

    def log_challenge(self, instigator: str, challenger: str, action: Action, success: bool, game_state: Optional[GameState]) -> None:
        if success:
            print(f"{challenger} succeeded the challenge {instigator} who claimed {action}")
        else:
            print(f"{challenger} failed the challenge against {instigator} who claimed {action}")

    def log_no_challenge(self, instigator: str, allower: str, action: Action, game_state: Optional[GameState]) -> None:
        print(f"{allower} did not challenge {instigator} who claimed {action}")

    def log_block(self, instigator: str, blocker: str, action: Action, block_action: Action, game_state: Optional[GameState]) -> None:
        print(f"{blocker} blocked {instigator} claiming {block_action}")

    def log_game_state(self, game_state: Optional[GameState]) -> None:
        print("Game State updated")

    def log_winner(self, winner: str) -> None:
        print(f"Winner: {winner}")