from player import Player
from character import Character, Contessa, Duke, Assassin, Captain, Ambassador

from typing import List, Optional
import random

class Game:
    def __init__(self):
        self._characters: List[Character] = [Contessa(), Contessa(), Contessa(),
                                             Duke(), Duke(), Duke(),
                                             Assassin(), Assassin(), Assassin(),
                                             Captain(), Captain(), Captain(),
                                             Ambassador(), Ambassador(), Ambassador()]
        self._players: List[Player] = []
        self._current_player: Optional[Player] = None
        self._game_active: bool = False
        self._winner: Optional[Player] = None

    def enter_players(self, *args: Player) -> None:
        for player in args:
            self._players.append(player)

    def start_game(self) -> None:
        if len(self._players) < 2:
            raise ValueError("game cannot start with less than 2 players")
        
        self._game_active = True
        self.__deal_coins__()
        self.__choose_starting_player__()

        # game loop
        while self._game_active:
            if len(self._players) == 1:
                self.__declare_winner__()
                return
            
            # game gets interesting here because we need to account for lies  

    def __choose_starting_player__(self) -> None:
        random.shuffle(self._players)
        starting_player_idx = random.randrange(len(self._players))
        self._current_player = self._players[starting_player_idx]

    def __deal_coins__(self) -> None:
        for player in self._players:
            player.coins(2)

    def __declare_winner__(self):
        self._game_active = False
        self._winner = self._players[0]
        print(f"The winner is {self._winner.name}!!!")

        