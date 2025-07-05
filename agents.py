from utils import Action, Claim, Character, PlayerPerspective, GameState

from typing import List, Optional, Tuple
from abc import abstractmethod
import random

class Agent:
    def __init__(self) -> None:
        self._total_reward = 0.0
        self._trajectory: List[Tuple[Claim, List[Claim], PlayerPerspective]] = []

    @abstractmethod
    def choose_to_challenge(self, instigator: str, claim: Claim, player_perspective: Optional[PlayerPerspective]) -> bool:
        pass

    @abstractmethod
    def choose_to_block(self, legal_responses: List[Claim], action: Action, player_perspective: Optional[PlayerPerspective]) -> Optional[Claim]: # Changed return type
        pass

    @abstractmethod
    def choose_action(self, legal_claims: List[Claim], player_perspective: Optional[PlayerPerspective]) -> Claim:
        pass

    @abstractmethod
    def choose_character(self, characters: List[Character], player_perspective: Optional[PlayerPerspective]) -> Character: # To reveal when losing influence
        pass

    @abstractmethod
    def exchange_cards(self, num_cards_to_exchange: int, available_characters: List[Character], player_perspective: Optional[PlayerPerspective]) -> List[Character]:
        pass

    def propogate_reward(self, reward: float) -> None:
        self._total_reward += reward

    def extend_trajectory(self, claim: Claim, legal_claims: List[Claim], player_perspective: Optional[PlayerPerspective]) -> None:
        assert player_perspective is not None

        self._trajectory.append((claim, legal_claims, player_perspective))

    def get_trajectory(self):
        return self._trajectory

    def reset_agent(self):
        self._total_reward = 0
        self._trajectory = []

class HumanInputAgent(Agent):
    def __init__(self):
        super().__init__()

    def display_perspective(self, perspective: Optional[PlayerPerspective]):
        if perspective is None:
            raise ValueError("Why is the player perspective None")

        print("\n" + "=" * 50)
        print(f"Your Name: {perspective.name}")
        print(f"Your Hidden Characters: {perspective.hidden_characters}")
        print("\nGame State:\n" + str(perspective.game_state))
        print("=" * 50 + "\n")

    def choose_to_challenge(self, instigator: str, claim: Claim, player_perspective: Optional[PlayerPerspective]) -> bool:
        if player_perspective is None:
            raise ValueError("Why is the player perspective None")

        self.display_perspective(player_perspective)
        print(f"{instigator} is claiming: {claim}")
        choice = input("Do you want to challenge this claim? (y/n): ").strip().lower()
        return choice == 'y'

    def choose_to_block(self, legal_responses: List[Claim], action: Action, player_perspective: Optional[PlayerPerspective]) -> Optional[Claim]:
        if player_perspective is None:
            raise ValueError("Why is the player perspective None")

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

    def choose_action(self, legal_claims: List[Claim], player_perspective: Optional[PlayerPerspective]) -> Claim:
        if player_perspective is None:
            raise ValueError("Why is the player perspective None")

        self.display_perspective(player_perspective)
        print("Your turn. Legal actions:")
        for i, claim in enumerate(legal_claims):
            print(f"  [{i}] {claim}")
        choice = int(input("Choose action index: ").strip())
        return legal_claims[choice]

    def choose_character(self, characters: List[Character], player_perspective: Optional[PlayerPerspective]) -> Character:
        if player_perspective is None:
            raise ValueError("Why is the player perspective None")

        self.display_perspective(player_perspective)
        print("Choose a character to lose:")
        for i, character in enumerate(characters):
            print(f"  [{i}] {character}")
        choice = int(input("Choose character index: ").strip())
        return characters[choice]

    def exchange_cards(self, num_cards_to_exchange: int, available_characters: List[Character], player_perspective: Optional[PlayerPerspective]) -> List[Character]:
        if player_perspective is None:
            raise ValueError("Why is the player perspective None")

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

    def choose_to_challenge(self, instigator: str, claim: Claim, player_perspective: Optional[PlayerPerspective]) -> bool:
        if player_perspective is None:
            raise ValueError("Why is the player perspective None")

        return random.choice([True, False])

    def choose_to_block(self, legal_responses: List[Claim], action: Action, player_perspective: Optional[PlayerPerspective]) -> Optional[Claim]:
        if player_perspective is None:
            raise ValueError("Why is the player perspective None")

        if not legal_responses:
            return None # Cannot block if there are no legal responses
        return random.choice(legal_responses)

    def choose_action(self, legal_claims: List[Claim], player_perspective: Optional[PlayerPerspective]) -> Claim:
        if player_perspective is None:
            raise ValueError("Why is the player perspective None")

        return random.choice(legal_claims)

    def choose_character(self, characters: List[Character], player_perspective: Optional[PlayerPerspective]) -> Character:
        if player_perspective is None:
            raise ValueError("Why is the player perspective None")

        return random.choice(characters)

    def exchange_cards(self, num_cards_to_exchange: int, available_characters: List[Character], player_perspective: Optional[PlayerPerspective]) -> List[Character]:
        if player_perspective is None:
            raise ValueError("Why is the player perspective None")

        return random.sample(available_characters, num_cards_to_exchange)

