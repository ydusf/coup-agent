from game import Game
from player import Player
from logger import Logger

from typing import List, Optional

class UI:
    def __init__(self, *players: Player) -> None:
        self.game = Game()
        self.logger = Logger()
        self.players: List[Player] = list(players)

    # next thing is to make handle_action return a list of all the people involved in the action including their decisions + rewards
    # this will be used to train an RL agent
    def start_game(self) -> Optional[str]:
        if len(self.players) < 2:
            raise ValueError("game cannot start with less than 2 players")
        
        if len(self.players) > 6:
            raise ValueError("game cannot start with more than 6 players")
        
        self.game.enter_players(*self.players) 
        self.game.initialise_game()

        # game loop
        while self.game.game_is_active():
            self.logger.log_turn_start(player_name=self.game.get_player_name(self.game._current_player_idx), 
                                       game_state=self.game.get_state())      

            if self.game.get_players_left() == 1:
                self.game.declare_winner(self.logger)
                return self.game.get_player_name(0)
            
            self.game.handle_action(self.logger)
            self.game.goto_next_player()

        return None

