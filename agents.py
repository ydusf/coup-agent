from character import Character
from utils import Action, Claim, GameState

from typing import List, Optional
from collections import defaultdict
from abc import abstractmethod
import random

class Agent:
    def __init__(self):
        pass

    @abstractmethod
    def choose_to_challenge(self, host: str, instigator: str, claim: Claim, game_state: GameState) -> bool:
        pass

    @abstractmethod
    def choose_to_block(self, host: str, legal_responses: List[Action], instigator: str, action: Action, game_state: GameState) -> Claim:
        pass

    @abstractmethod
    def choose_action(self, host: str, legal_actions: List[Action], other_players: List[str], game_state: GameState) -> Claim:
        pass

    @abstractmethod
    def choose_character(self, host: str, characters: List[Character], game_state: GameState) -> str:
        pass

    @abstractmethod
    def exchange_cards(self, host: str, available_characters: List[Character], game_state: GameState) -> List[int]:
        pass

    @abstractmethod
    def update_weights(self, host: str, won: bool, learning_rate: float = 0.1) -> None:
        pass


class RandomAgent(Agent):
    def __init__(self):
        super().__init__()

    def choose_to_challenge(self, host: str, instigator: str, claim: Claim, game_state: GameState) -> bool:
        return random.choice([True, False])
    
    def choose_to_block(self, host: str, legal_responses: List[Action], instigator: str, action: Action, game_state: GameState) -> Claim:
        is_blocking: bool = random.choice([True, False])
        if is_blocking:
            response: Action = random.choice(legal_responses)
            return Claim(action=response, target=instigator)

        return Claim(action=Action.NO_RESPONSE, target=None)


    def choose_action(self, host: str, legal_actions: List[Action], other_players: List[str], game_state: GameState) -> Claim:
        action: Action = random.choice(legal_actions)
        target: Optional[str] = None
        if action in (Action.STEAL, Action.ASSASSINATE, Action.COUP):
            target = random.choice(other_players)

        return Claim(action=action, target=target)
    
    def choose_character(self, host: str, characters: List[Character], game_state: GameState) -> str:
        return random.choice(characters).name
    
    def exchange_cards(self, host: str, available_characters: List[Character], game_state: GameState) -> List[int]:
        characters_to_put_back: List[int] = []    
        num_cards_to_put_back = len(available_characters) // 2
        for _ in range(num_cards_to_put_back):
            character_idx = random.randint(0, len(available_characters)-1)
            available_characters.pop(character_idx)
            characters_to_put_back.append(character_idx)

        return characters_to_put_back
    
    def update_weights(self, host: str, won: bool, learning_rate: float = 0.1) -> None:
        pass # do nothing as we do not learn


class LearningAgent(Agent):
    def __init__(self):
        super().__init__()

    def choose_to_challenge(self, host: str, instigator: str, claim: Claim, game_state: GameState) -> bool:
        pass

    def choose_to_block(self, host: str, legal_responses: List[Action], instigator: str, action: Action, game_state: GameState) -> Claim:
        pass

    def choose_action(self, host: str, legal_actions: List[Action], other_players: List[str], game_state: GameState) -> Claim:
        pass

    def choose_character(self, host: str, characters: List[Character], game_state: GameState) -> str:
        pass

    def exchange_cards(self, host: str, available_characters: List[Character], game_state: GameState) -> List[int]:
        pass

    def update_weights(self, host: str, won: bool, learning_rate: float = 0.1) -> None:
        pass