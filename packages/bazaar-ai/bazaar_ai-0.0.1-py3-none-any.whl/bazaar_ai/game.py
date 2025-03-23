from terms import CAMEL, MONEY, ICONS

class Game:
    def __init__(self, players, market):
        self.players = players
        self.market = market
        self.turn = 0
        self.round = 1

    def setup_hand(self, player):
        for _ in range(5):
            card = self.market.deck.pop()
            player.hand.append(card)

    def display_game_state(self, verbose):
        print("\n" + "="*50)
        print(f"Round {self.round}")
        print(f"Player {self.turn + 1}'s Turn")
        if verbose:
          print(self.market)
          print(self.players[0])
          print(self.players[1])
        else:
          print(self.market.summary())
        print("="*50)

    def output_statistics(self):
      # compute each player's score
      player1_score = self.players[0].purse.calculate_points(include_bonus=True)
      player2_score = self.players[1].purse.calculate_points(include_bonus=True)

      # determine which player has more camels
      player1_camel_count = sum(1 for card in self.players[0].hand if card.good_type == CAMEL)
      player2_camel_count = sum(1 for card in self.players[1].hand if card.good_type == CAMEL)
      if player1_camel_count > player2_camel_count:
        player1_score += self.market.camel_bonus
      elif player2_camel_count > player1_camel_count:
        player2_score += self.market.camel_bonus

      bold = "\033[1m"
      reset = "\033[0m"
      fg_white = "\033[38;2;255;255;255m"
      bg_black = "\033[48;2;0;0;0m"

      print(f"="*50)
      print("Results:")
      print(f"{bg_black}{fg_white}{self.players[0].name}{reset}\n{ICONS[MONEY]}: {player1_score}")
      print(f"{bg_black}{fg_white}{self.players[1].name}{reset}\n{ICONS[MONEY]}: {player2_score}")
      print(f"="*50)

    def setup(self):
      self.setup_hand(self.players[0])
      self.setup_hand(self.players[1])
      self.display_game_state(True)

    def play(self, verbose=True):
        while not self.market.is_market_closed():
            current_player = self.players[self.turn]
            current_market_observation = self.market.observe_market()
            current_player_action = current_player.select_action(current_market_observation)
            print(current_player_action)
            self.market.apply_action(current_player, current_player_action)
            self.turn = (self.turn + 1) % 2
            self.round += 1
            self.display_game_state(verbose)