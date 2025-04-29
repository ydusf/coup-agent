from enum import Enum

class Action(Enum):
    INCOME = 1
    FOREIGN_AID = 2
    MONEY_MAN = 3
    ASSASSINATE = 4
    STEAL = 5
    EXCHANGE = 6
    COUP = 7
    BLOCK_STEALING = 8
    BLOCK_ASSASSINATE = 9
    BLOCK_FOREIGN_AID = 10
    CALL_BULLSHIT = 11
    NO_RESPONSE = 12

def get_action(input: str) -> Action:
    match input:
        case "i":
            return Action.INCOME
        case "f":
            return Action.FOREIGN_AID
        case "m":
            return Action.MONEY_MAN
        case "s":
            return Action.STEAL
        case "e":
            return Action.EXCHANGE
        case "a":
            return Action.ASSASSINATE
        case "c":
            return Action.COUP
        case "ba":
            return Action.BLOCK_ASSASSINATE
        case "bf":
            return Action.BLOCK_FOREIGN_AID
        case "bs":
            return Action.BLOCK_STEALING
        case "bullshit":
            return Action.CALL_BULLSHIT
        case "n":
            return Action.NO_RESPONSE
    
    raise ValueError("invalid input")