from typing import List

class Player:
    def __init__(self, name: str):
        self._coins: int = 0
        self._name: str = name
        self._characters: List

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

    def take_income(self) -> None:
        self._coins += 1

    def take_foreign_aid(self) -> None:
        self._coins += 2