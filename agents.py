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
    def choose_to_block(self, legal_responses: List[Claim], action: Action, game_state: GameState) -> Claim:
        pass

    @abstractmethod
    def choose_action(self, legal_claims: List[Claim], game_state: GameState) -> Claim:
        pass

    @abstractmethod
    def choose_character(self, characters: List[Character], game_state: GameState) -> str:
        pass

    @abstractmethod
    def exchange_cards(self, num_cards_to_exchange: int, available_characters: List[str], game_state: GameState) -> List[int]:
        pass

    def propogate_reward(self, reward: float) -> None:
        self._total_reward += reward


class RandomAgent(Agent):
    def __init__(self, host: str):
        super().__init__(host)

    def choose_to_challenge(self, instigator: str, claim: Claim, game_state: GameState) -> bool:
        return random.choice([True, False])
    
    def choose_to_block(self, legal_responses: List[Claim], action: Action, game_state: GameState) -> Claim:
        return random.choice(legal_responses)
            
    def choose_action(self, legal_claims: List[Claim], game_state: GameState) -> Claim:
        return random.choice(legal_claims)
    
    def choose_character(self, characters: List[Character], game_state: GameState) -> str:
        return random.choice(characters).name
    
    def exchange_cards(self, num_cards_to_exchange: int, available_characters: List[str], game_state: GameState) -> List[str]:
        assert num_cards_to_exchange <= len(available_characters)    
        return random.sample(available_characters, num_cards_to_exchange)
        
class RuleBasedAgent(Agent):
    def __init__(self, host: str):
        super().__init__(host)

    def choose_to_challenge(self, instigator: str, claim: Claim, game_state: GameState) -> bool:
        return random.choice([True, False])
    
    def choose_to_block(self, legal_responses: List[Claim], action: Action, game_state: GameState) -> Claim:
        return random.choice(legal_responses)

    def choose_action(self, legal_claims: List[Claim], game_state: GameState) -> Claim:
        high_priority_players: List[str] = []
        for name, state in game_state.player_states.items():
            if state.in_game == False:
                continue

            if len(state.revealed_characters) == 0 and state.coins >= 5:
                high_priority_players.append(name)

        coup_claims: List[Claim] = [claim for claim in legal_claims if claim.action == Action.COUP]
        for claim in coup_claims:
            if claim.target in high_priority_players:
                return claim
            
        assassinate_claims: List[Claim] = [claim for claim in legal_claims if claim.action == Action.ASSASSINATE]
        for claim in assassinate_claims:
            if claim.target in high_priority_players:
                return claim

        steal_claims: List[Claim] = [claim for claim in legal_claims if claim.action == Action.STEAL]
        for claim in steal_claims:
            if claim.target in high_priority_players:
                return claim
                
        return random.choice(legal_claims)
    
    def choose_character(self, characters: List[Character], game_state: GameState) -> str:
        return random.choice(characters).name
    
    def exchange_cards(self, num_cards_to_exchange: int, available_characters: List[str], game_state: GameState) -> List[int]:
        assert num_cards_to_exchange <= len(available_characters)    
        return random.sample(available_characters, num_cards_to_exchange)

class LearningAgent(Agent):
    def __init__(self, host: str):
        super().__init__(host)

    def choose_to_challenge(self, instigator: str, claim: Claim, game_state: GameState) -> bool:
        pass

    def choose_to_block(self, legal_responses: List[Claim], action: Action, game_state: GameState) -> Claim:
        pass

    def choose_action(self, legal_claims: List[Claim], game_state: GameState) -> Claim:
        pass

    def choose_character(self, characters: List[Character], game_state: GameState) -> str:
        pass

    def exchange_cards(self, num_cards_to_exchange: int, available_characters: List[str], game_state: GameState) -> List[int]:
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