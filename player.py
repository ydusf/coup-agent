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
        challenged: bool = self._agent.choose_to_challenge(self.name, instigator, claim, game_state)
        if challenged:
            print(f"{self.name} challenges {instigator} for calling {claim.action}")
        else:
            print(f"{self.name} does not challenge")
        return challenged
    
    def ask_to_block(self, instigator: str, action: Action, game_state: GameState) -> Optional[Block]:
        legal_responses: List[Action] = [Action.NO_RESPONSE]
        if action == Action.STEAL:
            legal_responses.append(Action.BLOCK_STEALING)
        elif action == Action.ASSASSINATE:
            legal_responses.append(Action.BLOCK_ASSASSINATE)
        elif action == Action.FOREIGN_AID:
            legal_responses.append(Action.BLOCK_FOREIGN_AID)

        claim: Claim = self._agent.choose_to_block(self.name, legal_responses, instigator, action, game_state)
        if claim.action != Action.NO_RESPONSE:
            print(f"{self.name} blocks {instigator} using {action}")
            return Block(claim=claim, instigator=self.name)
        
        print(f"{self.name} does not block {instigator} using {action}")
        return None
    
    def ask_for_action(self, other_players: List[str], game_state: GameState) -> Claim:
        legal_actions: List[Action] = [Action.INCOME, Action.FOREIGN_AID, Action.TAX, Action.EXCHANGE, Action.STEAL]
        if self.coins >= 3:
            legal_actions.append(Action.ASSASSINATE)
        if self.coins >= 7:
            legal_actions.append(Action.COUP)
        if self.coins >= 10:
            legal_actions = [Action.COUP]

        claim: Claim = self._agent.choose_action(self.name, legal_actions, other_players, game_state)
        if claim.target is not None:
            print(f"{self.name} played {claim.action} against {claim.target}")
        else:
            print(f"{self.name} played {claim.action}")
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

        character: str = self._agent.choose_character(self.name, self._characters, game_state)
        
        for card_idx in range(len(self._characters)):
            if self._characters[card_idx].name == character:
                self._revealed_characters.append(self._characters[card_idx])
                self._characters.pop(card_idx)
                return
            
        assert False # the character removed must exist

    def exchange_cards(self, num_cards_to_exchange: int, game_state: GameState) -> List[Character]:
        card_indices_to_put_back: List[int] = self._agent.exchange_cards(self.name, num_cards_to_exchange, self._characters.copy(), game_state)
        cards_to_put_back: List[Character] = []
        for card_idx in card_indices_to_put_back:
            character: Character = self.characters.pop(card_idx)
            cards_to_put_back.append(character)

        return cards_to_put_back
    
    def propogate_result(self, did_agent_win: bool) -> None:
        self._agent.update_weights(self.name, did_agent_win)

        
