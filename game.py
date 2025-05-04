from player import Player
from character import Character
from utils import Action, Claim, Block, GameState, PlayerState

from typing import List, Dict, Optional
import random

class Game:
    def __init__(self):
        self._characters: List[Character] = [Character("Contessa"), Character("Contessa"), Character("Contessa"),
                                             Character("Assassin"), Character("Assassin"), Character("Assassin"),
                                             Character("Ambassador"), Character("Ambassador"), Character("Ambassador"),
                                             Character("Captain"), Character("Captain"), Character("Captain"),
                                             Character("Duke"), Character("Duke"), Character("Duke")]
        self._players: List[Player] = []
        self._current_player_idx: Optional[int] = None
        self._game_active: bool = False
        self._winner: Optional[Player] = None
        self._game_state: Optional[GameState] = GameState()
        self._turn: int = 0

    def enter_players(self, *args: Player) -> None:
        for player in args:
            self._players.append(player)

    def start_game(self) -> None:
        if len(self._players) < 2:
            raise ValueError("game cannot start with less than 2 players")
        
        if len(self._players) > 6:
            raise ValueError("game cannot start with more than 6 players")
        
        self._game_active = True
        self._deal_coins()
        self._deal_characters()
        self._choose_starting_player()
        self._update_game_state()

        # game loop
        while self._game_active:
            if len(self._players) == 1:
                self._declare_winner()
                return
                    
            self._handle_action()
            self._goto_next_player()
            self._update_game_state()

            for player in self._players:
                log = f"{player.name}; {player.coins}"
                for charac in player.characters:
                    log += f" -- {charac.name}"
                print(log)
            
    def _handle_action(self) -> None:
        game_state: Optional[GameState] = self._get_state()
        instigator: Player = self._players[self._current_player_idx]

        other_players: List[str] = []
        for player in self._players:
            if player.name == instigator.name:
                continue
            other_players.append(player.name)

        claim: Claim = instigator.ask_for_action(other_players, game_state)

        if claim.target is None: # either income, foreign aid, tax or exchange
            if claim.action == Action.INCOME:
                instigator.coins += 1
                print(f"{instigator.name} gets income")
            elif claim.action == Action.EXCHANGE:
                players_that_can_challenge: List[int] = []
                for player_idx in range(len(self._players)):
                    if self._players[player_idx].name == instigator.name:
                        continue
                    players_that_can_challenge.append(player_idx)

                challenger: Optional[str] = self._check_for_challenges(instigator.name, claim, players_that_can_challenge)
                if challenger is not None:
                    success: bool = self._handle_challenge(instigator.name, challenger, claim)
                    if success:
                        print("Challenge succeeded")
                        return
                    print("Challenge failed")
                
                cards_left = len(instigator.characters)
                for _ in range(cards_left):
                    instigator.add_character(self._characters.pop())

                cards_to_put_back: List[Character] = instigator.exchange_cards(game_state)
                for character in cards_to_put_back:
                    self._characters.append(character)
                random.shuffle(self._characters)

                print(f"{instigator.name} exchanges cards")

            elif claim.action == Action.TAX:
                players_that_can_challenge: List[int] = []
                for player_idx in range(len(self._players)):
                    if self._players[player_idx].name == instigator.name:
                        continue
                    players_that_can_challenge.append(player_idx)

                challenger: Optional[str] = self._check_for_challenges(instigator.name, claim, players_that_can_challenge)
                if challenger is not None:
                    success: bool = self._handle_challenge(instigator.name, challenger, claim)
                    if success:
                        print("Challenge succeeded")
                        return
                    print("Challenge failed")
                
                print(f"{instigator.name} gets tax")
                instigator.coins += 3
            
            elif claim.action == Action.FOREIGN_AID:
                blockable_players: List[int] = []
                for player_idx in range(len(self._players)):
                    if self._players[player_idx].name == instigator.name:
                        continue
                    blockable_players.append(player_idx)

                block: Optional[Block] = self._check_for_block(instigator.name, claim.action, blockable_players)
                if block is not None:
                    # we need to check if anyone wants to challenge
                    players_that_can_challenge: List[int] = []
                    for player_idx in range(len(self._players)):
                        if self._players[player_idx].name == block.instigator:
                            continue
                        players_that_can_challenge.append(player_idx)

                    challenger: Optional[str] = self._check_for_challenges(block.instigator, block.claim, players_that_can_challenge)
                    if challenger is not None:
                        success: bool = self._handle_challenge(block.instigator, challenger, block.claim)
                        if success:
                            print("Challenge succeeded")
                        else:
                            print("Challenge failed")
                            return
                    else:
                        return # nobody challenged the block
                        
                instigator.coins += 2
                print(f"{instigator.name} gets foreign aid")


        else: # either assassinating, stealing or couping
            everyone_but_target: List[int] = []
            for player_idx in range(len(self._players)):
                if self._players[player_idx].name == instigator.name:
                    continue
                if self._players[player_idx].name == claim.target:
                    continue
                everyone_but_target.append(player_idx)

            if claim.action == Action.ASSASSINATE:
                # ask anyone who isn't the target or instigator if they want to challenge 
                challenger: Optional[str] = self._check_for_challenges(instigator.name, claim, everyone_but_target)
                if challenger is not None:
                    success: bool = self._handle_challenge(instigator.name, challenger, claim)
                    if success:
                        print("Challenge succeeded")
                        return
                    print("Challenge failed")

                target_challenges: Optional[str] = self._check_for_challenges(instigator.name, claim, [self._get_player_idx(claim.target)])
                if target_challenges is not None:
                    success: bool = self._handle_challenge(instigator.name, target_challenges, claim)
                    if success:
                        print("Challenge succeeded")
                        return
                    print("Challenge failed")
                else:
                    # check if target wants to block given that they didn't challenge
                    block: Optional[Block] = self._check_for_block(instigator.name, claim.action, [self._get_player_idx(claim.target)])
                    if block is not None:
                        # we need to check if anyone wants to challenge
                        players_that_can_challenge: List[int] = []
                        for player_idx in range(len(self._players)):
                            if self._players[player_idx].name == block.instigator:
                                continue
                            players_that_can_challenge.append(player_idx)

                        challenger: Optional[str] = self._check_for_challenges(block.instigator, block.claim, players_that_can_challenge)
                        if challenger is not None:
                            success: bool = self._handle_challenge(block.instigator, challenger, block.claim)
                            if success:
                                print("Challenge succeeded; Block was unsuccessful")
                            else:
                                print("Challenge failed; Block was successful")
                                return

                target_player: Player = self._players[self._get_player_idx(claim.target)]
                target_player.remove_character(game_state)
                instigator.coins -= 3
                print(f"{instigator.name} assassinates {target_player.name}")

            elif claim.action == Action.STEAL:
                # ask anyone who isn't the target or instigator if they want to challenge 
                challenger: Optional[str] = self._check_for_challenges(instigator.name, claim, everyone_but_target)
                if challenger is not None:
                    success: bool = self._handle_challenge(instigator.name, challenger, claim)
                    if success:
                        print("Challenge succeeded")
                        return
                    print("Challenge failed")

                target_challenges: Optional[str] = self._check_for_challenges(instigator.name, claim, [self._get_player_idx(claim.target)])
                if target_challenges is not None:
                    success: bool = self._handle_challenge(instigator.name, target_challenges, claim)
                    if success:
                        print("Challenge succeeded")
                        return
                    print("Challenge failed")
                else:
                    # check if target wants to block given that they didn't challenge
                    block: Optional[Block] = self._check_for_block(instigator.name, claim.action, [self._get_player_idx(claim.target)])
                    if block is not None:
                        # we need to check if anyone wants to challenge
                        players_that_can_challenge: List[int] = []
                        for player_idx in range(len(self._players)):
                            if self._players[player_idx].name == block.instigator:
                                continue
                            players_that_can_challenge.append(player_idx)

                        challenger: Optional[str] = self._check_for_challenges(block.instigator, block.claim, players_that_can_challenge)
                        if challenger is not None:
                            success: bool = self._handle_challenge(block.instigator, challenger, block.claim)
                            if success:
                                print("Challenge succeeded; Block was unsuccessful")
                            else:
                                print("Challenge failed; Block was successful")
                                return

                target_player: Player = self._players[self._get_player_idx(claim.target)]
                coins_left = min(2, target_player.coins)
                target_player.coins -= coins_left
                instigator.coins += coins_left
                print(f"{instigator.name} steals {coins_left} coins from {target_player.name}")

            elif claim.action == Action.COUP:
                target_player: Player = self._players[self._get_player_idx(claim.target)]
                target_player.remove_character(game_state)
                instigator.coins -= 7
                print(f"{instigator.name} couped against {target_player.name}")
                


            
    def _check_for_block(self, instigator: str, action: Action, players_allowed: List[int]) -> Optional[Block]:
        game_state: Optional[GameState] = self._get_state()
        for player_idx in players_allowed:
            if self._players[player_idx].name == instigator:
                assert False # instigator should not be apart of players

            block: Optional[Block] = self._players[player_idx].ask_to_block(instigator, action, game_state)
            if block is not None:
                return block

        return None
        


    def _check_for_challenges(self, instigator: str, claim: Claim, players_that_can_challenge: List[int]) -> Optional[str]:
        game_state: Optional[GameState] = self._get_state()
        for player_idx in players_that_can_challenge:
            if self._players[player_idx].name == instigator:
                continue

            challenged: bool = self._players[player_idx].ask_to_challenge(instigator, claim, game_state)
            if challenged:
                return self._players[player_idx].name
        return None







    def _handle_challenge(self, instigator: str, challenger: str, claim: Claim) -> bool:
        game_state: Optional[GameState] = self._get_state()
        instigator_player: Player = self._players[self._get_player_idx(instigator)]
        challenger_player: Player = self._players[self._get_player_idx(challenger)]
        if claim.action == Action.EXCHANGE:
            if instigator_player.has_character("Ambassador"):
                challenger_player.remove_character(game_state)
                return False
            else:
                instigator_player.remove_character(game_state)
                return True
            
        elif claim.action == Action.TAX:
            if instigator_player.has_character("Duke"):
                challenger_player.remove_character(game_state)
                return False
            else:
                instigator_player.remove_character(game_state)
                return True
            
        elif claim.action == Action.ASSASSINATE:
            if instigator_player.has_character("Assassin"):
                challenger_player.remove_character(game_state)
                return False
            else:
                instigator_player.remove_character(game_state)
                return True
        
        elif claim.action == Action.STEAL:
            if instigator_player.has_character("Captain"):
                challenger_player.remove_character(game_state)
                return False
            else:
                instigator_player.remove_character(game_state)
                return True
            
        elif claim.action == Action.BLOCK_ASSASSINATE:
            if instigator_player.has_character("Contessa"):
                challenger_player.remove_character(game_state)
                return False
            else:
                instigator_player.remove_character(game_state)
                return True
            
        elif claim.action == Action.BLOCK_STEALING:
            if instigator_player.has_character("Captain") or instigator_player.has_character("Ambassador"):
                challenger_player.remove_character(game_state)
                return False
            else:
                instigator_player.remove_character(game_state)
                return True
            
        elif claim.action == Action.BLOCK_FOREIGN_AID:
            if instigator_player.has_character("Duke"):
                challenger_player.remove_character(game_state)
                return False
            else:
                instigator_player.remove_character(game_state)
                return True

        print(claim)
        assert False # need to implement the respective action
        

        













    def _get_state(self) -> Optional[GameState]:
        return self._game_state
    
    def _get_player_idx(self, player_name: str) -> Optional[int]:
        for player_idx in range(len(self._players)):
            if self._players[player_idx].name == player_name:
                return player_idx
        return None
    
    def _update_game_state(self) -> None:
        self._game_state.current_player = self._players[self._current_player_idx].name
        self._game_state.turn_count = self._turn
        for player in self._players:
            self._game_state.player_states[player.name] = PlayerState(coins=player.coins,
                                                                      revealed_characters=player.revealed_characters, 
                                                                      in_game=len(player.revealed_characters) == 0)

    def _choose_starting_player(self) -> None:
        random.shuffle(self._players)
        self._current_player_idx = random.randrange(len(self._players))

    def _goto_next_player(self) -> None:
        if len(self._players[self._current_player_idx].characters) == 0:
            del self._players[self._current_player_idx]
            if self._current_player_idx >= len(self._players):
                self._current_player_idx = 0
        else:
            self._current_player_idx = (self._current_player_idx + 1) % len(self._players)

        while len(self._players) > 1 and len(self._players[self._current_player_idx].characters) == 0:
            del self._players[self._current_player_idx]
            if self._current_player_idx >= len(self._players):
                self._current_player_idx = 0

        self._turn += 1

    def _deal_coins(self) -> None:
        for player in self._players:
            player.coins = 2

    def _deal_characters(self) -> None:
        random.shuffle(self._characters)
        for player in self._players:
            player.add_character(self._characters.pop())
            player.add_character(self._characters.pop())

    def _declare_winner(self) -> None:
        self._game_active = False
        self._winner = self._players[0]
        print(f"The winner is {self._winner.name}!!!")

    def _get_perspective(player_id: int) -> dict:
        pass
        