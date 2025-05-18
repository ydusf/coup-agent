from __future__ import annotations

from utils import Action, Claim, Block, PlayerPerspective, Character
from agents import Agent

from typing import List, Optional


class Player:
    def __init__(self, name: str, agent: Agent) -> None:
        self._coins: int = 0
        self._name: str = name
        self._characters: List[Character] = []
        self._revealed_characters: List[Character] = []
        self._log: dict = {}
        self._agent: Agent = agent

    @property
    def name(self) -> str:
        return self._name

    @property
    def coins(self) -> int:
        return self._coins

    @property
    def characters(self) -> List[Character]:
        return self._characters

    @property
    def revealed_characters(self) -> List[Character]:
        return self._revealed_characters

    def add_coins(self, value: int) -> None:
        self._coins = value

    def reset(self) -> None:
        self._coins = 0
        self._characters.clear()
        self._revealed_characters.clear()
        self._log.clear()

    def ask_to_challenge(self, instigator: str, claim: Claim, player_perspective: Optional[PlayerPerspective]) -> bool:
        challenged: bool = self._agent.choose_to_challenge(instigator, claim, player_perspective)
        return challenged

    def ask_to_block(self, instigator: str, action: Action, player_perspective: Optional[PlayerPerspective]) -> Optional[Block]:
        legal_responses: List[Claim] = [Claim(Action.NO_RESPONSE, None)]

        if action == Action.STEAL:
            legal_responses.append(Claim(Action.BLOCK_STEALING, instigator))
        elif action == Action.ASSASSINATE:
            legal_responses.append(Claim(Action.BLOCK_ASSASSINATE, instigator))
        elif action == Action.FOREIGN_AID:
            legal_responses.append(Claim(Action.BLOCK_FOREIGN_AID, instigator))

        claim: Optional[Claim] = self._agent.choose_to_block(legal_responses, action, player_perspective)
        assert claim is not None and claim in legal_responses

        if claim.action != Action.NO_RESPONSE:
            return Block(claim=claim, instigator=self.name)

        return None

    def ask_for_action(self, other_players: List[str], player_perspective: Optional[PlayerPerspective]) -> Claim:
        legal_claims: List[Claim] = [
            Claim(Action.INCOME, None),
            Claim(Action.FOREIGN_AID, None),
            Claim(Action.TAX, None),
            Claim(Action.EXCHANGE, None),
        ]

        for player_name in other_players:
            legal_claims.append(Claim(Action.STEAL, player_name))

        if self.coins >= 3:
            for player_name in other_players:
                legal_claims.append(Claim(Action.ASSASSINATE, player_name))

        if self.coins >= 7:
            for player_name in other_players:
                legal_claims.append(Claim(Action.COUP, player_name))

        if self.coins >= 10:
            legal_claims.clear()
            for player_name in other_players:
                legal_claims.append(Claim(Action.COUP, player_name))

        claim: Claim = self._agent.choose_action(legal_claims, player_perspective)

        if claim not in legal_claims:
            raise ValueError(f"{claim} not in {legal_claims}")

        return claim

    def has_character(self, character: Character) -> bool:
        return character in self.characters

    def add_character(self, character: Character) -> None:
        self.characters.append(character)

    def remove_character(self, player_perspective: Optional[PlayerPerspective]) -> None:
        if len(self.characters) <= 0:
            return

        character = self._agent.choose_character(self.characters.copy(), player_perspective)
        if character in self.characters:
            self._characters.remove(character)
            self._revealed_characters.append(character)
        else:
            raise AssertionError("The selected character does not exist in the player's hand.")

    def exchange_cards(self, num_cards_to_exchange: int, player_perspective: Optional[PlayerPerspective]) -> List[Character]:
        legal_exchanges = self.characters.copy()
        characters_to_exchange = self._agent.exchange_cards(num_cards_to_exchange, legal_exchanges, player_perspective)

        assert len(characters_to_exchange) == num_cards_to_exchange

        characters_to_put_back = []
        for character in characters_to_exchange:
            if character in self._characters:
                self._characters.remove(character)
                characters_to_put_back.append(character)
            else:
                raise AssertionError("Attempted to exchange a character not in hand.")

        return characters_to_put_back

    def propogate_reward(self, reward: float, next_player_perspective: Optional[PlayerPerspective]) -> None:
        self._agent.propogate_reward(reward, next_player_perspective)
