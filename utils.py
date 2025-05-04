from character import Character

from enum import Enum, auto
from typing import List, Dict, Optional
from dataclasses import dataclass, field

class Action(Enum):
    INCOME = auto()
    FOREIGN_AID = auto()
    TAX = auto()
    ASSASSINATE = auto()
    STEAL = auto()
    EXCHANGE = auto()
    COUP = auto()
    BLOCK_STEALING = auto()
    BLOCK_ASSASSINATE = auto()
    BLOCK_FOREIGN_AID = auto()
    CALL_BULLSHIT = auto()
    NO_RESPONSE = auto()

@dataclass
class Claim:
    action: Action
    target: Optional[str] = None

@dataclass
class Block:
    claim: Claim
    instigator: str

@dataclass
class PlayerState:
    coins: int = 0
    revealed_characters: List[Character] = field(default_factory=list)
    in_game: bool = False

@dataclass
class GameState:
    current_player: str = ""
    player_states: Dict[str, PlayerState] = field(default_factory=dict)
    turn_count: int = 0
    legal_actions: List[Action] = field(default_factory=list)

    def __str__(self):
        state_lines = [f"Turn: {self.turn_count}", f"Current Player: {self.current_player}", "Player States:"]
        for name, state in self.player_states.items():
            characters = ", ".join([c.name for c in state.revealed_characters]) or "None"
            in_game_status = "Yes" if state.in_game else "No"
            state_lines.append(f"  - {name}: {state.coins} coins, Revealed: [{characters}], In Game: {in_game_status}")
        actions = ", ".join([a.name for a in self.legal_actions]) or "None"
        state_lines.append(f"Legal Actions: {actions}")
        return "\n".join(state_lines)

  