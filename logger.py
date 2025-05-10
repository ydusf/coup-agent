from utils import LogEntry, ActionState, GameState, Claim, Action

from typing import List, Optional

class Logger:
    def __init__(self):
        self._log_entries: List[LogEntry] = []

    def log_turn_start(self, turn: int, player_name: str, game_state: GameState) -> None:
        print(f"{player_name}'s turn")

    def log_action(self, turn: int, instigator: str, action: Action, target: Optional[str], game_state: GameState) -> None:
        if target is not None:
            print(f"{instigator} claimed {action} against {target}")
        else:
            print(f"{instigator} claimed {action}")

    def log_challenge(self, turn: int, instigator: str, challenger: str, action: Action, success: bool, game_state: GameState) -> None:
        if success:
            print(f"{challenger} successfully challenged {instigator} who claimed {action}")
        else:
            print(f"{challenger} failed a challenged against {instigator} who claimed {action}")

    def log_block(self, turn: int, instigator: str, blocker: str, action: Action, block_action: Action, game_state: GameState) -> None:
        print(f"{blocker} blocked {instigator} claiming {block_action}")

    def log_game_state(self, game_state: GameState) -> None:
        print("Game State updated")

    def log_winner(self, winner: str) -> None:
        print(f"Winner: {winner}")

    def save_to_file(self, path: str) -> None:
        with open(path, "w") as f:
            for entry in self._log_entries:
                f.write(str(entry) + "\n")