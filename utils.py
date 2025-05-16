from enum import Enum, auto
from typing import List, Dict, Optional
from dataclasses import dataclass, field

# character            active                passive
# ambassador  |  exchange characters |  block stealing
# contessa    |  blocks assassinate  |       none
# captain     |     steal 2 coins    |  block stealing
# duke        |     take 3 coins     |  block foreign aid  
# assassin    | pay 3 to assassinate |        none
class Character(Enum):
    AMBASSADOR = auto()
    CONTESSA = auto()
    CAPTAIN = auto()
    DUKE = auto()
    ASSASSIN = auto()

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
    turn_count: int = 0
    current_player: str = ""
    num_players_alive: int = 0
    turn_order: List[str] = field(default_factory=list)
    player_states: Dict[str, PlayerState] = field(default_factory=dict)
    history: List[str] = field(default_factory=list)
    revealed_characters: List[Character] = field(default_factory=list)

    def __str__(self):
        state_lines = [
            f"Turn: {self.turn_count}",
            f"Current Player: {self.current_player}",
            f"Players Alive: {self.num_players_alive} / {len(self.player_states)}",
            "Turn Order: " + " -> ".join(self.turn_order),
            "Player States:"
        ]
        for name, state in self.player_states.items():
            characters = ", ".join(c.name for c in state.revealed_characters) or "None"
            in_game_status = "Yes" if state.in_game else "No"
            state_lines.append(f"  {name}: {state.coins} coins, Revealed: [{characters}], In Game: {in_game_status}")

        revealed_characters = ", ".join(c.name for c in self.revealed_characters) or "None"
        state_lines.append(f"Revealed Characters: [{revealed_characters}]")
        return "\n".join(state_lines)

@dataclass
class PlayerPerspective:
    game_state: GameState
    name: str
    hidden_characters: List[str]
    
@dataclass
class ActionState:
    instigator: str
    action: Action
    target: Optional[str]
    target_coins_before: int
    target_coins_after: int
    target_revealed_characters_before: List[str]
    target_revealed_characters_after: List[str]

@dataclass
class LogEntry:
    turn: int
    action_state: ActionState
    game_state: GameState
  