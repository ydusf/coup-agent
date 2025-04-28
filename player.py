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
        play = input(
            f"{self.name}'s move:\n"
            "  [i] Take income (+1 coin)\n"
            "  [f] Take foreign aid (+2 coins)\n"
            "  [m] Use Duke's active (+3 coins)\n"
            "  [s] Use Captain's active (steal 2 coins)\n"
            "  [e] Use Ambassador's active (exchange characters)\n"
            "  [a] Use Assassin's active (-3 coins to assassinate)\n"
            "Your choice: "
        )
        return play

    def add_character(self, character: Character) -> None:
        self._characters.append(character)

    def __take_income__(self) -> None:
        self._coins += 1

    def __take_foreign_aid__(self) -> None:
        self._coins += 2