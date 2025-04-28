from abc import ABC, abstractmethod
from typing import Optional

# character            active                passive
# ambassador  |  exchange characters |  block stealing
# contessa    |  blocks assassinate  |       none
# captain     |     steal 2 coins    |  block stealing
# duke        |     take 3 coins     |  block foreign aid  
# assassin    | pay 3 to assassinate |        none

class Character:
    def __init__(self):
        pass

    @abstractmethod
    def use_active(self) -> None:
        print("used active ability")
        pass

    @abstractmethod
    def use_passive(self) -> None:
        print("used passive ability")
        pass

class Contessa(Character):
    def __init__(self):
        super().__init__()

    def use_active(self) -> None:
        pass

    def use_passive(self) -> None:
        pass

    def __str__(self) -> str:
        return "Contessa"

class Assassin(Character):
    def __init__(self):
        super().__init__()

    def use_active(self) -> None:
        pass

    def use_passive(self) -> None:
        pass

    def __str__(self) -> str:
        return "Assassin"

class Duke(Character):
    def __init__(self):
        super().__init__()

    def use_active(self) -> None:
        pass

    def use_passive(self) -> None:
        pass

    def __str__(self) -> str:
        return "Duke"

class Captain(Character):
    def __init__(self):
        super().__init__()

    def use_active(self) -> None:
        pass

    def use_passive(self) -> None:
        pass

    def __str__(self) -> str:
        return "Captain"

class Ambassador(Character):
    def __init__(self):
        super().__init__()

    def use_active(self) -> None:
        pass

    def use_passive(self) -> None:
        pass

    def __str__(self) -> str:
        return "Ambassador"