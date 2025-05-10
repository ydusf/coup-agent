from player import Player
from character import Character
from utils import Action, Claim, Block, GameState, PlayerState
from logger import Logger

from typing import List, Dict, Optional
import random
import copy

class Game:
    def __init__(self):
        self._deck: List[Character] = [Character("Contessa"), Character("Contessa"), Character("Contessa"),
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
        self._logger: Logger = Logger()

    def enter_players(self, *args: Player) -> None:
        for player in args:
            self._players.append(player)

    def start_game(self) -> Optional[Player]:
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
            self._logger.log_turn_start(turn=self._turn, 
                                        player_name=self._players[self._current_player_idx].name, 
                                        game_state=self._get_state())      

            if len(self._players) == 1:
                self._declare_winner()
                return self._winner
            
            self._handle_action()
            self._goto_next_player()
            
    def _handle_action(self) -> None:
        game_state: Optional[GameState] = self._get_state()
        instigator: Player = self._players[self._current_player_idx]

        other_players: List[str] = []
        for player in self._players:
            if player.name == instigator.name:
                continue
            other_players.append(player.name)

        players_that_can_challenge_action: List[int] = []
        for player_idx in range(len(self._players)):
            if self._players[player_idx].name == instigator.name:
                continue
            players_that_can_challenge_action.append(player_idx)

        claim: Claim = instigator.ask_for_action(other_players, game_state)
        self._logger.log_action(
            turn=self._turn,
            instigator=instigator.name,
            action=claim.action,
            target=claim.target,
            game_state=game_state
        )

        if claim.target is None: # either income, foreign aid, tax or exchange
            if claim.action == Action.INCOME:
                instigator.coins += 1
                print(f"{instigator.name} gets income")
                self._update_game_state()
                self._logger.log_game_state(game_state=self._get_state())

            elif claim.action == Action.EXCHANGE:
                challenger: Optional[str] = self._check_for_challenges(instigator.name, claim, players_that_can_challenge_action)
                if challenger is not None:
                    success: bool = self._handle_challenge(instigator.name, challenger, claim)
                    self._logger.log_challenge(
                        turn=self._turn,
                        instigator=instigator.name,
                        challenger=challenger,
                        action=claim.action,
                        success=success,
                        game_state=self._get_state()
                    )
                    if success:
                        return
                
                cards_left = len(instigator.characters)
                for _ in range(cards_left):
                    instigator.add_character(self._deck.pop())

                characters_to_put_back: List[Character] = instigator.exchange_cards(len(instigator.characters) // 2, game_state)
                for character in characters_to_put_back:
                    self._deck.append(character)
                random.shuffle(self._deck)

                print(f"{instigator.name} exchanges cards")
                self._update_game_state()
                self._logger.log_game_state(game_state=self._get_state())

            elif claim.action == Action.TAX:
                challenger: Optional[str] = self._check_for_challenges(instigator.name, claim, players_that_can_challenge_action)
                if challenger is not None:
                    success: bool = self._handle_challenge(instigator.name, challenger, claim)
                    self._logger.log_challenge(
                        turn=self._turn,
                        instigator=instigator.name,
                        challenger=challenger,
                        action=claim.action,
                        success=success,
                        game_state=self._get_state()
                    )
                    if success:
                        return
                
                print(f"{instigator.name} gets tax")
                instigator.coins += 3
                self._update_game_state()
                self._logger.log_game_state(game_state=self._get_state())
            
            elif claim.action == Action.FOREIGN_AID:
                block: Optional[Block] = self._check_for_block(instigator.name, claim.action, players_that_can_challenge_action)
                if block is not None:
                    self._logger.log_block(
                        turn=self._turn,
                        instigator=instigator.name,
                        blocker=block.instigator,
                        action=claim.action,
                        block_action=block.claim.action,
                        game_state=self._get_state()
                    )
                    players_that_can_challenge_block: List[int] = self._get_players_that_can_challenge(block.instigator)

                    challenger: Optional[str] = self._check_for_challenges(block.instigator, block.claim, players_that_can_challenge_block)
                    if challenger is not None:
                        success: bool = self._handle_challenge(block.instigator, challenger, block.claim)
                        self._logger.log_challenge(
                            turn=self._turn,
                            instigator=block.instigator,
                            challenger=challenger,
                            action=block.claim.action,
                            success=success,
                            game_state=self._get_state()
                        )
                        if not success:
                            return 
  
                    else:
                        return # nobody challenged the block
                        
                instigator.coins += 2
                print(f"{instigator.name} gets foreign aid")
                self._update_game_state()
                self._logger.log_game_state(game_state=self._get_state())

        else: # either assassinating, stealing or couping
            if claim.action == Action.ASSASSINATE:
                # ask anyone who isn't the target or instigator if they want to challenge 
                challenger: Optional[str] = self._check_for_challenges(instigator.name, claim, players_that_can_challenge_action)
                if challenger is not None:
                    success: bool = self._handle_challenge(instigator.name, challenger, claim)
                    self._logger.log_challenge(
                        turn=self._turn,
                        instigator=instigator.name,
                        challenger=challenger,
                        action=claim.action,
                        success=success,
                        game_state=self._get_state()
                    )
                    if success:
                        return

                # check if target wants to block given that they didn't challenge
                block: Optional[Block] = self._check_for_block(instigator.name, claim.action, [self._get_player_idx(claim.target)])
                if block is not None:
                    self._logger.log_block(
                        turn=self._turn,
                        instigator=instigator.name,
                        blocker=block.instigator,
                        action=claim.action,
                        block_action=block.claim.action,
                        game_state=self._get_state()
                    )
                    # we need to check if anyone wants to challenge
                    players_that_can_challenge_block: List[int] = self._get_players_that_can_challenge(block.instigator)

                    challenger: Optional[str] = self._check_for_challenges(block.instigator, block.claim, players_that_can_challenge_block)
                    if challenger is not None:
                        success: bool = self._handle_challenge(block.instigator, challenger, block.claim)
                        self._logger.log_challenge(
                            turn=self._turn,
                            instigator=block.instigator,
                            challenger=challenger,
                            action=block.claim.action,
                            success=success,
                            game_state=self._get_state()
                        )
                        if not success:
                            return

                target_player: Player = self._players[self._get_player_idx(claim.target)]
                target_player.remove_character(game_state)
                instigator.coins -= 3
                print(f"{instigator.name} assassinates {target_player.name}")
                self._update_game_state()
                self._logger.log_game_state(game_state=self._get_state())

            elif claim.action == Action.STEAL:
                # ask anyone who isn't the target or instigator if they want to challenge 
                challenger: Optional[str] = self._check_for_challenges(instigator.name, claim, players_that_can_challenge_action)
                if challenger is not None:
                    success: bool = self._handle_challenge(instigator.name, challenger, claim)
                    self._logger.log_challenge(
                        turn=self._turn,
                        instigator=instigator.name,
                        challenger=challenger,
                        action=claim.action,
                        success=success,
                        game_state=self._get_state()
                    )
                    if success:
                        return

                # check if target wants to block given that they didn't challenge
                block: Optional[Block] = self._check_for_block(instigator.name, claim.action, [self._get_player_idx(claim.target)])
                if block is not None:
                    self._logger.log_block(
                        turn=self._turn,
                        instigator=instigator.name,
                        blocker=block.instigator,
                        action=claim.action,
                        block_action=block.claim.action,
                        game_state=self._get_state()
                    )
                    # we need to check if anyone wants to challenge
                    players_that_can_challenge_block: List[int] = self._get_players_that_can_challenge(block.instigator)

                    challenger: Optional[str] = self._check_for_challenges(block.instigator, block.claim, players_that_can_challenge_block)
                    if challenger is not None:
                        success: bool = self._handle_challenge(block.instigator, challenger, block.claim)
                        self._logger.log_challenge(
                            turn=self._turn,
                            instigator=block.instigator,
                            challenger=challenger,
                            action=block.claim.action,
                            success=success,
                            game_state=self._get_state()
                        )
                        if not success:
                            return

                target_player: Player = self._players[self._get_player_idx(claim.target)]
                coins_left = min(2, target_player.coins)
                target_player.coins -= coins_left
                instigator.coins += coins_left
                print(f"{instigator.name} steals {coins_left} coins from {target_player.name}")
                self._update_game_state()
                self._logger.log_game_state(game_state=self._get_state())

            elif claim.action == Action.COUP:
                target_player: Player = self._players[self._get_player_idx(claim.target)]
                target_player.remove_character(game_state)
                instigator.coins -= 7
                print(f"{instigator.name} couped against {target_player.name}")
                self._update_game_state()
                self._logger.log_game_state(game_state=self._get_state())

    def _get_players_that_can_challenge(self, instigator: str):
        players_that_can_challenge: List[int] = []
        for player_idx in range(len(self._players)):
            if self._players[player_idx].name == instigator:
                continue
            players_that_can_challenge.append(player_idx)
        random.shuffle(players_that_can_challenge)
        return players_that_can_challenge

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
        action_to_roles = { Action.EXCHANGE: ["Ambassador"],
                            Action.TAX: ["Duke"],
                            Action.ASSASSINATE: ["Assassin"],
                            Action.STEAL: ["Captain"],
                            Action.BLOCK_ASSASSINATE: ["Contessa"],
                            Action.BLOCK_STEALING: ["Captain", "Ambassador"],
                            Action.BLOCK_FOREIGN_AID: ["Duke"] }

        roles = action_to_roles.get(claim.action)
        if roles is not None:
            return self._apply_challenge(challenger, instigator, roles)

        print(claim)
        assert False # need to implement the respective action
        
    def _apply_challenge(self, challenger: str, instigator: str, characters_claiming: List[str]) -> bool:
        game_state: Optional[GameState] = self._get_state()
        instigator_player: Player = self._players[self._get_player_idx(instigator)]
        challenger_player: Player = self._players[self._get_player_idx(challenger)]
        not_lying: bool = any(instigator_player.has_character(name) for name in characters_claiming)
        if not_lying:
            challenger_player.remove_character(game_state)
            instigator_player.add_character(self._deck.pop())
            character_to_put_back: List[Character] = instigator_player.exchange_cards(1, game_state)
            for character in character_to_put_back:
                self._deck.append(character)
            random.shuffle(self._deck)
            return False
        else:
            instigator_player.remove_character(game_state)
            return True

    def _get_state(self) -> Optional[GameState]:
        game_state_copy: GameState = copy.deepcopy(self._game_state)
        return game_state_copy
    
    def _get_player_idx(self, player_name: str) -> Optional[int]:
        for player_idx in range(len(self._players)):
            if self._players[player_idx].name == player_name:
                return player_idx
        return None

    def _choose_starting_player(self) -> None:
        random.shuffle(self._players)
        self._current_player_idx = random.randrange(len(self._players))

    def _goto_next_player(self) -> None:
        self._update_game_state()
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
        self._update_game_state()

    def _deal_coins(self) -> None:
        for player in self._players:
            player.coins = 2

    def _deal_characters(self) -> None:
        random.shuffle(self._deck)
        for player in self._players:
            player.add_character(self._deck.pop())
            player.add_character(self._deck.pop())

    def _declare_winner(self) -> None:
        self._game_active = False
        self._winner = self._players[0]
        self._logger.log_winner(self._winner.name)   

    def _update_game_state(self) -> None:
        self._game_state.turn_count = self._turn
        self._game_state.current_player = self._players[self._current_player_idx].name
        self._game_state.num_players_alive = len(self._players)
        self._game_state.turn_order = [player.name for player in self._players]
        for player in self._players:
            self._game_state.player_states[player.name] = PlayerState(coins=player.coins,
                                                                      revealed_characters=player.revealed_characters.copy(),
                                                                      in_game=len(player.characters) > 0)
            for character in player.revealed_characters:
                if character not in self._game_state.revealed_characters:
                    self._game_state.revealed_characters.append(character)