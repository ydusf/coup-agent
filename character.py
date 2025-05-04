# character            active                passive
# ambassador  |  exchange characters |  block stealing
# contessa    |  blocks assassinate  |       none
# captain     |     steal 2 coins    |  block stealing
# duke        |     take 3 coins     |  block foreign aid  
# assassin    | pay 3 to assassinate |        none

class Character:
    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name