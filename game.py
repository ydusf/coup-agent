from player import Player
from utils import Action, Claim, Block, GameState, Character, PlayerState, PlayerPerspective
from logger import Logger

from typing import List, Optional
import random
import copy

class Game:
    def __init__(self):
        self._deck: List[Character] = [Character.CONTESSA, Character.CONTESSA, Character.CONTESSA,
                                      Character.ASSASSIN, Character.ASSASSIN, Character.ASSASSIN,
                                      Character.AMBASSADOR, Character.AMBASSADOR, Character.AMBASSADOR,
                                      Character.CAPTAIN, Character.CAPTAIN, Character.CAPTAIN,
                                      Character.DUKE, Character.DUKE, Character.DUKE]
        
        self._players: List[Player] = []
        self._current_player_idx: Optional[int] = None
        self._game_active: bool = False
        self._winner: Optional[Player] = None
        self._game_state: Optional[GameState] = GameState()

    def enter_players(self, *args: Player) -> None:
        names_this_far: List[str] = []   
        for player in args:
            if player.name in names_this_far:
                raise ValueError("Two players have the same username")
            
            self._players.append(player)
            names_this_far.append(player.name)

    def initialise_game(self) -> None:
        assert len(self._players) > 1

        self._game_active = True
        self._deal_coins()
        self._deal_characters()
        self._choose_starting_player()
        self._update_game_state()
            
    def handle_action(self, logger: Logger) -> None:
        game_state: Optional[GameState] = self.get_state()
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

        claim: Claim = instigator.ask_for_action(other_players, self._get_player_perspective(instigator.name))
        logger.log_action(
            instigator=instigator.name,
            action=claim.action,
            target=claim.target,
            game_state=game_state
        )

        if claim.target is None: # either income, foreign aid, tax or exchange
            if claim.action == Action.INCOME:
                instigator.coins += 1
                print(f"{instigator.name} gets income")

                instigator.propogate_reward(self._calculate_reward(1, 0, 0, 0, 0), self._get_player_perspective(instigator.name))
                self._update_game_state()
                logger.log_game_state(game_state=self.get_state())

            elif claim.action == Action.EXCHANGE:
                challenger: Optional[str] = self._check_for_challenges(instigator.name, claim, players_that_can_challenge_action, logger)
                if challenger is not None:
                    success: bool = self._handle_challenge(instigator.name, challenger, claim)
                    logger.log_challenge(
                        instigator=instigator.name,
                        challenger=challenger,
                        action=claim.action,
                        success=success,
                        game_state=self.get_state()
                    )
                    if success:
                        return
                
                cards_left = len(instigator.characters)
                for _ in range(cards_left):
                    instigator.add_character(self._deck.pop())

                characters_to_put_back: List[Character] = instigator.exchange_cards(cards_left, self._get_player_perspective(instigator.name))
                for character in characters_to_put_back:
                    self._deck.append(character)
                random.shuffle(self._deck)

                print(f"{instigator.name} exchanges cards")

                instigator.propogate_reward(self._calculate_reward(0, 0, 0, 0, cards_left), self._get_player_perspective(instigator.name))
                self._update_game_state()
                logger.log_game_state(game_state=self.get_state())

            elif claim.action == Action.TAX:
                challenger: Optional[str] = self._check_for_challenges(instigator.name, claim, players_that_can_challenge_action, logger)
                if challenger is not None:
                    success: bool = self._handle_challenge(instigator.name, challenger, claim)
                    logger.log_challenge(
                        instigator=instigator.name,
                        challenger=challenger,
                        action=claim.action,
                        success=success,
                        game_state=self.get_state()
                    )
                    if success:
                        return

                instigator.coins += 3
                print(f"{instigator.name} gets tax")

                instigator.propogate_reward(self._calculate_reward(3, 0, 0, 0, 0), self._get_player_perspective(instigator.name))
                self._update_game_state()
                logger.log_game_state(game_state=self.get_state())
            
            elif claim.action == Action.FOREIGN_AID:
                block: Optional[Block] = self._check_for_block(instigator.name, claim.action, players_that_can_challenge_action)
                if block is not None:
                    logger.log_block(
                        instigator=instigator.name,
                        blocker=block.instigator,
                        action=claim.action,
                        block_action=block.claim.action,
                        game_state=self.get_state()
                    )
                    players_that_can_challenge_block: List[int] = self._get_players_that_can_challenge(block.instigator)

                    challenger: Optional[str] = self._check_for_challenges(block.instigator, block.claim, players_that_can_challenge_block, logger)
                    if challenger is not None:
                        success: bool = self._handle_challenge(block.instigator, challenger, block.claim)
                        logger.log_challenge(
                            instigator=block.instigator,
                            challenger=challenger,
                            action=block.claim.action,
                            success=success,
                            game_state=self.get_state()
                        )
                        if not success:
                            return # challenge to block failed 
  
                    else:
                        # might need to add something here to reward the person who successfully blocked
                        return # nobody challenged the block
                        
                instigator.coins += 2
                print(f"{instigator.name} gets foreign aid")

                instigator.propogate_reward(self._calculate_reward(2, 0, 0, 0, 0), self._get_player_perspective(instigator.name))
                self._update_game_state()
                logger.log_game_state(game_state=self.get_state())

        else: # either assassinating, stealing or couping
            if claim.action == Action.ASSASSINATE:
                # ask anyone who isn't the target or instigator if they want to challenge 
                challenger: Optional[str] = self._check_for_challenges(instigator.name, claim, players_that_can_challenge_action, logger)
                if challenger is not None:
                    success: bool = self._handle_challenge(instigator.name, challenger, claim)
                    logger.log_challenge(
                        instigator=instigator.name,
                        challenger=challenger,
                        action=claim.action,
                        success=success,
                        game_state=self.get_state()
                    )
                    if success:
                        return

                # check if target wants to block given that they didn't challenge
                block: Optional[Block] = self._check_for_block(instigator.name, claim.action, [self._get_player_idx(claim.target)])
                if block is not None:
                    logger.log_block(
                        instigator=instigator.name,
                        blocker=block.instigator,
                        action=claim.action,
                        block_action=block.claim.action,
                        game_state=self.get_state()
                    )
                    # we need to check if anyone wants to challenge
                    players_that_can_challenge_block: List[int] = self._get_players_that_can_challenge(block.instigator)

                    challenger: Optional[str] = self._check_for_challenges(block.instigator, block.claim, players_that_can_challenge_block, logger)
                    if challenger is not None:
                        success: bool = self._handle_challenge(block.instigator, challenger, block.claim)
                        logger.log_challenge(
                            instigator=block.instigator,
                            challenger=challenger,
                            action=block.claim.action,
                            success=success,
                            game_state=self.get_state()
                        )
                        if not success:
                            return # challenge to block failed
                    else:
                        # might need to add something here to reward the person who successfully blocked
                        return # nobody challenged the block

                target_player: Player = self._players[self._get_player_idx(claim.target)]
                target_player.remove_character(self._get_player_perspective(target_player.name))
                instigator.coins -= 3
                print(f"{instigator.name} assassinates {target_player.name}")

                instigator.propogate_reward(self._calculate_reward(-3, 0, 0, 1, 0), self._get_player_perspective(instigator.name))
                target_player.propogate_reward(self._calculate_reward(0, 0, 1, 0, 0), self._get_player_perspective(target_player.name))
                self._update_game_state()
                logger.log_game_state(game_state=self.get_state())

            elif claim.action == Action.STEAL:
                # ask anyone who isn't the target or instigator if they want to challenge 
                challenger: Optional[str] = self._check_for_challenges(instigator.name, claim, players_that_can_challenge_action, logger)
                if challenger is not None:
                    success: bool = self._handle_challenge(instigator.name, challenger, claim)
                    logger.log_challenge(
                        instigator=instigator.name,
                        challenger=challenger,
                        action=claim.action,
                        success=success,
                        game_state=self.get_state()
                    )
                    if success:
                        return

                # check if target wants to block given that they didn't challenge
                block: Optional[Block] = self._check_for_block(instigator.name, claim.action, [self._get_player_idx(claim.target)])
                if block is not None:
                    logger.log_block(
                        instigator=instigator.name,
                        blocker=block.instigator,
                        action=claim.action,
                        block_action=block.claim.action,
                        game_state=self.get_state()
                    )
                    # we need to check if anyone wants to challenge
                    players_that_can_challenge_block: List[int] = self._get_players_that_can_challenge(block.instigator)

                    challenger: Optional[str] = self._check_for_challenges(block.instigator, block.claim, players_that_can_challenge_block, logger)
                    if challenger is not None:
                        success: bool = self._handle_challenge(block.instigator, challenger, block.claim)
                        logger.log_challenge(
                            instigator=block.instigator,
                            challenger=challenger,
                            action=block.claim.action,
                            success=success,
                            game_state=self.get_state()
                        )
                        if not success:
                            return
                    else:
                        # might need to add something here to reward the person who successfully blocked
                        return # nobody challenged the block

                target_player: Player = self._players[self._get_player_idx(claim.target)]
                coins_left = min(2, target_player.coins)
                target_player.coins -= coins_left
                instigator.coins += coins_left
                print(f"{instigator.name} steals {coins_left} coins from {target_player.name}")

                instigator.propogate_reward(self._calculate_reward(coins_left, 0, 0, 0, 0), self._get_player_perspective(instigator.name))
                target_player.propogate_reward(self._calculate_reward(-coins_left, 0, 0, 0, 0), self._get_player_perspective(target_player.name))
                self._update_game_state()
                logger.log_game_state(game_state=self.get_state())

            elif claim.action == Action.COUP:
                target_player: Player = self._players[self._get_player_idx(claim.target)]
                target_player.remove_character(self._get_player_perspective(target_player.name))
                instigator.coins -= 7
                print(f"{instigator.name} couped against {target_player.name}")

                instigator.propogate_reward(self._calculate_reward(-7, 0, 0, 1, 0), self._get_player_perspective(instigator.name))
                target_player.propogate_reward(self._calculate_reward(0, 0, 1, 0, 0), self._get_player_perspective(target_player.name))
                self._update_game_state()
                logger.log_game_state(game_state=self.get_state())

    def _get_players_that_can_challenge(self, instigator: str):
        players_that_can_challenge: List[int] = []
        for player_idx in range(len(self._players)):
            if self._players[player_idx].name == instigator:
                continue
            players_that_can_challenge.append(player_idx)
        random.shuffle(players_that_can_challenge)
        return players_that_can_challenge

    def _check_for_block(self, instigator: str, action: Action, players_allowed: List[int]) -> Optional[Block]:
        game_state: Optional[GameState] = self.get_state()
        for player_idx in players_allowed:
            potential_blocker: Player = self._players[player_idx]
            if self._players[player_idx].name == instigator:
                assert False # instigator should not be apart of players

            block: Optional[Block] = self._players[player_idx].ask_to_block(instigator, action, self._get_player_perspective(potential_blocker.name))
            if block is not None:
                return block

        return None

    def _check_for_challenges(self, instigator: str, claim: Claim, players_that_can_challenge: List[int], logger: Logger) -> Optional[str]:
        game_state: Optional[GameState] = self.get_state()
        for player_idx in players_that_can_challenge:
            potential_challenger: Player = self._players[player_idx]
            if potential_challenger.name == instigator:
                continue

            challenged: bool = potential_challenger.ask_to_challenge(instigator, claim, self._get_player_perspective(potential_challenger.name))
            if challenged:
                return potential_challenger.name
            
            logger.log_no_challenge(instigator, potential_challenger.name, claim.action, game_state)
            
        # nobody challenged
        return None

    def _handle_challenge(self, instigator: str, challenger: str, claim: Claim) -> bool:
        action_to_roles = { Action.EXCHANGE: [Character.AMBASSADOR],
                            Action.TAX: [Character.DUKE],
                            Action.ASSASSINATE: [Character.ASSASSIN],
                            Action.STEAL: [Character.CAPTAIN],
                            Action.BLOCK_ASSASSINATE: [Character.CONTESSA],
                            Action.BLOCK_STEALING: [Character.CAPTAIN, Character.AMBASSADOR],
                            Action.BLOCK_FOREIGN_AID: [Character.DUKE] }

        roles = action_to_roles.get(claim.action)
        if roles is not None:
            return self._apply_challenge(challenger, instigator, roles)

        print(claim)
        assert False # need to implement the respective action
        
    def _apply_challenge(self, challenger: str, instigator: str, characters_claiming: List[Character]) -> bool:
        instigator_player: Player = self._players[self._get_player_idx(instigator)]
        challenger_player: Player = self._players[self._get_player_idx(challenger)]
        not_lying: bool = any(instigator_player.has_character(character) for character in characters_claiming)
        if not_lying:
            challenger_player.remove_character(self._get_player_perspective(challenger))
            instigator_player.add_character(self._deck.pop())
            character_to_put_back: List[Character] = instigator_player.exchange_cards(1, self._get_player_perspective(instigator))
            for character in character_to_put_back:
                self._deck.append(character)
            random.shuffle(self._deck)

            instigator_player.propogate_reward(self._calculate_reward(0, 0, 0, 1, 0), self._get_player_perspective(instigator))
            challenger_player.propogate_reward(self._calculate_reward(0, 0, 1, 0, 0), self._get_player_perspective(challenger))
            return False
        else:
            instigator_player.remove_character(self._get_player_perspective(instigator))
            instigator_player.propogate_reward(self._calculate_reward(0, 0, 1, 0, 0), self._get_player_perspective(instigator))
            challenger_player.propogate_reward(self._calculate_reward(0, 0, 0, 1, 0), self._get_player_perspective(challenger))
            return True

    def _calculate_reward(self, coins_gained: int, other_coins_lost: int, cards_lost: int, other_cards_lost: int, cards_seen: int) -> float:
        total_reward: float = 0.0
        total_reward += (coins_gained * 0.2)
        total_reward += (other_coins_lost * 0.1)
        total_reward += (cards_lost * -1.0)
        total_reward += (other_cards_lost * 0.5)
        total_reward += (cards_seen * 0.2)

        return total_reward

    def get_state(self) -> Optional[GameState]:
        game_state_copy: GameState = copy.deepcopy(self._game_state)
        return game_state_copy
    
    def get_player_name(self, idx: int) -> str:
        assert len(self._players) > idx
        return self._players[idx].name
    
    def get_players_left(self) -> int:
        return len(self._players)
    
    def game_is_active(self) -> bool:
        return self._game_active
    
    def _get_player_perspective(self, player_name: str) -> Optional[PlayerPerspective]:
        game_state: GameState = self.get_state()
        player: Player = self._players[self._get_player_idx(player_name)]
        player_perspective = PlayerPerspective(game_state, player.name, player.characters)
        return player_perspective
    
    def _get_player_idx(self, player_name: str) -> Optional[int]:
        for player_idx in range(len(self._players)):
            if self._players[player_idx].name == player_name:
                return player_idx
        return None

    def _choose_starting_player(self) -> None:
        random.shuffle(self._players)
        self._current_player_idx = random.randrange(len(self._players))

    def goto_next_player(self) -> None:
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

        self._update_game_state()

    def _deal_coins(self) -> None:
        for player in self._players:
            player.coins = 2

    def _deal_characters(self) -> None:
        random.shuffle(self._deck)
        for player in self._players:
            player.add_character(self._deck.pop())
            player.add_character(self._deck.pop())

    def declare_winner(self, logger: Logger) -> None:
        self._game_active = False
        self._winner = self._players[0]
        self._winner.propogate_reward(10, self._get_player_perspective(self._winner.name))
        for player in self._players:
            if player.name != self._winner:
                player.propogate_reward(-10, self._get_player_perspective(player.name))
        logger.log_winner(self._winner.name)   

    def _update_game_state(self) -> None:
        self._game_state.current_player = self._players[self._current_player_idx].name
        self._game_state.num_players_alive = len(self._players)
        self._game_state.turn_order = [player.name for player in self._players]
        self._game_state.revealed_characters.clear()
        for player in self._players:
            self._game_state.player_states[player.name] = PlayerState(coins=player.coins,
                                                                      revealed_characters=player.revealed_characters.copy(),
                                                                      in_game=len(player.characters) > 0)
        
        for name, player_state in self._game_state.player_states.items():
            for character in player_state.revealed_characters:
                self._game_state.revealed_characters.append(character)