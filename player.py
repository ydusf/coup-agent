class Player:
    def __init__(self, name: str):
        self._coins = 0
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @property
    def coins(self) -> int:
        return self._coins
    
    @coins.setter
    def coins(self, value: int) -> None:
        if not value:
            raise ValueError("value cannot be empty")
        
        if value <= 0:
            raise ValueError("value must be greater than 0")
        
        self._coins = value

    def take_one_coin(self) -> None:
        self._coins += 1

    def take_foreign_aid(self) -> None:
        self._coins += 2