class RuleBasedAgent(Agent):
    def __init__(self):
        super().__init__()

    def choose_to_challenge(self, instigator: str, claim: Claim, player_perspective: Optional[PlayerPerspective]) -> bool:
        if player_perspective is None:
            raise ValueError("Why is the player perspective None")

        return random.choice([True, False])

    def choose_to_block(self, legal_responses: List[Claim], action: Action, player_perspective: Optional[PlayerPerspective]) -> Optional[Claim]:
        if player_perspective is None:
            raise ValueError("Why is the player perspective None")

        if not legal_responses:
            return None
        return random.choice(legal_responses)

    def choose_action(self, legal_claims: List[Claim], player_perspective: Optional[PlayerPerspective]) -> Claim:
        if player_perspective is None:
            raise ValueError("Why is the player perspective None")

        game_state: GameState = player_perspective.game_state
        most_coins: int = 0
        least_revealed_cards: int = 0

        influentual_player: Optional[str] = None
        richest_player: Optional[str] = None

        for name, player_state in game_state.player_states.items():
            if name == player_perspective.name:
                continue

            if player_state.coins > most_coins:
                most_coins = player_state.coins
                richest_player = name

            if len(player_state.revealed_characters) < least_revealed_cards:
                least_revealed_cards = len(player_state.revealed_characters)
                influentual_player = name

        players_to_coup: List[str] = [claim.target for claim in legal_claims if claim.action == Action.COUP and claim.target is not None]
        players_to_assassinate: List[str] = [claim.target for claim in legal_claims if claim.action == Action.ASSASSINATE and claim.target is not None]

        if richest_player in players_to_coup:
            return Claim(Action.COUP, richest_player)
        elif influentual_player in players_to_coup:
            return Claim(Action.COUP, influentual_player)
        elif Character.DUKE in player_perspective.hidden_characters and Claim(Action.TAX, None) in legal_claims:
            return Claim(Action.TAX, None)
        elif Character.CAPTAIN in player_perspective.hidden_characters and Claim(Action.STEAL, richest_player) in legal_claims:
            return Claim(Action.STEAL, richest_player)
        elif Character.ASSASSIN in player_perspective.hidden_characters:
            if influentual_player in players_to_assassinate:
                return Claim(Action.ASSASSINATE, influentual_player)
            elif richest_player in players_to_assassinate:
                return Claim(Action.ASSASSINATE, richest_player)

        return random.choice(legal_claims) # backup incase heuristic falls flat

    def choose_character(self, characters: List[Character], player_perspective: Optional[PlayerPerspective]) -> Character:
        if player_perspective is None:
            raise ValueError("Why is the player perspective None")

        return random.choice(characters)

    def exchange_cards(self, num_cards_to_exchange: int, available_characters: List[Character], player_perspective: Optional[PlayerPerspective]) -> List[Character]:
        if player_perspective is None:
            raise ValueError("Why is the player perspective None")

        return random.sample(available_characters, num_cards_to_exchange)