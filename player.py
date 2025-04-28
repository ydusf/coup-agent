from character import Character

from typing import List

class Player:
    def __init__(self, name: str):
        self._coins: int = 0
        self._name: str = name
        self._characters: List[Character] = []

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

    def ask_for_input(self) -> str:

        prompt: str = f"{self.name}'s move: {self.coins} -- {self._characters[0]} -- {self._characters[1]}\n"
        
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
        
        return play

    def add_character(self, character: Character) -> None:
        self._characters.append(character)

    def __take_income__(self) -> None:
        self._coins += 1

    def __take_foreign_aid__(self) -> None:
        self._coins += 2