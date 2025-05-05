from character import Character
from utils import Action, Claim, GameState, PlayerState

from typing import List, Optional
from abc import abstractmethod
import random

class Agent:
    def __init__(self, host: str):
        self._host = host
        self._total_reward = 0.0

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
    def exchange_cards(self, num_cards_to_exchange: int, available_characters: List[Character], game_state: GameState) -> List[int]:
        pass

    def propogate_reward(self, reward: float) -> None:
        self._total_reward += reward


class RandomAgent(Agent):
    def __init__(self, host: str):
        super().__init__(host)

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
    
    def exchange_cards(self, num_cards_to_exchange: int, available_characters: List[Character], game_state: GameState) -> List[int]:
        characters_to_put_back: List[int] = []    
        for _ in range(num_cards_to_exchange):
            character_idx = random.randint(0, len(available_characters)-1)
            available_characters.pop(character_idx)
            characters_to_put_back.append(character_idx)

        return characters_to_put_back

class RuleBasedAgent(Agent):
    def __init__(self, host: str):
        super().__init__(host)

    def choose_to_challenge(self, instigator: str, claim: Claim, game_state: GameState) -> bool:
        return random.choice([True, False])
    
    def choose_to_block(self, legal_responses: List[Action], instigator: str, action: Action, game_state: GameState) -> Claim:
        is_blocking: bool = random.choice([True, False])
        if is_blocking:
            response: Action = random.choice(legal_responses)
            return Claim(action=response, target=instigator)

        return Claim(action=Action.NO_RESPONSE, target=None)

    def choose_action(self, legal_actions: List[Action], other_players: List[str], game_state: GameState) -> Claim:
        if Action.COUP in legal_actions:
            high_priority_players: List[str] = []
            for player_name in other_players:
                player_state: PlayerState = game_state.player_states[player_name]
                if len(player_state.revealed_characters) == 0:
                    high_priority_players.append(player_name)
                elif player_state.coins >= 5:
                    high_priority_players.append(player_name)

            if len(high_priority_players) > 0:
                return Claim(action=Action.COUP, target=random.choice(high_priority_players))
            else:
                return Claim(action=Action.COUP, target=random.choice(other_players))
        else:
            action: Action = random.choice(legal_actions)
            target: Optional[str] = None
            if action in (Action.STEAL, Action.ASSASSINATE, Action.COUP):
                target = random.choice(other_players)

            return Claim(action=action, target=target)
    
    def choose_character(self, characters: List[Character], game_state: GameState) -> str:
        return random.choice(characters).name
    
    def exchange_cards(self, num_cards_to_exchange: int, available_characters: List[Character], game_state: GameState) -> List[int]:
        characters_to_put_back: List[int] = []    
        for _ in range(num_cards_to_exchange):
            character_idx = random.randint(0, len(available_characters)-1)
            available_characters.pop(character_idx)
            characters_to_put_back.append(character_idx)

        return characters_to_put_back

class LearningAgent(Agent):
    def __init__(self, host: str):
        super().__init__(host)

    def choose_to_challenge(self, instigator: str, claim: Claim, game_state: GameState) -> bool:
        pass

    def choose_to_block(self, legal_responses: List[Action], instigator: str, action: Action, game_state: GameState) -> Claim:
        pass

    def choose_action(self, legal_actions: List[Action], other_players: List[str], game_state: GameState) -> Claim:
        pass

    def choose_character(self, characters: List[Character], game_state: GameState) -> str:
        pass

    def exchange_cards(self, num_cards_to_exchange: int, available_characters: List[Character], game_state: GameState) -> List[int]:
        pass





# plan is to build an agent with this reward system:
    
# +1 for every influence someone else lost
# -1 for every influence you lost
# +0.1 for every coin gained
# -0.1 for every coin lost
# +0.2 for every coin someone else lost
# +0.5 for every new card seen
# -5 for losing
# +5 for winning