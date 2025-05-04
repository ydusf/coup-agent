from character import Character
from utils import Action, Claim, GameState
from abc import abstractmethod

from typing import List, Optional
import random

class Agent:
    def __init__(self):
        pass

    @abstractmethod
    def choose_to_challenge(self, instigator: str, claim: Claim, game_state: GameState) -> bool:
        pass

    @abstractmethod
    def choose_to_block(self, legal_responses: List[Action], instigator: str, action: Action, game_state: GameState) -> Claim:
        pass

    @abstractmethod
    def choose_action(self, legal_actions: List[Action], other_players: List[str], game_state: GameState) -> Claim:
        pass

    @abstractmethod
    def choose_character(self, characters: List[Character], game_state: GameState) -> str:
        pass

    @abstractmethod
    def exchange_cards(self, available_characters: List[Character], game_state: GameState) -> List[int]:
        pass


class RandomAgent(Agent):
    def __init__(self):
        super().__init__()

    def choose_to_challenge(self, instigator: str, claim: Claim, game_state: GameState) -> bool:
        return random.choice([True, False])
    
    def choose_to_block(self, legal_responses: List[Action], instigator: str, action: Action, game_state: GameState) -> Claim:
        is_blocking: bool = random.choice([True, False])
        if is_blocking:
            response: Action = random.choice(legal_responses)
            return Claim(action=response, target=instigator)

        return Claim(action=Action.NO_RESPONSE, target=None)


    def choose_action(self, legal_actions: List[Action], other_players: List[str], game_state: GameState) -> Claim:
        action: Action = random.choice(legal_actions)
        target: Optional[str] = None
        if action in (Action.STEAL, Action.ASSASSINATE, Action.COUP):
            target = random.choice(other_players)

        return Claim(action=action, target=target)
    
    def choose_character(self, characters: List[Character], game_state: GameState) -> str:
        return random.choice(characters).name
    
    def exchange_cards(self, available_characters: List[Character], game_state: GameState) -> List[int]:
        characters_to_put_back: List[int] = []    
        num_cards_to_put_back = len(available_characters) // 2
        for _ in range(num_cards_to_put_back):
            character_idx = random.randint(0, len(available_characters)-1)
            available_characters.pop(character_idx)
            characters_to_put_back.append(character_idx)

        return characters_to_put_back