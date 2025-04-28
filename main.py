from player import Player
from game import Game

if __name__ == "__main__":
    game = Game()

    player1 = Player("Sebastian")
    player2 = Player("Hansel")
    player3 = Player("Yusuf")

    game.enter_players(player1, player2, player3)
    game.start_game()
    
    print("Hello World!")