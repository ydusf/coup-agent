from character import Character
from utils import Action
from utils import get_action

from typing import List

class Player:
    def __init__(self, name: str):
        self._coins: int = 0
        self._name: str = name
        self._characters: List[Character] = []
        self._log: dict = {}

    @property
    def name(self) -> str:
        return self._name

    @property
    def coins(self) -> int:
        return self._coins
    
    @coins.setter
    def coins(self, value: int) -> None:        
        if value < 2:
            raise ValueError("value must be greater than 0")
        
        self._coins = value

    def ask_for_action(self, players: List[Character]) -> str:
        prompt = f"{self.name}'s move: {self.coins} -- {self._characters[0]} -- {self._characters[1]}\n"
        
        prompt += "  [i] Take income (+1 coin)\n"
        prompt += "  [f] Take foreign aid (+2 coins)\n"
        prompt += "  [m] Use Duke's active (+3 coins)\n"
        prompt += "  [s] Use Captain's active (steal 2 coins)\n"
        prompt += "  [e] Use Ambassador's active (exchange characters)\n"

        if self.coins >= 3:
            prompt += "  [a] Use Assassin's active (-3 coins to assassinate)\n"

        if self.coins >= 7:
            prompt += "  [c] Call a coup (-7 coins)\n"

        prompt += "Your choice: "

        play = input(prompt)

        self.__handle_input__(play, players)
        
        return play
    
    def ask_for_response(self, action: Action) -> str:
        prompt = f"{self.name} choose a response: {self.coins} -- {self._characters[0]} -- {self._characters[1]}\n"

        if action == Action.ASSASSINATE:
            prompt += "  [b] Block assassination\n"
        elif action == Action.STEAL:
            prompt += "  [bs] Block stealing\n"
        elif action == Action.FOREIGN_AID:
            prompt += "  [bf] Block foreign aid\n"

        prompt += "  [n] No response\n"
        prompt += "Your choice: "

        play = input(prompt)

        self.__handle_input__(play, [])

        return play

    def add_character(self, character: Character) -> None:
        self._characters.append(character)

    def __handle_input__(self, input: str, players: List[Character]) -> None:
        action = get_action(input)
        
        if action == Action.INCOME:
            self.__take_income__() # nobody can block

        if action == Action.COUP:
            self.__coup__(players)

        if action in (Action.FOREIGN_AID, Action.ASSASSINATE, Action.EXCHANGE, Action.MONEY_MAN):
            # ask for responses of other players
            for player in players:
                if self != player:
                    player.ask_for_response(action)            

    def __take_income__(self) -> None:
        self._coins += 1

    def __take_foreign_aid__(self) -> None:
        self._coins += 2

    def __coup__(self, players: List[Character]) -> None:
        pass

# need functionality to broadcast messages to the rest of the players to give them a chance to respond