from abc import ABC, abstractmethod
import random
from terms import THREE, FOUR, FIVE, MONEY, ICONS

# formatting
bold = "\033[1m"
reset = "\033[0m"
fg_white = "\033[38;2;255;255;255m"
bg_black = "\033[48;2;0;0;0m"

from actions import Take, Trade, Sell, Herd

class Player:
    def __init__(self, SEED, name):
        # use this for any random operations
        self._rng = random.Random(SEED)

        self._name = name
        self._hand = []
        self._purse = Satchel()

    @property
    def rng(self):
      return self._rng

    @property
    def name(self):
      return self._name

    @property
    def hand(self):
      return self._hand

    @property
    def purse(self):
      return self._purse

    def get_all_actions(self, market_observation):
      actions = []
      actions += Take.get_all_actions(self.hand, market_observation)
      actions += Trade.get_all_actions(self.hand, market_observation)
      actions += Sell.get_all_actions(self.hand, market_observation)
      actions += Herd.get_all_actions(self.hand, market_observation)
      return actions

    @abstractmethod
    def select_action(self, market_observation):
      actions = self.get_all_actions(market_observation)
      return self.rng.choice(actions)

    def __repr__(self):
        bold = "\033[1m"
        reset = "\033[0m"
        fg_white = "\033[38;2;255;255;255m"
        bg_black = "\033[48;2;0;0;0m"

        return f"{bg_black}{fg_white}{self.name}{reset}\n{bold}Hand:{reset}\n{self.hand}\n{self.purse}"
    
    
class Satchel:
    def __init__(self):
        self._coins = []
        self._bonus_coins = {THREE: [], FOUR: [], FIVE: []}

    def add_coin(self, coin):
      self._coins.append(coin)

    @property
    def coins(self):
      return self._coins

    def add_bonus_coin(self, bonus_coin):
      self._bonus_coins[bonus_coin.bonus_type].append(bonus_coin)

    def get_bonus_coin_count(self, bonus_type):
      return len(self._bonus_coins[bonus_type])

    def calculate_points(self, include_bonus = False):
      points = 0
      for coin in self._coins:
        points += coin.value
      if include_bonus:
        for bonus_coins_by_type in self._bonus_coins.values():
          for bonus_coin in bonus_coins_by_type:
            points += bonus_coin.value
      return points

    def __repr__(self):
        s =  f"{bold}Purse:{reset}\n{ICONS[MONEY]}: {self.calculate_points()} | "
        s += f"{ICONS[THREE]}: {self.get_bonus_coin_count(THREE)} "
        s += f"{ICONS[FOUR]}: {self.get_bonus_coin_count(FOUR)} "
        s += f"{ICONS[FIVE]}: {self.get_bonus_coin_count(FIVE)}"
        return s     