from __future__ import annotations

from character import Character
from utils import Action, Claim, Block, GameState
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

    def ask_to_challenge(self, instigator: str, claim: Claim, game_state: GameState) -> bool:
        challenged: bool = self._agent.choose_to_challenge(instigator, claim, game_state)
        return challenged
    
    def ask_to_block(self, instigator: str, action: Action, game_state: GameState) -> Optional[Block]:
        legal_responses: List[Claim] = [Claim(Action.NO_RESPONSE, None)]

        if action == Action.STEAL:
            legal_responses.append(Claim(Action.BLOCK_STEALING, instigator))
        elif action == Action.ASSASSINATE:
            legal_responses.append(Claim(Action.BLOCK_ASSASSINATE, instigator))
        elif action == Action.FOREIGN_AID:
            legal_responses.append(Claim(Action.BLOCK_FOREIGN_AID, instigator))

        claim: Claim = self._agent.choose_to_block(legal_responses, action, game_state)
        if claim.action != Action.NO_RESPONSE:
            return Block(claim=claim, instigator=self.name)
        
        return None
    
    def ask_for_action(self, other_players: List[str], game_state: GameState) -> Claim:
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

        claim: Claim = self._agent.choose_action(legal_claims, game_state)
        return claim

    def has_character(self, character_name: str) -> bool:
        for card in self._characters:
            if card.name == character_name:
                return True
        return False

    def add_character(self, character: Character) -> None:
        self._characters.append(character)
    
    def remove_character(self, game_state: GameState) -> None:
        if len(self._characters) <= 0:
            return

        character: str = self._agent.choose_character(self._characters, game_state)
        
        for card_idx in range(len(self._characters)):
            if self._characters[card_idx].name == character:
                self._revealed_characters.append(self._characters[card_idx])
                self._characters.pop(card_idx)
                return
            
        assert False # the character removed must exist

    def exchange_cards(self, num_cards_to_exchange: int, game_state: GameState) -> List[Character]:
        legal_exchanges: List[str] = [character.name for character in self._characters]
        
        characters_to_exchange: List[str] = self._agent.exchange_cards(num_cards_to_exchange, legal_exchanges, game_state)
        assert len(characters_to_exchange) == num_cards_to_exchange
        
        cards_to_put_back: List[Character] = []
        for name in characters_to_exchange:
            assert name in legal_exchanges

            for idx, character in enumerate(self._characters):
                if character.name == name:
                    cards_to_put_back.append(self._characters.pop(idx))
                    break
        
        return cards_to_put_back
    
    def propogate_reward(self, reward: float) -> None:
        self._agent.propogate_reward(reward)

        
