from utils import Action, Claim, Character, PlayerPerspective, GameState

from typing import List, Optional, Dict, Tuple 
from abc import abstractmethod
import random
import numpy as np
from collections import defaultdict, Counter

class Agent:
    def __init__(self):
        self._total_reward = 0.0

    @abstractmethod
    def choose_to_challenge(self, instigator: str, claim: Claim, player_perspective: PlayerPerspective) -> bool:
        pass

    @abstractmethod
    def choose_to_block(self, legal_responses: List[Claim], action: Action, player_perspective: PlayerPerspective) -> Optional[Claim]: # Changed return type
        pass

    @abstractmethod
    def choose_action(self, legal_claims: List[Claim], player_perspective: PlayerPerspective) -> Claim:
        pass

    @abstractmethod
    def choose_character(self, characters: List[Character], player_perspective: PlayerPerspective) -> Character: # To reveal when losing influence
        pass

    @abstractmethod
    def exchange_cards(self, num_cards_to_exchange: int, available_characters: List[Character], player_perspective: PlayerPerspective) -> List[Character]: 
        pass

    def propogate_reward(self, reward: float, next_player_perspective: PlayerPerspective) -> None:
        self._total_reward += reward

class HumanInputAgent(Agent):
    def __init__(self):
        super().__init__()

    def display_perspective(self, perspective: PlayerPerspective):
        print("\n" + "=" * 50)
        print(f"Your Name: {perspective.name}")
        print(f"Your Hidden Characters: {perspective.hidden_characters}")
        print("\nGame State:\n" + str(perspective.game_state))
        print("=" * 50 + "\n")

    def choose_to_challenge(self, instigator: str, claim: Claim, player_perspective: PlayerPerspective) -> bool:
        self.display_perspective(player_perspective)
        print(f"{instigator} is claiming: {claim}")
        choice = input("Do you want to challenge this claim? (y/n): ").strip().lower()
        return choice == 'y'

    def choose_to_block(self, legal_responses: List[Claim], action: Action, player_perspective: PlayerPerspective) -> Optional[Claim]:
        self.display_perspective(player_perspective)
        print(f"Action against you: {action}")
        if not legal_responses:
            print("You have no legal blocks.")
            return None
        print("Available blocks:")
        for i, claim in enumerate(legal_responses):
            print(f"  [{i}] {claim}")
        choice = input("Choose block index (or press enter to not block): ").strip()
        if choice == "":
            return None
        return legal_responses[int(choice)]

    def choose_action(self, legal_claims: List[Claim], player_perspective: PlayerPerspective) -> Claim:
        self.display_perspective(player_perspective)
        print("Your turn. Legal actions:")
        for i, claim in enumerate(legal_claims):
            print(f"  [{i}] {claim}")
        choice = int(input("Choose action index: ").strip())
        return legal_claims[choice]

    def choose_character(self, characters: List[Character], player_perspective: PlayerPerspective) -> Character:
        self.display_perspective(player_perspective)
        print("Choose a character to lose:")
        for i, character in enumerate(characters):
            print(f"  [{i}] {character}")
        choice = int(input("Choose character index: ").strip())
        return characters[choice]

    def exchange_cards(self, num_cards_to_exchange: int, available_characters: List[Character], player_perspective: PlayerPerspective) -> List[Character]:
        self.display_perspective(player_perspective)
        print(f"Exchange {num_cards_to_exchange} card(s). Available cards: {available_characters}")
        chosen = []
        for i in range(num_cards_to_exchange):
            print(f"Select card {i+1}:")
            for j, char in enumerate(available_characters):
                print(f"  [{j}] {char}")
            idx = int(input("Choose index: ").strip())
            chosen.append(available_characters.pop(idx))
        return chosen

