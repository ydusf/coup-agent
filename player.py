from __future__ import annotations

from utils import Action, Claim, Block, PlayerPerspective, Character
from agents import Agent

import random
from typing import List, Optional

class Player:
    def __init__(self, name: str, agent: Agent):
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
    
    @coins.setter
    def coins(self, value: int) -> None:        
        if value < 0:
            raise ValueError("value must be greater than 0")
        
        self._coins = value

    def ask_to_challenge(self, instigator: str, claim: Claim, player_perspective: PlayerPerspective) -> bool:
        challenged: bool = self._agent.choose_to_challenge(instigator, claim, player_perspective)
        return challenged
    
    def ask_to_block(self, instigator: str, action: Action, player_perspective: PlayerPerspective) -> Optional[Block]:
        legal_responses: List[Claim] = [Claim(Action.NO_RESPONSE, None)]

        if action == Action.STEAL:
            legal_responses.append(Claim(Action.BLOCK_STEALING, instigator))
        elif action == Action.ASSASSINATE:
            legal_responses.append(Claim(Action.BLOCK_ASSASSINATE, instigator))
        elif action == Action.FOREIGN_AID:
            legal_responses.append(Claim(Action.BLOCK_FOREIGN_AID, instigator))

        claim: Claim = self._agent.choose_to_block(legal_responses, action, player_perspective)
        assert claim in legal_responses

        if claim.action != Action.NO_RESPONSE:
            return Block(claim=claim, instigator=self.name)
        
        return None
    
    def ask_for_action(self, other_players: List[str], player_perspective: PlayerPerspective) -> Claim:
        legal_claims: List[Claim] = [Claim(Action.INCOME, None), 
                                     Claim(Action.FOREIGN_AID, None), 
                                     Claim(Action.TAX, None), 
                                     Claim(Action.EXCHANGE, None)]
        
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
        assert claim in legal_claims

        return claim

    def has_character(self, character: Character) -> bool:
        return character in self.characters

    def add_character(self, character: Character) -> None:
        self.characters.append(character)
    
    def remove_character(self, player_perspective: PlayerPerspective) -> None:
        if len(self.characters) <= 0:
            return

        character: Character = self._agent.choose_character(self.characters.copy(), player_perspective)
        
        for card_idx in range(len(self.characters)):
            if self.characters[card_idx] == character:
                self._revealed_characters.append(self.characters[card_idx])
                self.characters.pop(card_idx)
                return
            
        assert False # the character removed must exist

    def exchange_cards(self, num_cards_to_exchange: int, player_perspective: PlayerPerspective) -> List[Character]:
        legal_exchanges: List[Character] = self.characters.copy()
        
        characters_to_exchange: List[Character] = self._agent.exchange_cards(num_cards_to_exchange, legal_exchanges, player_perspective)
        assert len(characters_to_exchange) == num_cards_to_exchange
        
        characters_to_put_back: List[Character] = []
        for i, hidden_character in enumerate(self.characters):
            for j, exchanged_character in enumerate(characters_to_exchange):
                if exchanged_character == hidden_character:
                    characters_to_put_back.append(exchanged_character)
                    characters_to_exchange.pop(j)
                    self.characters.pop(i)
            
        return characters_to_put_back
    
    def propogate_reward(self, reward: float, next_player_perspective: PlayerPerspective) -> None:
        self._agent.propogate_reward(reward, next_player_perspective)

        