class RandomAgent(Agent):
    def __init__(self):
        super().__init__()

    def choose_to_challenge(self, instigator: str, claim: Claim, player_perspective: PlayerPerspective) -> bool:
        return random.choice([True, False])
    
    def choose_to_block(self, legal_responses: List[Claim], action: Action, player_perspective: PlayerPerspective) -> Optional[Claim]:
        if not legal_responses:
            return None # Cannot block if there are no legal responses
        return random.choice(legal_responses)
            
    def choose_action(self, legal_claims: List[Claim], player_perspective: PlayerPerspective) -> Claim:
        return random.choice(legal_claims)
    
    def choose_character(self, characters: List[Character], player_perspective: PlayerPerspective) -> Character:
        return random.choice(characters)
    
    def exchange_cards(self, num_cards_to_exchange: int, available_characters: List[Character], player_perspective: PlayerPerspective) -> List[Character]:
        return random.sample(available_characters, num_cards_to_exchange)
        
class RuleBasedAgent(Agent):
    def __init__(self):
        super().__init__()

    def choose_to_challenge(self, instigator: str, claim: Claim, player_perspective: PlayerPerspective) -> bool:
        return random.choice([True, False])
    
    def choose_to_block(self, legal_responses: List[Claim], action: Action, player_perspective: PlayerPerspective) -> Optional[Claim]:
        if not legal_responses:
            return None
        return random.choice(legal_responses)

    def choose_action(self, legal_claims: List[Claim], player_perspective: PlayerPerspective) -> Claim:
        game_state: GameState = player_perspective.game_state
        most_coins: int = 0
        least_revealed_cards: int = 0

        influentual_player: str = None
        richest_player: str = None

        for name, player_state in game_state.player_states.items():
            if name == player_perspective.name:
                continue

            if player_state.coins > most_coins:
                most_coins = player_state.coins
                richest_player = name

            if len(player_state.revealed_characters) < least_revealed_cards:
                least_revealed_cards = len(player_state.revealed_characters)
                influentual_player = name

        players_to_coup: List[str] = [claim.target for claim in legal_claims if claim.action == Action.COUP]
        players_to_assassinate: List[str] = [claim.target for claim in legal_claims if claim.action == Action.ASSASSINATE]

        if richest_player in players_to_coup:
            return Claim(Action.COUP, richest_player)
        elif influentual_player in players_to_coup:
            return Claim(Action.COUP, influentual_player)
        elif Character.DUKE in player_perspective.hidden_characters:
            return Claim(Action.TAX, None)
        elif Character.CAPTAIN in player_perspective.hidden_characters:
            return Claim(Action.STEAL, richest_player)
        elif Character.ASSASSIN in player_perspective.hidden_characters:
            if influentual_player in players_to_assassinate:
                return Claim(Action.ASSASSINATE, influentual_player)
            elif richest_player in players_to_assassinate:
                return Claim(Action.ASSASSINATE, richest_player)
    
        return random.choice(legal_claims) # backup incase heuristic falls flat
    
    def choose_character(self, characters: List[Character], player_perspective: PlayerPerspective) -> Character:
        return random.choice(characters)
    
    def exchange_cards(self, num_cards_to_exchange: int, available_characters: List[Character], player_perspective: PlayerPerspective) -> List[Character]:
        return random.sample(available_characters, num_cards_to_exchange)
    
class LearningAgent(Agent):
    def __init__(self):
        super().__init__()

    def choose_to_challenge(self, instigator: str, claim: Claim, player_perspective: PlayerPerspective) -> bool:
        return random.choice([True, False])
    
    def choose_to_block(self, legal_responses: List[Claim], action: Action, player_perspective: PlayerPerspective) -> Optional[Claim]:
        if not legal_responses:
            return None # Cannot block if there are no legal responses
        return random.choice(legal_responses)
            
    def choose_action(self, legal_claims: List[Claim], player_perspective: PlayerPerspective) -> Claim:
        return random.choice(legal_claims)
    
    def choose_character(self, characters: List[Character], player_perspective: PlayerPerspective) -> Character:
        return random.choice(characters)
    
    def exchange_cards(self, num_cards_to_exchange: int, available_characters: List[Character], player_perspective: PlayerPerspective) -> List[Character]:
        return random.sample(available_characters, num_cards_to_exchange)